from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from core.utils import send_custom_email
from .utils import account_activation_token_generator
from .models import Profile


User = get_user_model()


# сигнал для автоматического создания профиля при создании пользователя
# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)


# Если профиль уже есть, но нужно обновить связь
# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     if hasattr(instance, "profile"):
#         instance.profile.save()


# Отправляем письмо для подтверждения почты только НОВОМУ и НЕАКТИВНОМУ пользователю
@receiver(post_save, sender=User)
def send_activation_email_signal(sender, instance, created, **kwargs):
    if created and not instance.is_active:
        token = account_activation_token_generator.make_token(instance)
        uid = urlsafe_base64_encode(force_bytes(instance.pk))

        activation_link = f"{settings.SITE_URL}/activate/{uid}/{token}/"

        context = {
            "user_name": instance.email.split("@")[0],
            "activation_link": activation_link,
            "timeout_hours": settings.ACCOUNT_ACTIVATION_TIMEOUT // 3600,
        }

        send_custom_email(
            subject="Подтверждение регистрации",
            template_name="accounts/emails/activation_email.html",
            context=context,
            to_email=instance.email,
        )


# Создаем профиль только если пользователь активен и его еще нет
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if instance.is_active:
        Profile.objects.get_or_create(user=instance)


# Обновляем профиль только если он существует
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if instance.is_active and hasattr(instance, "profile"):
        instance.profile.save()
