from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    # TokenBlacklistView,  #  для Blacklist
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from .views import (
    register_view,
    change_password_view,
    password_reset_request_view,
    password_reset_confirm_view,
    logout_view,
    category_tree_view,
    product_detail_view,
    category_detail_view,
)


urlpatterns = [
    # -----------
    # Simple JWT
    # -----------
    # получить пару jwt-токенов при login
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    # обновить access-token
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # path("token/blacklist/", TokenBlacklistView.as_view(), name="token_blacklist"),  # для Blacklist
    # ---------
    # Main API
    # ---------
    path("register/", register_view, name="register"),
    path("change-password/", change_password_view, name="change_password"),
    path("password-reset/", password_reset_request_view, name="password_reset"),
    path(
        "password-reset/<uid>/<token>/",
        password_reset_confirm_view,
        name="password_reset_confirm",
    ),
    path("logout/", logout_view, name="logout"),
    path("categories/", category_tree_view, name="category_tree"),
    path(
        "categories/<slug:category_slug>/", category_detail_view, name="category_detail"
    ),
    path(
        "categories/<slug:category_slug>/<slug:product_slug>/",
        product_detail_view,
        name="product_detail",
    ),
    # ---------------
    # Spectacular UI
    # ---------------
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
