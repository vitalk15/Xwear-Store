from django.urls import path

# from rest_framework_simplejwt.views import (
#     # TokenBlacklistView,  #  для Blacklist
# )
from .views import (
    CustomTokenObtainView,
    CustomTokenRefreshView,
    register_view,
    change_password_view,
    password_reset_request_view,
    password_reset_confirm_view,
    logout_view,
    user_profile_view,
    address_list_create_view,
    address_detail_view,
)


urlpatterns = [
    # получить пару jwt-токенов при login
    path("token/", CustomTokenObtainView.as_view(), name="token_obtain_pair"),
    # обновить access-token
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
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
    path("profile/", user_profile_view, name="user-profile"),
    path("addresses/", address_list_create_view, name="address-list"),
    path("addresses/<int:pk>/", address_detail_view, name="address-detail"),
]
