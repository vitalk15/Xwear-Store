from django.contrib import admin
from .models import City


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active", "delivery_cost"]
    list_editable = ["is_active", "delivery_cost"]
    search_fields = ["name"]
