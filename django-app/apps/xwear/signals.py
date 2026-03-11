from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from .models import ProductSpecification, ProductImage


@receiver(post_save, sender=ProductSpecification)
def set_product_article(sender, instance, created, **kwargs):
    # Генерируем артикул только если его еще нет
    if not instance.article:
        from .utils import generate_unique_article

        new_article = generate_unique_article(instance)

        if new_article:
            # Используем .update(), так как он НЕ вызывает метод save()
            # и не провоцирует повторный запуск сигналов.
            ProductSpecification.objects.filter(pk=instance.pk).update(
                article=new_article
            )


@receiver(post_delete, sender=ProductImage)
def signal_post_delete(sender, instance, **kwargs):
    # post_delete срабатывает, когда объекта уже нет в базе,
    # поэтому мы просто пересчитываем оставшихся
    try:
        # Проверяем, существует ли еще товар.
        # Если мы удаляем товар целиком, доступ к instance.product вызовет ошибку.
        product = instance.product
        if product:
            from .utils import sync_product_images

            transaction.on_commit(lambda: sync_product_images(product))
    except ObjectDoesNotExist:
        # Если товара уже нет в базе (каскадное удаление), просто ничего не делаем
        pass
