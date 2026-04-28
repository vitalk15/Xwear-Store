# БАННЕРЫ, ИЗБРАННОЕ И ПРОЧЕЕ

from django.contrib import admin
from adminsortable2.admin import SortableAdminMixin
from core.admin import ReadOnlyAdminMixin
from ..models import SliderBanner, Favorite
from ..utils import add_validator_attrs_to_widget
from .base import ImagePreviewMixin


@admin.register(Favorite)
class FavoriteAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ("user", "variant", "created_at")
    # list_filter = ("user", "product__brand", "created_at")
    search_fields = ("user__email", "variant__full_name", "variant__article")
    readonly_fields = (
        "user",
        "variant",
        "created_at",
    )


@admin.register(SliderBanner)
class SliderBannerAdmin(ImagePreviewMixin, SortableAdminMixin, admin.ModelAdmin):
    list_display = ("image_preview", "title", "link", "is_active")
    list_editable = ("link", "is_active")
    fields = ("image", "image_preview_large", "title", "link", "is_active")
    readonly_fields = ("image_preview_large",)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == "image":
            # Прокидываем лимиты ImageValidator в админку (в data-атрибуты поля)
            add_validator_attrs_to_widget(db_field, formfield)
        return formfield

    class Media:
        js = ("admin/js/image_preview.js",)
