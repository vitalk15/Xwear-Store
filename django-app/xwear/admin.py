from django.contrib import admin
from django_mptt_admin.admin import DjangoMpttAdmin
from .models import User, Category, Product, ProductImage, Size, ProductSize
from .utils import get_admin_thumb


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # строковое отображение записи в виде: email, время регистрации
    list_display = ("email", "is_active", "date_joined", "last_login")
    # фильтрация
    list_filter = ("is_active", "is_staff", "is_superuser")
    # поля для перехода в "карточку" записи
    list_display_links = ["email"]
    # редактирование поля в строковом отображении
    list_editable = ["is_active"]
    # поиск по именам, адресам эл.почты, настоящим именам и фамилиям
    search_fields = ("email", "phone", "first_name", "last_name")
    # порядок отображения полей пользователя
    fields = (
        ("email", "phone", "is_active"),
        ("first_name", "last_name"),
        ("is_staff", "is_superuser"),
        "groups",
        "user_permissions",
        ("last_login", "date_joined"),
    )

    # делаем доступными только для чтения поля даты регистрации пользователя и последнего его входа на сайт.
    readonly_fields = ("last_login", "date_joined")


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
    extra = 1  # 1 пустая строка
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
    fields = ["size", "price", "is_active"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("size")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline, ProductSizeInline]

    list_display = [
        "name",
        "category",
        "gender",
        "active_sizes_count",
        "image_main",
        "is_active",
    ]
    list_display_links = ["name", "image_main"]
    list_filter = ["is_active", "gender", "category", SizeFilter]
    search_fields = ["name", "description"]

    # Редактирование в списке
    list_editable = ["is_active"]

    # Форма редактирования
    fields = [
        "name",
        "slug",
        "category",
        "description",
        "gender_display",
        "is_active",
    ]
    readonly_fields = ["slug"]

    # Автозаполнение slug
    prepopulated_fields = {"slug": ("name",)}

    def gender_display(self, obj):
        return obj.get_gender_display()

    gender_display.short_description = "Пол"

    def image_main(self, obj):
        # Используем данные из кэша prefetch_related, не обращаясь к БД снова
        all_images = list(obj.images.all())
        main_img = next((img for img in all_images if img.is_main), None) or (
            all_images[0] if all_images else None
        )

        return get_admin_thumb(main_img.image if main_img else None, size=(60, 50))

    image_main.short_description = "Главное фото"

    def active_sizes_count(self, obj):
        # Считаем в памяти Python из уже загруженного prefetch_related
        return len([s for s in obj.sizes.all() if s.is_active])

    active_sizes_count.short_description = "Доступно размеров"

    # Оптимизация запросов
    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("category")
            .prefetch_related("sizes__size", "images")
        )
