from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from core.admin import NoDeleteAddMixin
from .models import User, Profile, Address


class AddressInline(admin.TabularInline):
    model = Address
    extra = 0
    fields = ["city", "street", "house", "apartment", "is_default", "created_at"]
    readonly_fields = ["created_at"]


@admin.register(Profile)
class ProfileAdmin(NoDeleteAddMixin, admin.ModelAdmin):
    inlines = [AddressInline]

    list_display = ["user", "phone", "first_name", "last_name"]
    search_fields = ["user__email", "phone"]
    readonly_fields = ("user",)


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False  # Нельзя удалить профиль отдельно от юзера
    fields = (("first_name", "last_name"), "phone")

    verbose_name = "Персональные данные"
    verbose_name_plural = "Персональные данные"

    class Media:
        # Прячем заголовок h3 внутри инлайна (появляется при StackedInline)
        css = {"all": ("admin/css/hide_inline_header.css",)}


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [ProfileInline]

    # строковое отображение записи в виде: email, время регистрации
    list_display = ["email", "get_phone", "is_active", "date_joined", "last_login"]
    # фильтрация
    list_filter = ["is_active", "is_staff", "is_superuser"]
    # поля для перехода в "карточку" записи
    list_display_links = ["email"]
    # редактирование поля в строковом отображении
    list_editable = ["is_active"]
    # поиск по именам, адресам эл.почты, настоящим именам и фамилиям
    search_fields = [
        "email",
        "profile__phone",
        "profile__first_name",
        "profile__last_name",
    ]

    fieldsets = (
        (
            None,
            {"fields": ("email", "password")},
        ),
        (
            "Права доступа",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Даты",
            {"fields": ("last_login", "date_joined")},
        ),
    )

    readonly_fields = ["last_login", "date_joined"]
    list_select_related = ["profile"]  # Оптимизация
    ordering = ("email",)  # BaseUserAdmin требует сортировку

    @admin.display(description="Телефон")
    def get_phone(self, obj):
        return obj.profile.phone if hasattr(obj, "profile") else "-"

    # Запрещаем удалять пользователей, мы их деактивируем (is_active=False)
    # def has_delete_permission(self, request, obj=None):
    #     return False
