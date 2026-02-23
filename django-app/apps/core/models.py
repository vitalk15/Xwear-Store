from django.db import models


class City(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название города")
    is_active = models.BooleanField(default=True, verbose_name="Доступен для доставки")
    delivery_cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Стоимость доставки"
    )

    class Meta:
        verbose_name = "Город"
        verbose_name_plural = "Список городов"
        ordering = ["name"]

    def __str__(self):
        return self.name
