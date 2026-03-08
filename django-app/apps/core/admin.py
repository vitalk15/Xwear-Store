from django.contrib import admin
from .models import City, Document, ContactSettings, CommercialConfig


# --------- МИКСИНЫ ПРАВ ДОСТУПА В АДМИНКЕ ------------


class SingletonAdminMixin:
    """Запрещаем добавлять новые записи, если одна уже есть"""

    def has_add_permission(self, request):
        return not self.model.objects.exists()


class ReadOnlyAdminMixin:
    """Миксин для создания интерфейса 'только просмотр'"""

    # Запрещаем добавление записи
    def has_add_permission(self, request):
        return False

    # Запрещаем удаление записи
    def has_delete_permission(self, request, obj=None):
        return False

    # Запрещаем правку записи. Это уберет кнопку "Сохранить" и "Сохранить и продолжить"
    def has_change_permission(self, request, obj=None):
        return False

    # Разрешаем просмотр записи
    def has_view_permission(self, request, obj=None):
        return True


class NoDeleteAddMixin:
    """Миксин запрещающий удаление и добавление, но разрешающий правку"""

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# --------------------------------------------------------


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active", "delivery_cost"]
    list_editable = ["is_active", "delivery_cost"]
    search_fields = ["name"]


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at")


@admin.register(ContactSettings)
class ContactSettingsAdmin(SingletonAdminMixin, admin.ModelAdmin):
    fieldsets = (
        (
            "Основная связь",
            {"fields": ("phone", "email")},
        ),
        (
            "Мессенджеры и соцсети",
            {"fields": ("tg_url", "vb_url", "vk_url", "ok_url", "ig_url")},
        ),
        (
            "График работы",
            {"fields": ("schedule_days", "schedule_time", "schedule_extra")},
        ),
    )


@admin.register(CommercialConfig)
class CommercialConfigAdmin(SingletonAdminMixin, admin.ModelAdmin):
    fieldsets = (
        (
            "Бесплатная доставка",
            {"fields": ("is_free_delivery_active", "free_delivery_threshold")},
        ),
        (
            "Текстовая информация",
            {"fields": ("delivery_info", "payment_info")},
        ),
    )
