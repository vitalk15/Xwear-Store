# МИКСИНЫ И ОБЩИЕ НАСТРОЙКИ

from django.contrib import admin
from easy_thumbnails.files import get_thumbnailer
from ..utils import get_admin_thumb, generate_banner_html


class ImagePreviewMixin:
    """Миксин для добавления превью изображений в списки и карточки."""

    @admin.display(description="Превью")
    def image_preview(self, obj):
        return get_admin_thumb(obj.image)

    # @admin.display(description="Текущее изображение")
    # def image_preview_small(self, obj):
    #     return get_admin_thumb(obj.image, alias="slider_small", show_info=True)


class MainPreviewMixin:
    """Миксин для добавления превью главного изображения в списки и карточки."""

    @admin.display(description="Главное фото")
    def get_main_preview(self, obj):
        main_img = obj.get_main_image_obj
        if main_img:
            return get_admin_thumb(main_img.image)
        return "-"


class BannerPreviewMixin:
    """Миксин для добавления превью баннера."""

    @admin.display(description="Превью")
    def banner_preview(self, obj):
        """Большое превью для формы редактирования"""
        if not obj.image:
            return generate_banner_html(obj, None, "1000px")

        thumbnailer = get_thumbnailer(obj.image)
        thumb_url = thumbnailer["slider_medium"].url

        return generate_banner_html(obj, thumb_url, max_width="1000px", is_list=False)

    @admin.display(description="Превью")
    def banner_preview_small(self, obj):
        """Маленькое превью для списка (Changelist)"""
        if not obj.image:
            return generate_banner_html(obj, None, "280px")

        thumbnailer = get_thumbnailer(obj.image)
        thumb_url = thumbnailer["slider_small"].url

        return generate_banner_html(obj, thumb_url, max_width="280px", is_list=True)
