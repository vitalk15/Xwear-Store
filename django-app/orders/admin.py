from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ("product_size", "quantity", "total_item_price")


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    inlines = [CartItemInline]

    list_display = ("id", "user", "total_price")
    fields = ("user", "total_price")
    readonly_fields = ("user", "total_price")


# --- ЗАКАЗЫ ---


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = (
        "product",
        "product_name",
        "size_name",
        "price_at_purchase",
        "quantity",
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]

    list_display = ("id", "user", "status", "total_price", "created_at", "updated_at")
    list_editable = ["status"]
    list_filter = ("status", "city", "created_at", "updated_at")
    search_fields = ("user__email", "id")
    readonly_fields = (
        "user",
        "city",
        "address_text",
        "total_price",
        "delivery_cost",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Основная информация",
            {"fields": ("status", "created_at", "updated_at", "user")},
        ),
        (
            "Доставка",
            {"fields": ("city", "address_text", "delivery_cost")},
        ),
        (
            "Стоимость",
            {
                "fields": ("total_price",),
                "description": "Итоговая стоимость заказа с учетом доставки",
            },
        ),
    )

    # "быстрые действия" для отмены
    actions = ["make_cancelled"]

    @admin.action(description="Отменить выбранные заказы")
    def make_cancelled(self, _request, queryset):
        queryset.update(status="cancelled")

    # Запрещаем удалять заказы админу
    def has_delete_permission(self, request, obj=None):
        return False

    # Запрещаем админу создавать заказы вручную через админку
    def has_add_permission(self, request):
        return False
