from django.conf import settings
from xwear.utils import get_thumbnail_data


# Формируем расширенный контекст для писем заказа
def get_order_email_context(order):
    # Собираем данные по товарам
    items_data = []

    # Определяем алиас для писем
    aliases = {"url": "product_small"}

    # Определяем абсолютный путь к изображению
    for item in order.items.all():
        image_url = None

        if item.product:
            main_image_obj = item.product.images.first()

            if main_image_obj:
                # Передаем None вместо request,
                # так как в сигналах request обычно недоступен.
                thumb_data = get_thumbnail_data(
                    main_image_obj.image, aliases, request=None
                )

                if thumb_data and "url" in thumb_data:
                    # Так как request=None, функция вернет относительный путь /media/...
                    # Добавляем SITE_URL вручную
                    image_url = f"{settings.SITE_URL}{thumb_data['url']}"

        # Считаем сумму для конкретной позиции
        line_total = item.price_at_purchase * item.quantity

        items_data.append(
            {
                "name": item.product_name,
                "size": item.size_name,
                "quantity": item.quantity,
                "price": item.price_at_purchase,
                "total": line_total,
                "image_url": image_url,
            }
        )

    return {
        "order": order,
        "items": items_data,
        "site_url": settings.SITE_URL,
        "user_name": order.user.first_name or "клиент",
    }
