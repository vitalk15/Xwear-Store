from django import forms
from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem, PickupPoint


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


@admin.register(PickupPoint)
class PickupPointAdmin(admin.ModelAdmin):
    list_display = ("city", "address", "working_hours", "is_active")
    list_editable = ["is_active"]
    list_filter = ("city", "is_active")


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


# Чтобы менеджер не мог выбрать некорректный статус, мы переопределяем форму в админке.
# Она будет динамически скрывать ненужные опции.
class OrderAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Фильтруем статусы в зависимости от способа доставки
            current_method = self.instance.delivery_method
            all_statuses = Order.STATUS_CHOICES

            if current_method == "pickup":
                # Убираем "Отправлен"
                filtered = [s for s in all_statuses if s[0] != "shipped"]
            else:
                # Убираем "Готов к получению"
                filtered = [s for s in all_statuses if s[0] != "ready_for_pickup"]

            self.fields["status"].choices = filtered


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    form = OrderAdminForm
    inlines = [OrderItemInline]

    list_display = (
        "id",
        "user",
        "delivery_method",
        "status",
        "total_price",
        "created_at",
        "updated_at",
    )
    list_editable = ["status"]
    list_filter = ("delivery_method", "status", "city", "created_at", "updated_at")
    search_fields = ("user__email", "id")
    readonly_fields = (
        "user",
        "delivery_method",
        "pickup_point",
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
            {"fields": ("status", "delivery_method", "user", "created_at", "updated_at")},
        ),
        (
            "Локация",
            {"fields": ("city", "pickup_point", "address_text")},
        ),
        (
            "Стоимость",
            {"fields": ("delivery_cost", "total_price")},
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
