from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static  # работает только в debug-режиме

# from django.views.static import serve  # для медиафайлов в prod-режиме
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/core/", include("core.urls")),
    path("api/auth/", include("accounts.urls")),
    path("api/shop/", include("xwear.urls")),
    path("api/orders/", include("orders.urls")),
    # ---------------
    # Spectacular UI
    # ---------------
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"
    ),
]

# маршруты медиа-файлов (для debug-режима)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# маршруты медиа-файлов (для prod-режима)
# if not settings.DEBUG:
#     urlpatterns.append(
#         path("media/<path:path>", serve, {"document_root": settings.MEDIA_ROOT})
#     )
