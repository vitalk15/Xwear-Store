from django.db import models


class City(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название города")
    is_active = models.BooleanField(default=True, verbose_name="Доступен для доставки")
    delivery_cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Стоимость доставки"
    )

    class Meta:
        verbose_name = "Город и доставка"
        verbose_name_plural = "Города и доставка"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Document(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название документа")
    file = models.FileField(upload_to="documents/", verbose_name="Файл (PDF)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    class Meta:
        verbose_name = "Юридический документ"
        verbose_name_plural = "Юридические документы"

    def __str__(self):
        return self.title


class ContactSettings(models.Model):
    phone = models.CharField(
        max_length=20, verbose_name="Телефон", default="8-802-100-4777"
    )
    email = models.EmailField(verbose_name="Email", default="support@xwear.by")

    # Ссылки на мессенджеры и соцсети
    tg_url = models.URLField(verbose_name="Telegram (ссылка)", blank=True)
    vb_url = models.URLField(verbose_name="Viber (ссылка)", blank=True)
    vk_url = models.URLField(verbose_name="VK (ссылка)", blank=True)
    ok_url = models.URLField(verbose_name="Odnoklassniki (ссылка)", blank=True)
    ig_url = models.URLField(verbose_name="Instagram (ссылка)", blank=True)

    # График работы
    schedule_days = models.CharField(
        max_length=100, verbose_name="Дни работы", default="Пн-Пт"
    )
    schedule_time = models.CharField(
        max_length=100, verbose_name="Время работы", default="с 9:00 до 18:00"
    )
    schedule_extra = models.CharField(
        max_length=100, verbose_name="Выходные дни", default="Сб-Вс: Выходные"
    )

    class Meta:
        verbose_name = "Контакты и соцсети"
        verbose_name_plural = "Контакты и соцсети"

    # def __str__(self):
    #     return "Контакты сайта"


class CommercialConfig(models.Model):
    is_free_delivery_active = models.BooleanField(
        default=True, verbose_name="Активировать бесплатную доставку"
    )
    free_delivery_threshold = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1000,
        verbose_name="Порог бесплатной доставки",
    )
    delivery_info = models.TextField(
        verbose_name="Информация о доставке",
        default="Доставка осуществляется курьером в пределах города. При заказе от 1000 руб. — бесплатно.",
    )
    payment_info = models.TextField(
        verbose_name="Информация об оплате",
        default="Оплата осуществляется при получении заказа картой либо наличными.",
    )

    class Meta:
        verbose_name = "Условия доставки и оплаты"
        verbose_name_plural = "Условия доставки и оплаты"
