from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from core.serializers import CitySerializer
from core.models import City
from .models import Profile, Address

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, validators=[validate_password], style={"input_type": "password"}
    )
    password_confirm = serializers.CharField(
        write_only=True, style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = ("id", "email", "password", "password_confirm")

    def validate_email(self, value):
        return value.strip().lower()

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Пароли не совпадают"})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        return User.objects.create_user(**validated_data)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(write_only=True, required=True)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Старый пароль неверный")
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError("Пароли не совпадают")
        return attrs

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        # instance — это request.user
        instance.set_password(validated_data["new_password"])
        instance.increment_token_version()  # инвалидация старых токенов (вместо blacklist)
        # Метод модели increment_token_version сам делает save(update_fields),
        # но так как мы еще меняли пароль, вызываем полный save()
        instance.save()
        return instance


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        uid = self.context.get("uid")
        token = self.context.get("token")

        if not uid or not token:
            raise serializers.ValidationError("Неверный uid или token")

        # Валидация uid
        try:
            decoded_uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=decoded_uid)
        except (TypeError, ValueError, User.DoesNotExist) as exc:
            raise serializers.ValidationError("Неверная ссылка") from exc

        # Валидация токена
        if not default_token_generator.check_token(user, token):
            raise serializers.ValidationError("Неверный или истёкший токен")

        # Сохраняем user для view
        self.instance = user

        # Валидация паролей
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError("Пароли не совпадают")

        return attrs

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        instance.set_password(validated_data["new_password"])
        instance.increment_token_version()  # Инвалидация всех JWT
        # Метод модели increment_token_version сам делает save(update_fields),
        # но так как мы еще меняли пароль, вызываем полный save()
        instance.save()
        return instance


# кастомный сериализатор, добавляем в payload токена кроме user_id, exp, iat ещё token_version при login
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["user_id"] = user.id
        token["token_version"] = user.token_version  # Добавляем в payload
        return token

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class AddressSerializer(serializers.ModelSerializer):
    # При чтении (GET) мы хотим видеть объект города целиком
    city = CitySerializer(read_only=True)
    # Это поле позволит нам отправлять ID города при создании (POST)
    # Мы привязываем его к полю модели 'city' через аргумент source
    city_id = serializers.PrimaryKeyRelatedField(
        queryset=City.objects.all(), source="city", write_only=True
    )
    address_simple = serializers.ReadOnlyField()

    class Meta:
        model = Address
        fields = (
            "id",
            "city",  # Для отображения
            "city_id",  # Для записи
            "street",  # Поля для форм редактирования
            "house",
            "apartment",
            "is_default",
            "address_simple",  # Готовая строка для истории заказов или чеков
        )


class ProfileSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True, read_only=True)

    class Meta:
        model = Profile
        fields = ("first_name", "last_name", "phone", "addresses")

    def validate_phone(self, value):
        if value:
            return value.strip()
        return value


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ("id", "email", "date_joined", "profile")
        read_only_fields = ("id", "email", "date_joined")

    def update(self, instance, validated_data):
        """
        Переопределяем метод update, чтобы при PATCH запросе на /user/
        обновлялись данные внутри вложенного профиля.
        """
        # Извлекаем данные профиля из запроса, если они есть
        profile_data = validated_data.pop("profile", None)

        # Обновляем поля самого User (если вдруг решим разрешить менять что-то кроме пароля/email)
        super().update(instance, validated_data)

        # Если пришли данные для профиля, обновляем их
        if profile_data:
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return instance
