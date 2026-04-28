# МИКСИНЫ И ОБЩИЕ НАСТРОЙКИ

from django.contrib import admin
from ..utils import get_admin_thumb


class ImagePreviewMixin:
    """Миксин для добавления превью изображений в списки и карточки."""

    @admin.display(description="Превью")
    def image_preview(self, obj):
        return get_admin_thumb(obj.image)

    @admin.display(description="Текущее изображение")
    def image_preview_large(self, obj):
        return get_admin_thumb(obj.image, alias="slider_large", show_info=True)


class MainPreviewMixin:
    """Миксин для добавления превью главного изображения в списки и карточки."""

    @admin.display(description="Главное фото")
    def get_main_preview(self, obj):
        main_img = obj.get_main_image_obj
        if main_img:
            return get_admin_thumb(main_img.image)
        return "-"
