import time
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.conf import settings
from django.urls import reverse

# время жизни refresh-токена
refresh_lifetime = settings.SIMPLE_JWT.get("REFRESH_TOKEN_LIFETIME")


# Установка Refresh-токена в куку.
def set_refresh_cookie(response, refresh_token):
    response.set_cookie(
        key="refresh_token",
        value=str(refresh_token),
        httponly=settings.COOKIE_HTTP_ONLY,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=int(refresh_lifetime.total_seconds()),
        path=reverse("token_refresh"),  # Кука летит ТОЛЬКО на '/api/auth/token/refresh/'
    )
    return response


# Кастомный генератор токенов (используем для активации юзера при подтверждении его почты)
class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def check_token(self, user, token):
        """
        Переопределяем проверку, чтобы использовать ACCOUNT_ACTIVATION_TIMEOUT
        вместо PASSWORD_RESET_TIMEOUT.
        """
        if not (user and token):
            return False

        # Стандартная проверка структуры токена и хеша
        if not super().check_token(user, token):
            return False

        # Проверка времени (логика взята из исходников Django,
        # но с нашей константой)
        try:
            ts_b36 = token.split("-")[0]
            from django.utils.http import base36_to_int

            timestamp = base36_to_int(ts_b36)
        except (ValueError, IndexError):
            return False

        # Проверяем, не истекло ли время
        if (
            self._num_seconds(self._now()) - timestamp
        ) > settings.ACCOUNT_ACTIVATION_TIMEOUT:
            return False

        return True


# Создаем экземпляр
account_activation_token_generator = AccountActivationTokenGenerator()
