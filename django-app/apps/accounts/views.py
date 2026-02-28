from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction
from django.db.models import Prefetch
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.conf import settings
from .models import Address
from .serializers import (
    RegisterSerializer,
    ChangePasswordSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer,
    UserSerializer,
    AddressSerializer,
)
from .utils import (
    set_refresh_cookie,
    account_activation_token_generator,
    send_password_reset_email,
    send_password_changed_notification,
)

User = get_user_model()


# Кастомная simplejwt-вьюха для логина
# переопределяем так как нужно установить Refresh-токен в HttpOnly куку
class CustomTokenObtainView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            refresh_token = response.data.get("refresh")
            # Устанавливаем куку
            set_refresh_cookie(response, refresh_token)
            # Удаляем refresh из JSON-ответа
            del response.data["refresh"]
        return response


# Кастомная simplejwt-вьюха обновления access-токена
# переопределяем так как Refresh-токен установлен в HttpOnly куку, фронтенд не сможет достать его и отправить в теле запроса.
class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        # Достаем токен из куки, если его нет в body
        refresh_token = request.COOKIES.get("refresh_token")
        if refresh_token:
            request.data["refresh"] = refresh_token

        response = super().post(request, *args, **kwargs)

        # Если включена ротация (ROTATE_REFRESH_TOKENS: True)
        if response.status_code == 200 and "refresh" in response.data:
            set_refresh_cookie(response, response.data["refresh"])
            del response.data["refresh"]

        return response


# регистрация пользователя с автоматической авторизацией (с выдачей токенов)
# @api_view(["POST"])
# @permission_classes([AllowAny])
# def register_view(request):
#     serializer = RegisterSerializer(data=request.data)
#     if serializer.is_valid():
#         try:
#             # Оборачиваем в транзакцию: создастся либо всё (User+Profile+Cart), либо ничего
#             # Profile создаётся через сигнал при создании User (также Cart)
#             with transaction.atomic():
#                 user = serializer.save()
#             # Генерируем новую пару токенов и добавляем token_version
#             refresh = RefreshToken.for_user(user)  # используется TOKEN_OBTAIN_SERIALIZER!
#             refresh["token_version"] = user.token_version

