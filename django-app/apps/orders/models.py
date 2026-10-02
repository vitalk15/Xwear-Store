import requests
from django.contrib import admin
from django.db import models
from django.conf import settings

from xwear.models import ProductVariant, ProductSize

# --- Корзина ---


class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
        verbose_name="Пользователь",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"Корзина {self.user.email}"

    @property
    @admin.display(description="Итоговая стоимость")
    def total_price(self):
        return sum(item.total_item_price for item in self.items.all())

    @property
    @admin.display(description="Всего товаров")
    def total_quantity(self):
        return sum(item.quantity for item in self.items.all())

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name="items", verbose_name="Корзина"
    )
    product_size = models.ForeignKey(
        ProductSize, on_delete=models.CASCADE, verbose_name="Товар и размер"
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")

    def __str__(self):
        # variant_name = self.product_size.variant.full_name
        # size_name = self.product_size.size.name

        # return f"{variant_name} - Размер: {size_name}"
        return ""

    @property
    @admin.display(description="Стоимость")
    def total_item_price(self):
        return self.product_size.final_price * self.quantity

    class Meta:
        verbose_name = "Товар в корзине"
        verbose_name_plural = "Товары в корзине"


# --- Адреса ПВЗ ---


class PickupPoint(models.Model):
    city = models.ForeignKey(
        "core.City",
        on_delete=models.CASCADE,
        related_name="pickup_points",
        verbose_name="Город",
    )
    address = models.CharField(max_length=255, verbose_name="Адрес (улица, дом)")
    work_schedule = models.CharField(
        max_length=255,
        help_text="Напр: Пн-Пт 10:00-22:00, Сб-Вс 10:00-20:00",
        default="Пн-Вс 10:00-21:00",
        verbose_name="Режим работы",
    )
    phone = models.CharField(max_length=20, verbose_name="Телефон ПВЗ", blank=True)

    # Координаты для карты
    lat = models.DecimalField(
        max_digits=9, decimal_places=6, verbose_name="Широта", null=True, blank=True
    )
    lon = models.DecimalField(
        max_digits=9, decimal_places=6, verbose_name="Долгота", null=True, blank=True
    )

    is_active = models.BooleanField(default=True, verbose_name="Активен")

    def save(self, *args, **kwargs):
        # Если координаты не введены вручную
        if not self.lat or not self.lon:
            try:
                full_address = f"{self.city.name}, {self.address}"

                url = "https://geocode-maps.yandex.ru/1.x/"
                params = {
                    "apikey": settings.API_KEY_GEOKODER_YANDEX,
                    "geocode": full_address,
                    "format": "json",
                }

                response = requests.get(url, params=params, timeout=5)
                data = response.json()

                # Извлекаем найденные объекты
                feature_member = (
                    data.get("response", {})
                    .get("GeoObjectCollection", {})
                    .get("featureMember", [])
                )

                if feature_member:
                    # Строка координат вида "37.617635 55.755814" (долгота широта)
                    pos = feature_member[0]["GeoObject"]["Point"]["pos"]
                    lon_str, lat_str = pos.split(" ")

                    self.lon = float(lon_str)
                    self.lat = float(lat_str)
            except Exception as e:
                print(f"Ошибка геокодирования Яндекса: {e}")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.city}, {self.address}"

    class Meta:
        verbose_name = "Пункт выдачи"
        verbose_name_plural = "Пункты выдачи"


# --- Заказы ---


class Order(models.Model):
    DELIVERY_METHODS = [
        ("pickup", "Самовывоз"),
        ("delivery", "Доставка"),
    ]

    PAYMENT_METHODS = [
        ("online", "Онлайн картой"),
        ("upon_receipt", "При получении"),
    ]

    STATUS_CHOICES = [
        ("processing", "В обработке"),
        # ("paid", "Оплачен"),  # (возможно понадобится позже)
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
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        default="online",
        verbose_name="Способ оплаты",
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

    @property
    def total_quantity(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def items_total_price(self):
        return sum(item.total_price for item in self.items.all())

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

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ["-created_at"]


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Заказ",
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Вариант товара",
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

    @property
    def total_price(self):
        return self.price_at_purchase * self.quantity

    def __str__(self):
        # return f"{self.product_name} (x{self.quantity}) для заказа #{self.order.id}"
        return ""

    class Meta:
        verbose_name = "Товар в заказе"
        verbose_name_plural = "Товары в заказе"
