from django.conf import settings
from django.urls import reverse


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
