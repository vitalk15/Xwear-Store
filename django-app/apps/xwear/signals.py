# from django.db.models.signals import post_delete, m2m_changed
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from .models import ProductImage

# from .models import ProductImage, ProductVariant


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


# @receiver(m2m_changed, sender=ProductVariant.sizes.through)
# def update_variant_status_on_size_change(sender, instance, action, **kwargs):
#     """
#     Срабатывает при любом изменении связей 'размеры - вариант'.
#     Работает и в админке, и в API.
#     """
#     if action in ["post_add", "post_remove", "post_clear"]:
#         # Если вариант активен, но у него не осталось активных размеров
#         if instance.is_active and not instance.sizes.filter(is_active=True).exists():
#             instance.is_active = False
#             instance.save(update_fields=["is_active"])
#             # Здесь можно добавить логику уведомления (например, запись в лог)
