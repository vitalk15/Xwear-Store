from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from django.conf import settings
from core.utils import send_custom_email
from .utils import get_order_email_context
from .models import Cart, Order


# # сигнал для автоматического создания корзины пользователя при его создании
# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def create_user_cart(sender, instance, created, **kwargs):
#     if created:
#         Cart.objects.create(user=instance)


# Создаем корзину только если пользователь активен и её еще нет
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_cart(sender, instance, created, **kwargs):
    if instance.is_active:
        Cart.objects.get_or_create(user=instance)


# сигнал для отслеживания изменения статуса заказа и отправки соответствующих писем
@receiver(post_save, sender=Order)
def order_status_changed(sender, instance, created, **kwargs):
    def send():
        context = get_order_email_context(instance)

        # При создании заказа
        if created:
            send_custom_email(
                subject=f"Заказ №{instance.id} принят",
                template_name="orders/emails/order_received.html",
                context=context,
                to_email=instance.user.email,
            )
            return

        # При обновлении статуса (проверка через кастомный флаг status_changed)
        if getattr(instance, "status_changed", False):
            if instance.status == "shipped" and instance.delivery_method == "delivery":
                send_custom_email(
                    subject=f"Ваш заказ №{instance.id} отправлен",
                    template_name="orders/emails/order_shipped.html",
                    context=context,
                    to_email=instance.user.email,
                )
            elif (
                instance.status == "ready_for_pickup"
                and instance.delivery_method == "pickup"
            ):
                send_custom_email(
                    subject=f"Заказ №{instance.id} готов к выдаче",
                    template_name="orders/emails/order_ready.html",
                    context=context,
                    to_email=instance.user.email,
                )
            elif instance.status == "cancelled":
                send_custom_email(
                    subject=f"Заказ №{instance.id} отменен",
                    template_name="orders/emails/order_cancelled.html",
                    context=context,
                    to_email=instance.user.email,
                )

    # Отправляем только после фиксации в БД
    transaction.on_commit(send)
