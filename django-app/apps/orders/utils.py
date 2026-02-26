from decimal import Decimal
from django.conf import settings
from xwear.utils import get_thumbnail_data
from core.models import CommercialConfig, ContactSettings


# Формируем расширенный контекст для писем заказа
def get_order_email_context(order):
    # Возвращаем первую запись или создаем пустую (с дефолтными значениями), если её нет
    config, _ = CommercialConfig.objects.get_or_create(id=1)
    contacts, _ = ContactSettings.objects.get_or_create(id=1)

    # Итоговая сумма товаров
    items_total = Decimal("0.00")

    # Собираем данные по товарам
    items_data = []

    # Определяем алиас минииатюры товара для писем
    aliases = {"url": "product_small"}

    # Определяем абсолютный путь к изображению
    for item in order.items.all():
        image_url = None

        if item.product:
            # Благодаря ordering = ["-is_main", "id"] в модели,
            # .first() вернет главное фото или самое первое по ID
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

        # Считаем сумму для конкретной позиции и итоговую сумму
        line_total = item.price_at_purchase * item.quantity
        items_total += line_total

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
        "items_total": items_total,  # Сумма товаров без доставки
        "site_url": settings.SITE_URL,
        "user_name": order.user.first_name or "клиент",
        "contacts": contacts,
        "payment_info": config.payment_info,
    }


# расчёт стоимости доставки и итоговой суммы
def calculate_order_totals(order, items_sum):
    """
    items_sum — сумма товаров без учета доставки.
    """
    # Возвращаем первую запись или создаем пустую (с дефолтными значениями), если её нет
    config, _ = CommercialConfig.objects.get_or_create(id=1)

    # 1. Если самовывоз — доставка всегда бесплатна
    if order.delivery_method == "pickup":
        delivery_cost = Decimal("0.00")

    else:
        # 2. Базовая цена из модели City
        delivery_cost = order.city.delivery_cost

        # 3. Проверяем условие бесплатной доставки
        if config.is_free_delivery_active:
            if items_sum >= config.free_delivery_threshold:
                delivery_cost = Decimal("0.00")

    order.delivery_cost = delivery_cost
    order.total_price = items_sum + delivery_cost
    return order
