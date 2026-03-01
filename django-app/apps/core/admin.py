from django.contrib import admin
from .models import City, Document, ContactSettings, CommercialConfig


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active", "delivery_cost"]
    list_editable = ["is_active", "delivery_cost"]
    search_fields = ["name"]


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at")


# Базовый класс для синглтонов
class SingletonAdmin(admin.ModelAdmin):
    # Запрещаем добавлять новые записи, если одна уже есть
    def has_add_permission(self, request):
        return not self.model.objects.exists()


@admin.register(ContactSettings)
class ContactSettingsAdmin(SingletonAdmin):
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
class CommercialConfigAdmin(SingletonAdmin):
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
