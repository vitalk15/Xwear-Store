from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # строковое отображение записи в виде: email, время регистрации
    list_display = ["email", "is_active", "date_joined", "last_login"]
    # фильтрация
    list_filter = ["is_active", "is_staff", "is_superuser"]
    # поля для перехода в "карточку" записи
    list_display_links = ["email"]
    # редактирование поля в строковом отображении
    list_editable = ["is_active"]
    # поиск по именам, адресам эл.почты, настоящим именам и фамилиям
    search_fields = ["email", "phone", "first_name", "last_name"]
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
    readonly_fields = ["last_login", "date_joined"]
