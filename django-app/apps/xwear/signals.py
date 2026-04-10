from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from .models import ProductImage


@receiver(post_delete, sender=ProductImage)
def signal_post_delete(sender, instance, **kwargs):
    # post_delete срабатывает, когда объекта уже нет в базе,
    # поэтому мы просто пересчитываем оставшихся
    try:
        # Проверяем, существует ли еще товар.
        # Если мы удаляем вариант целиком, доступ к instance.variant вызовет ошибку.
        variant = instance.variant
        if variant:
            from .utils import sync_product_images

            transaction.on_commit(lambda: sync_product_images(variant))
    except ObjectDoesNotExist:
        # Если товара уже нет в базе (каскадное удаление), просто ничего не делаем
        pass
