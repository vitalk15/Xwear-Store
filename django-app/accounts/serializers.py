from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "email", "password", "password_confirm")

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError("Пароли не совпадают")
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        user = User.objects.create_user(
            email=validated_data["email"], password=validated_data["password"]
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "phone", "date_joined")
        read_only_fields = (
            "id",
            "email",
            "date_joined",
        )


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
