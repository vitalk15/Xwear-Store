from django.db import models
from django.conf import settings
from xwear.models import Product, ProductSize


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


# --- Адреса ПВЗ ---


class PickupPoint(models.Model):
    city = models.ForeignKey(
        "core.City",
        on_delete=models.CASCADE,
        related_name="pickup_points",
        verbose_name="Город",
    )
    address = models.CharField(max_length=255, verbose_name="Адрес (улица, дом)")
    working_hours = models.CharField(
        max_length=255,
        help_text="Напр: Будни 9:00-22:00, Сб-Вс 10:00-20:00",
        verbose_name="Время работы",
    )
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    class Meta:
        verbose_name = "Пункт выдачи"
        verbose_name_plural = "Пункты выдачи"

    def __str__(self):
        return f"{self.city.name}, {self.address}"


# --- Заказы ---


class Order(models.Model):
    DELIVERY_METHODS = [
        ("pickup", "Самовывоз"),
        ("delivery", "Доставка"),
    ]

    STATUS_CHOICES = [
        ("processing", "В обработке"),
        ("paid", "Оплачен"),  # не используется (возможно понадобится позже)
        ("ready", "Готов к получению"),  # только Самовывоз
        ("shipped", "Отправлен"),  # только Доставка
        ("completed", "Завершен"),
        ("canceled", "Отменен"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Пользователь",
    )
    delivery_method = models.CharField(
        max_length=20,
        choices=DELIVERY_METHODS,
        default="pickup",
        verbose_name="Способ получения",
    )
    pickup_point = models.ForeignKey(
        PickupPoint,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Пункт выдачи",
    )

    # Поля для снимка данных
    city = models.ForeignKey(
        "core.City", on_delete=models.PROTECT, verbose_name="Город доставки"
    )
    address_text = models.TextField(verbose_name="Адрес доставки / ПВЗ")

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="processing",
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Запоминаем статус, который был в базе
        self.__original_status = self.status

    def save(self, *args, **kwargs):
        # Проверяем, изменился ли статус
        self.status_changed = self.status != self.__original_status
        super().save(*args, **kwargs)
        # Обновляем состояние после сохранения
        self.__original_status = self.status

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
