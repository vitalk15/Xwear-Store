from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed


# Проверка user_id + token_version
class VersionedJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user_id = validated_token.get("user_id")
        token_version = validated_token.get("token_version")

        try:
            user = self.user_model.objects.get(id=user_id, token_version=token_version)
        except self.user_model.DoesNotExist:
            raise AuthenticationFailed(
                "Токен недействителен или сессия устарела.", code="token_not_valid"
            )

        if not user.is_active:
            raise AuthenticationFailed(
                "Пользователь деактивирован.", code="user_inactive"
            )

        return user
