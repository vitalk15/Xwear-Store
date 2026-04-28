# ВСПОМОГАТЕЛЬНЫЕ СПРАВОЧНИКИ - КАТЕГОРИИ, БРЕНДЫ, РАЗМЕРЫ, ЦВЕТА, МАТЕРИАЛЫ И ДР.

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from django_mptt_admin.admin import DjangoMpttAdmin
from adminsortable2.admin import SortableAdminMixin
from ..forms import ColorAdminForm
from ..models import Category, Brand, Color, Size, Material


@admin.register(Category)
class CategoryAdmin(DjangoMpttAdmin):
    # атр. prepopulated_fields - автогенерация slug по name (показ подсказки в админке)
    prepopulated_fields = {"slug": ("name",)}
    list_display = ["name", "slug", "level", "is_active"]
    list_display_links = ["name"]
    list_filter = ["is_active", "level"]
    list_editable = ["is_active"]
    search_fields = ["name"]

    # Это ускорит работу __str__, так как родители будут в памяти
    def get_queryset(self, request):
        return super().get_queryset(request).select_related("parent")


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "view_products_link_list"]
    readonly_fields = ["view_products_link_detail"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]

    fieldsets = (
        (
            None,
            {
                "fields": (("name", "slug"), "view_products_link_detail"),
            },
        ),
    )

    # @admin.display(description="Кол-во товаров", ordering="products_count")
    # def get_products_count(self, obj):
    #     # Берем значение из аннотации
    #     return obj.products_count

    # Ссылка для общего СПИСКА брендов (компактная)
    @admin.display(description="Товары")
    def view_products_link_list(self, obj):
        if obj.pk:
            # Динамически получаем имя приложения и имя связанной модели (Product через related_name)
            target_model = obj.products.model
            app_label = target_model._meta.app_label
            model_name = target_model._meta.model_name

            url = (
                reverse(f"admin:{app_label}_{model_name}_changelist")
                + f"?brand__id__exact={obj.pk}"
            )
            return format_html('<a href="{}">Перейти ({})</a>', url, obj.products_count)
        return "-"

    # 3. Кнопка для СТРАНИЦЫ редактирования бренда
    @admin.display(description="Управление ассортиментом")
    def view_products_link_detail(self, obj):
        if obj.pk:
            # Динамически получаем имя приложения и имя связанной модели (Product через related_name)
            target_model = obj.products.model
            app_label = target_model._meta.app_label
            model_name = target_model._meta.model_name

            url = (
                reverse(f"admin:{app_label}_{model_name}_changelist")
                + f"?brand__id__exact={obj.pk}"
            )
            return format_html(
                '<a href="{}" class="button" style="background-color: #79aec8; color: white; padding: 10px 15px; text-decoration: none; border-radius: 4px;">'
                'Посмотреть все товары бренда "{}" ({})'
                "</a>",
                url,
                obj.name,
                obj.products_count,
            )
        return "Сначала сохраните бренд"

    def get_queryset(self, request):
        # Используем аннотацию
        return super().get_queryset(request).annotate(products_count=Count("products"))


@admin.register(Color)
class ColorAdmin(SortableAdminMixin, admin.ModelAdmin):
    form = ColorAdminForm
    list_display = ["name", "color_preview", "slug", "hex_code", "hex_code_2"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}

    @admin.display(description="Цвет")
    def color_preview(self, obj):
        # Базовые стили для кружочка
        style = "width: 24px; height: 24px; border-radius: 50%; border: 1px solid #ccc;"

        # 1. Приоритет отдаем текстуре (картинке)
        if obj.texture:
            style += f"background-image: url({obj.texture.url}); background-size: cover; background-position: center;"
        # 2. Если есть второй цвет — делаем диагональный градиент
        elif obj.hex_code_2:
            style += f"background: linear-gradient(135deg, {obj.hex_code} 51%, {obj.hex_code_2} 49%);"
        # 3. Обычный однотонный цвет
        elif obj.hex_code:
            style += f"background-color: {obj.hex_code};"

        return format_html('<div title="{}" style="{}"></div>', obj.name, style)


@admin.register(Size)
class SizeAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ["name"]
    list_display_links = ["name"]
    search_fields = ["name"]

    def get_search_results(self, request, queryset, search_term):
        # Вызываем стандартный поиск
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term
        )

        # Если это запрос от нашего фильтра в админке
        if "autocomplete" in request.path:
            # Ограничиваем выдачу только теми размерами, которые есть в ProductSize
            queryset = queryset.filter(productsize__isnull=False).distinct()

        return queryset, use_distinct


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ("name", "material_type")
    list_filter = ("material_type",)

    # Поиск по названию (обязательно для работы autocomplete_fields)
    search_fields = ("name",)

    ordering = ("material_type", "name")
