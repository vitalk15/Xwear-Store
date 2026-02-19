from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Cart


# сигнал для автоматического создания корзины пользователя при его создании
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_cart(_sender, instance, created, **_kwargs):
    if created:
        Cart.objects.create(user=instance)
