from django.contrib import admin
from .models import User, Profile, Address, City


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active", "delivery_cost"]
    list_editable = ["is_active", "delivery_cost"]
    search_fields = ["name"]


class AddressInline(admin.TabularInline):
    model = Address
    extra = 0
    fields = ["city", "street", "house", "apartment", "is_default", "created_at"]
    readonly_fields = ["created_at"]


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    inlines = [AddressInline]

    list_display = ["user", "phone", "first_name", "last_name"]
    search_fields = ["user__email", "phone"]


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False  # Нельзя удалить профиль отдельно от юзера
    fields = (("first_name", "last_name"), "phone")


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
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
    # порядок отображения полей пользователя
    fields = (
        ("email", "is_active"),
        ("is_staff", "is_superuser"),
        "groups",
        "user_permissions",
        ("last_login", "date_joined"),
    )

    # делаем доступными только для чтения поля даты регистрации пользователя и последнего его входа на сайт.
    readonly_fields = ["last_login", "date_joined"]

    @admin.display(description="Телефон")
    def get_phone(self, obj):
        return obj.profile.phone if hasattr(obj, "profile") else "-"
