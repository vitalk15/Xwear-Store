from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from rest_framework.pagination import LimitOffsetPagination
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.conf import settings
from xwear.models import Category, Product, ProductImage, ProductSize
from .serializers import (
    RegisterSerializer,
    ChangePasswordSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer,
    CategorySerializer,
    ProductListSerializer,
    ProductDetailSerializer,
)

User = get_user_model()


# регистрация пользователя с автоматической авторизацией (с выдачей токенов)
@api_view(["POST"])
@permission_classes([AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)  # используется TOKEN_OBTAIN_SERIALIZER!
        return Response(
            {
                "user": {
                    "id": user.id,
                    "email": user.email,
                },
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# смена пароля авторизованным пользователем с аннулированием старых токенов и выдачей новых
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        user = request.user
        user.set_password(serializer.validated_data["new_password"])
        user.increment_token_version()  # инвалидация старых токенов (вместо blacklist)
        user.save()

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "message": "Пароль успешно изменён",
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
                # "user": {
                #     "id": user.id,
                #     "email": user.email,
                # },
            },
            status=status.HTTP_200_OK,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# запрос ссылки для сброса пароля на email
@api_view(["POST"])
@permission_classes([AllowAny])
def password_reset_request_view(request):
    serializer = PasswordResetSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data["email"]
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = f"{settings.RESET_URL}/reset-password/{uid}/{token}/"

            send_mail(
                "Сброс пароля",
                f"Перейдите по ссылке (действительна {settings.PASSWORD_RESET_TIMEOUT//3600} час(а)): {reset_url}",
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
        except User.DoesNotExist:
            pass

        return Response({"message": f"Ссылка отправлена на email: {email}"})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# подтверждение сброса пароля через email
@api_view(["POST"])
@permission_classes([AllowAny])
def password_reset_confirm_view(request, uid, token):
    serializer = PasswordResetConfirmSerializer(data=request.data)
    serializer.context["uid"] = uid
    serializer.context["token"] = token

    if serializer.is_valid():
        user = serializer.user
        user.set_password(serializer.validated_data["new_password"])
        user.increment_token_version()  # Инвалидация старых JWT
        user.save()

        return Response({"message": "Пароль сброшен успешно"})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# выход пользователя с аннулированием старых токенов
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    user = request.user
    user.increment_token_version()  # инвалидация старых токенов (вместо blacklist)
    user.save()

    return Response(
        {"message": "Выход выполнен."},
        status=status.HTTP_205_RESET_CONTENT,
    )


# дерево категорий
@api_view(["GET"])
def category_tree_view(request):
    # c корневой mptt-категорией
    # root_categories = Category.objects.filter(level=0, is_active=True)
    # serializer = CategorySerializer(
    #     root_categories, many=True, context={"request": request}
    # )

    # без корневой mptt-категории
    categories = Category.objects.filter(level=1, is_active=True)
    serializer = CategorySerializer(categories, many=True, context={"request": request})
    return Response(serializer.data)


# товары категории
@api_view(["GET"])
def category_detail_view(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug, is_active=True)
    products_queryset = (
        category.products.filter(is_active=True)
        .prefetch_related(
            Prefetch(
                "images",
                queryset=ProductImage.objects.filter(is_main=True),
                to_attr="main_image_preview",  # Сохраняем в отдельный атрибут для скорости
            )
        )
        .order_by("-created_at")
    )

    # Пагинация из settings.py
    paginator = LimitOffsetPagination()
    page = paginator.paginate_queryset(products_queryset, request)

    serializer = ProductListSerializer(page, many=True, context={"request": request})

    return paginator.get_paginated_response(
        {
            "category": {
                "id": category.id,
                "name": category.name,
                "slug": category.slug,
            },
            "products": serializer.data,
        }
    )


# Детали товара
@api_view(["GET"])
def product_detail_view(request, category_slug, product_slug):
    product = get_object_or_404(
        Product.objects.filter(
            is_active=True, category__slug=category_slug, slug=product_slug
        ).prefetch_related(
            Prefetch("images", queryset=ProductImage.objects.order_by("-is_main")),
            Prefetch(
                "sizes",
                queryset=ProductSize.objects.filter(is_active=True).select_related(
                    "size"
                ),
            ),
        )
    )

    serializer = ProductDetailSerializer(product, context={"request": request})
    return Response(serializer.data, status=status.HTTP_200_OK)