#             response = Response(
#                 {
#                     "message": "Регистрация нового пользователя прошла успешно. Авторизация выполнена.",
#                     "user": {
#                         "id": user.id,
#                         "email": user.email,
#                     },
#                     "access": str(refresh.access_token),
#                 },
#                 status=status.HTTP_201_CREATED,
#             )
#             return set_refresh_cookie(response, refresh)
#         except Exception:
#             return Response(
#                 {"detail": "Ошибка при создании профиля"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# регистрация пользователя c подтверждением почты
@api_view(["POST"])
@permission_classes([AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        # Создаем пользователя. Флаг is_active=False должен стоять в сериализаторе
        # или здесь принудительно.
        user = serializer.save(is_active=False)

        # Сигнал отправит письмо
        return Response(
            {
                "message": "Регистрация прошла успешно. Пожалуйста, проверьте почту для активации аккаунта.",
                "email": user.email,
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# активация и одновременная авторизация пользователя (с выдачей токенов) после подтверждения почты
@api_view(["POST"])
@permission_classes([AllowAny])
def activate_view(request):
    uid_b64 = request.data.get("uid")
    token = request.data.get("token")

    if not uid_b64 or not token:
        return Response(
            {"error": "Неполные данные для активации"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Декодируем ID пользователя
        uid = force_str(urlsafe_base64_decode(uid_b64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token_generator.check_token(user, token):
        if not user.is_active:
            # Оборачиваем в транзакцию: либо активируется юзер и автоматически создаются для него Profile и Cart, либо ничего не меняется
            with transaction.atomic():
                user.is_active = True
                user.save()
                # В этот момент сработали сигналы: создались Profile и Cart

        # Сразу авторизуем пользователя (генерируем новую пару токенов и добавляем token_version)
        refresh = RefreshToken.for_user(user)  # используется TOKEN_OBTAIN_SERIALIZER!
        refresh["token_version"] = user.token_version

        response = Response(
            {
                "message": "Аккаунт успешно активирован и выполнен вход.",
                "user": {
                    "id": user.id,
                    "email": user.email,
                },
                "access": str(refresh.access_token),
            },
            status=status.HTTP_200_OK,
        )

        return set_refresh_cookie(response, refresh)

    return Response(
        {"error": "Ссылка активации недействительна или просрочена"},
        status=status.HTTP_400_BAD_REQUEST,
    )


# смена пароля авторизованным пользователем с аннулированием старых токенов и выдачей новых
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    serializer = ChangePasswordSerializer(
        instance=request.user, data=request.data, context={"request": request}
    )
    if serializer.is_valid():
        # Метод save() вызовет update() в сериализаторе, где пароль сменится
        # и версия токена увеличится.
        user = serializer.save()

        # Отправляем уведомление на email
        send_password_changed_notification(user)

        # Генерируем новую пару токенов и добавляем token_version
        refresh = RefreshToken.for_user(user)  # используется TOKEN_OBTAIN_SERIALIZER!
        refresh["token_version"] = user.token_version

        response = Response(
            {
                "message": "Пароль успешно изменён. Старые сессии аннулированы.",
                "access": str(refresh.access_token),
            },
            status=status.HTTP_200_OK,
        )
        return set_refresh_cookie(response, refresh)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# запрос ссылки для сброса пароля на email
@api_view(["POST"])
@permission_classes([AllowAny])
def password_reset_request_view(request):
    serializer = PasswordResetSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data["email"]
        user = User.objects.filter(email=email).first()

        if user:
            try:
                # генерируем ссылку для сброса пароля и отправляем письмо
                send_password_reset_email(user)
            except Exception:
                return Response(
                    {"error": "Ошибка отправки email. Попробуйте позже."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        # Всегда возвращаем успех, чтобы не выдавать наличие email в базе
        return Response(
            {"message": f"Инструкции для сброса пароля отправлены на email: {email}."},
            status=status.HTTP_200_OK,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# подтверждение сброса пароля через email
@api_view(["POST"])
@permission_classes([AllowAny])
def password_reset_confirm_view(request, uid, token):
    serializer = PasswordResetConfirmSerializer(
        data=request.data, context={"uid": uid, "token": token}
    )

    if serializer.is_valid():
        # Внутри save() происходит user.set_password() и user.save()
        serializer.save()

        response = Response(
            {
                "message": "Пароль успешно сброшен. Все активные сессии завершены. Войдите с новым паролем"
            },
            status=status.HTTP_200_OK,
        )

        try:
            refresh_path = reverse("token_refresh")
            response.delete_cookie(
                "refresh_token",
                path=refresh_path,
                samesite=settings.COOKIE_SAMESITE,
            )
        except Exception:
            # Если reverse не сработал (редкость), не ломаем ответ пользователю
            pass

        return response

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# выход пользователя с аннулированием старых токенов и удалением куки
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    user = request.user
    user.increment_token_version()  # инвалидация старых токенов (вместо blacklist)
    user.save()

    response = Response(
        {"message": "Выход успешно выполнен со всех устройств."},
        status=status.HTTP_200_OK,
    )

    response.delete_cookie(
        "refresh_token",
        path=reverse("token_refresh"),
        samesite=settings.COOKIE_SAMESITE,
    )

    return response


# Просмотр и редактирование данных текущего пользователя
@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def user_profile_view(request):
    user = (
        User.objects.select_related("profile")
        .prefetch_related(
            Prefetch(
                "profile__addresses", queryset=Address.objects.select_related("city")
            )
        )
        .get(id=request.user.id)
    )

    if request.method == "GET":
        serializer = UserSerializer(user)
        return Response(serializer.data)

    if request.method == "PATCH":
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# создание и получение списка адресов пользователя
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def address_list_create_view(request):
    user_profile = request.user.profile

    if request.method == "GET":
        addresses = user_profile.addresses.select_related("city").all()
        serializer = AddressSerializer(addresses, many=True)
        return Response(serializer.data)

    if request.method == "POST":
        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            # При сохранении передаем профиль вручную, так как его нет в данных формы
            serializer.save(profile=user_profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# редактирование и удаление адреса пользователя
@api_view(["PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def address_detail_view(request, pk):
    try:
        # Важно: ищем адрес только среди адресов текущего пользователя!
        address = request.user.profile.addresses.select_related("city").get(pk=pk)
    except Address.DoesNotExist:
        return Response({"detail": "Адрес не найден"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "PATCH":
        serializer = AddressSerializer(address, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        address.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
