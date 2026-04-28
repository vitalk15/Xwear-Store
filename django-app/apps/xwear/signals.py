# from django.db.models.signals import post_delete, m2m_changed
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from easy_thumbnails.files import get_thumbnailer
from .models import ProductImage

# from .models import ProductImage, ProductVariant


@receiver(post_delete, sender=ProductImage)
def signal_post_delete(sender, instance, **kwargs):
    """
    1. Удаляет кэш миниатюр при удалении объекта.
    2. Синхронизирует позиции оставшихся фото.
    """
    # --- 1: Очистка миниатюр ---
    if instance.image:
        try:
            # get_thumbnailer найдет все превью, связанные с этим файлом в папке thumbnails
            get_thumbnailer(instance.image).delete_thumbnails()
        except Exception:
            # Ошибка удаления миниатюр не должна прерывать работу сигнала
            pass

    # --- 2: Логика синхронизации ---
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


@receiver(pre_save, sender=ProductImage)
def signal_pre_save_image_cleanup(sender, instance, **kwargs):
    """
    Удаляет миниатюры старого изображения, если файл был заменен на новый.
    """
    if not instance.pk:
        return  # Это новый объект, чистить нечего

    try:
        old_instance = sender.objects.get(pk=instance.pk)
        # Если путь к файлу изменился (заменили картинку)
        if old_instance.image and old_instance.image != instance.image:
            get_thumbnailer(old_instance.image).delete_thumbnails()
    except sender.DoesNotExist:
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
