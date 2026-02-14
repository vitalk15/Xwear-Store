from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Profile


# сигнал для автоматического создания профиля при создании пользователя
@receiver(post_save, sender=User)
def create_user_profile(_sender, instance, created, **_kwargs):
    if created:
        Profile.objects.create(user=instance)


# Если профиль уже есть, но нужно обновить связь
@receiver(post_save, sender=User)
def save_user_profile(_sender, instance, **_kwargs):
    if hasattr(instance, "profile"):
        instance.profile.save()
