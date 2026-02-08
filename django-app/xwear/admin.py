from django import forms
from django.contrib import admin, messages
from django.utils.html import format_html
from django.urls import reverse
from django_mptt_admin.admin import DjangoMpttAdmin
from .models import (
    Category,
    Brand,
    Product,
    ProductImage,
    Size,
    ProductSize,
    ProductSpecification,
    Favorite,
    SliderBanner,
)
from .utils import get_admin_thumb


@admin.register(Category)
class CategoryAdmin(DjangoMpttAdmin):
    # атр. prepopulated_fields - автогенерация slug по name (показ подсказки в админке)
    prepopulated_fields = {"slug": ("name",)}
    list_display = ["name", "slug", "level", "is_active"]
    list_display_links = ["name"]
    list_filter = ["is_active", "level"]
    list_editable = ["is_active"]
    search_fields = ["name"]


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # 1 пустая строка для изображения
    fields = ["image", "is_main", "alt", "image_preview"]
    readonly_fields = ["image_preview"]

    def image_preview(self, obj):
        return get_admin_thumb(obj.image)

    image_preview.short_description = "Превью"


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ["name", "order"]
    list_display_links = ["name"]
    search_fields = ["name"]
    list_editable = ["order"]
    fields = (("name", "order"),)


class SizeFilter(admin.SimpleListFilter):
    title = "Размер"
    parameter_name = "size"

    def lookups(self, request, model_admin):
        sizes = Size.objects.all()
        return [(s.id, s.name) for s in sizes]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(sizes__id=self.value())
        return queryset


class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 3  # 3 пустых размера
    fields = ["size", "price", "discount_percent", "get_final_price", "is_active"]
    # Это делает выбор размера быстрым поиском (требует search_fields в SizeAdmin)
    autocomplete_fields = ["size"]
    readonly_fields = ["get_final_price"]

    @admin.display(description="Итоговая цена")
    def get_final_price(self, obj):
        # Проверка obj.pk нужна, чтобы не считать цену для пустых (extra) строк до их сохранения
        if obj.pk and obj.price:
            return f"{obj.final_price} ₽"
        return "-"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("size")


class DiscountFilter(admin.SimpleListFilter):
    title = "Наличие скидки"
    parameter_name = "has_discount"

    def lookups(self, request, model_admin):
        return (
            ("yes", "Со скидкой"),
            ("no", "Без скидки"),
        )

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(sizes__discount_percent__gt=0).distinct()
        if self.value() == "no":
            return queryset.filter(sizes__discount_percent=0).distinct()


class SpecificationInline(admin.StackedInline):
    model = ProductSpecification
    can_delete = False
    verbose_name = "Характеристики"
    # Ограничиваем количество, так как это OneToOne
    max_num = 1


class ProductAdminForm(forms.ModelForm):
    # Добавляем виртуальное поле, которого нет в модели
    set_discount_all_sizes = forms.IntegerField(
        label="Установить скидку (%) на все размеры",
        required=False,
        min_value=0,
        max_value=100,
        help_text="Введите число, чтобы массово обновить скидку. Оставьте пустым, если не нужно менять.",
    )

    class Meta:
        model = Product
        fields = "__all__"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    inlines = [ProductImageInline, ProductSizeInline, SpecificationInline]

    list_display = [
        "name",
        "brand",
        "category",
        "gender",
        "active_sizes_count",
        "get_price_range",
        "image_main",
        "is_active",
    ]
    list_display_links = ["name", "image_main"]
    list_filter = ["is_active", "gender", "brand", "category", SizeFilter, DiscountFilter]
    search_fields = ["name"]

    # Если категорий и брендов будет много (заменяет выбор из выпадающего списка на удобный поиск)
    # search_fields = ["name", "brand__name", "category__name"]
    # autocomplete_fields = ["brand", "category"]

    # Редактирование в списке
    list_editable = ["is_active"]

    # Форма редактирования
    fields = [
        "name",
        "slug",
        "brand",
        "category",
        "description",
        "gender",
        "set_discount_all_sizes",
        "is_active",
    ]

    # Автозаполнение slug
    prepopulated_fields = {"slug": ("name",)}

    @admin.display(description="Пол")
    def gender_display(self, obj):
        return obj.get_gender_display()

    # gender_display.short_description = "Пол"

    @admin.display(description="Главное фото")
    def image_main(self, obj):
        main_img = obj.get_main_image_obj
        if main_img:
            return get_admin_thumb(main_img.image, size=(80, 80))
        return "-"
        # return None

    @admin.display(description="Доступно размеров")
    def active_sizes_count(self, obj):
        # Считаем в памяти Python из уже загруженного prefetch_related
        return len([s for s in obj.sizes.all() if s.is_active])

    @admin.display(description="Диапазон цен")
    def get_price_range(self, obj):
        # Разброс цен для справки
        prices = [s.final_price for s in obj.sizes.all() if s.is_active]
        if prices:
            return f"{min(prices)} - {max(prices)} ₽"
        return "Цена не задана"

    # Оптимизация запросов
    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("category", "brand")
            .prefetch_related("sizes__size", "images")
        )

    def save_model(self, request, obj, form, change):
        # 1. Сначала сохраняем сам товар
        super().save_model(request, obj, form, change)

        # 2. Проверяем, ввел ли менеджер значение в поле массовой скидки
        discount_value = form.cleaned_data.get("set_discount_all_sizes")

        if discount_value is not None:
            # Обновляем все активные размеры этого товара одним запросом к базе
            obj.sizes.filter(is_active=True).update(discount_percent=discount_value)

            messages.info(
                request, f"Скидка {discount_value}% применена ко всем размерам."
            )


class ProductInline(admin.TabularInline):
    model = Product
    # Указываем только самые важные поля для быстрого обзора
    fields = ["name", "category", "get_edit_link", "is_active"]
    readonly_fields = ["get_edit_link"]
    extra = 0
    show_change_link = True  # Встроенная ссылка на редактирование от Django

    @admin.display(description="Действие")
    def get_edit_link(self, obj):
        if obj.pk:
            # Создаем прямую ссылку на полную страницу редактирования товара
            url = reverse("admin:xwear_product_change", args=[obj.pk])
            return format_html('<a href="{}" class="button">Редактировать</a>', url)
        return "-"


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "get_products_count"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]
    inlines = [ProductInline]

    @admin.display(description="Кол-во товаров")
    def get_products_count(self, obj):
        return obj.products.count()

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("products")


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "created_at")
    list_filter = ("user", "created_at")
    search_fields = ("user__email", "product__name")
    readonly_fields = ("created_at",)


@admin.register(SliderBanner)
class SliderBannerAdmin(admin.ModelAdmin):
    list_display = ("get_preview", "title", "order", "is_active")
    list_editable = ("order", "is_active")
    readonly_fields = ("get_preview_large",)

    @admin.display(description="Превью")
    def get_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 150px; height: auto;" />', obj.image.url
            )
        return "Нет изображения"

    @admin.display(description="Текущее изображение")
    def get_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 600px; height: auto;" />', obj.image.url
            )
        return "Нет изображения"
