from django.db import models
from django.conf import settings
from xwear.models import Product, ProductSize
from accounts.models import City


# --- Корзина ---


class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
        verbose_name="Пользователь",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    def __str__(self):
        return f"Корзина {self.user.email}"

    @property
    def total_price(self):
        return sum(item.total_item_price for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name="items", verbose_name="Корзина"
    )
    product_size = models.ForeignKey(
        ProductSize, on_delete=models.CASCADE, verbose_name="Товар и размер"
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")

    class Meta:
        verbose_name = "Товар в корзине"
        verbose_name_plural = "Товары в корзине"

    def __str__(self):
        return f"{self.product_size.product.name} ({self.product_size.size.name}) x {self.quantity}"

    @property
    def total_item_price(self):
        return self.product_size.final_price * self.quantity


# --- Заказы ---


class Order(models.Model):
    STATUS_CHOICES = [
        ("processing", "В обработке"),
        ("paid", "Оплачен"),
        ("shipped", "Отправлен"),
        ("completed", "Завершен"),
        ("canceled", "Отменен"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Пользователь",
    )
    city = models.ForeignKey(
        City, on_delete=models.PROTECT, verbose_name="Город доставки"
    )
    # Данные адреса храним строкой (снимок на момент заказа)
    address_text = models.TextField(verbose_name="Адрес доставки (улица, дом, кв)")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="new",
        verbose_name="Статус",
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Итоговая сумма",
    )
    delivery_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Стоимость доставки",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Заказ #{self.id} ({self.user.email})"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Заказ",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Товар",
    )

    # Снимки данных на момент покупки
    product_name = models.CharField(max_length=50, verbose_name="Название товара")
    size_name = models.CharField(max_length=10, verbose_name="Размер")
    price_at_purchase = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена покупки",
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")

    class Meta:
        verbose_name = "Товар в заказе"
        verbose_name_plural = "Товары в заказе"

    def __str__(self):
        return f"{self.product_name} (x{self.quantity}) для заказа #{self.order.id}"
