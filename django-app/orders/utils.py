from django.core.mail import send_mail
from django.conf import settings


# Функция для отправки письма об успешно созданном заказе
def send_order_confirmation_email(order):
    subject = f"Заказ №{order.id} оформлен | XWEAR"
    message = (
        f"Здравствуйте, {order.user.first_name if order.user.first_name else 'покупатель'}!\n\n"
        f"Ваш заказ №{order.id} успешно принят в обработку.\n"
        f"Сумма заказа: {order.total_price} руб. (включая доставку {order.delivery_cost} руб.)\n"
        f"Адрес доставки: {order.city.name}, {order.address_text}\n\n"
        f"С вами свяжется менеджер для уточнения деталей доставки.\n\n"
        f"Спасибо, что выбрали XWEAR!"
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [order.user.email])
