from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    # TokenBlacklistView,  #  для Blacklist
)
from .views import (
    register_view,
    change_password_view,
    password_reset_request_view,
    password_reset_confirm_view,
    logout_view,
)


urlpatterns = [
    # получить пару jwt-токенов при login
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    # обновить access-token
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # path("token/blacklist/", TokenBlacklistView.as_view(), name="token_blacklist"),  # для Blacklist
    path("register/", register_view, name="register"),
    path("change-password/", change_password_view, name="change_password"),
    path("password-reset/", password_reset_request_view, name="password_reset"),
    path(
        "password-reset/<uid>/<token>/",
        password_reset_confirm_view,
        name="password_reset_confirm",
    ),
    path("logout/", logout_view, name="logout"),
]
