# БАННЕРЫ, ИЗБРАННОЕ И ПРОЧЕЕ

from django.contrib import admin
from adminsortable2.admin import SortableAdminMixin
from django_jsonform.widgets import JSONFormWidget
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
    list_display = ("image_preview_small", "display_title", "is_active")
    list_editable = ("is_active",)
    list_display_links = ("display_title",)
    fieldsets = (
        (
            "Изображение слайда",
            {
                "fields": (("image", "image_preview_small"), "title"),
            },
        ),
        (
            "Ссылки",
            {
                "fields": ("links",),
            },
        ),
        (
            "Настройки отображения",
            {
                "fields": ("is_active",),
                "classes": ("collapse",),
            },
        ),
    )
    readonly_fields = ("image_preview_small",)

    @admin.display(description="Заголовок")
    def display_title(self, obj):
        return obj.title or "— Без заголовка —"

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "links":
            # Подключаем виджет и передаем ему схему
            kwargs["widget"] = JSONFormWidget(schema=SliderBanner.LINKS_SCHEMA)

        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == "image":
            # Прокидываем лимиты ImageValidator в админку (в data-атрибуты поля)
            add_validator_attrs_to_widget(db_field, formfield)

        return formfield

    class Media:
        js = ("admin/js/image_preview.js",)
