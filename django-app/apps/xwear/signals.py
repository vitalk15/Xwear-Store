from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
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


def sync_product_images(product):
    images = list(product.images.all().order_by("position"))
    if not images:
        return

    first_image = images[0]

    # Если первое фото не главное — исправляем это в базе
    if not first_image.is_main:
        # Сбрасываем у всех остальных (одним запросом)
        product.images.exclude(pk=first_image.pk).update(is_main=False)
        # Делаем главной
        product.images.filter(pk=first_image.pk).update(is_main=True)


@receiver(post_save, sender=ProductImage)
def signal_post_save(sender, instance, **kwargs):
    transaction.on_commit(lambda: sync_product_images(instance.product))


@receiver(post_delete, sender=ProductImage)
def signal_post_delete(sender, instance, **kwargs):
    # post_delete срабатывает, когда объекта уже нет в базе,
    # поэтому мы просто пересчитываем оставшихся
    transaction.on_commit(lambda: sync_product_images(instance.product))
