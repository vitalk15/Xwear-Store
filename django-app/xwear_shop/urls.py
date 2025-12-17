from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static  # работает только в debug-режиме

# from django.views.static import serve  # для медиафайлов в prod-режиме


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
]

# маршруты медиа-файлов (для debug-режима)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# маршруты медиа-файлов (для prod-режима)
# if not settings.DEBUG:
#     urlpatterns.append(
#         path("media/<path:path>", serve, {"document_root": settings.MEDIA_ROOT})
#     )
