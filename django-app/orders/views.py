from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from accounts.models import Address
from .utils import send_order_confirmation_email
from .models import Cart, CartItem, Order, OrderItem, PickupPoint
from .serializers import (
    CartSerializer,
    CartItemSerializer,
    OrderSerializer,
)


# Получение корзины текущего пользователя
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def cart_view(request):
    cart = (
        Cart.objects.filter(user=request.user)
        .prefetch_related(
            "items__product_size__product__images", "items__product_size__size"
        )
        .first()
    )

    serializer = CartSerializer(cart, context={"request": request})
    return Response(serializer.data)


# Добавление товара в корзину или увеличение количества
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cart_add_item(request):
    cart = request.user.cart
    serializer = CartItemSerializer(data=request.data)

    if serializer.is_valid():
        product_size = serializer.validated_data["product_size"]
        quantity = serializer.validated_data.get("quantity", 1)

        # Если такой товар с таким размером уже есть — просто увеличиваем количество
        item, created = CartItem.objects.get_or_create(
            cart=cart, product_size=product_size, defaults={"quantity": quantity}
        )
        if not created:
            item.quantity += quantity
            item.save()

        return Response(
            # Возвращаем обновленную корзину целиком, чтобы фронтенд сразу перерисовал итоговую сумму
            CartSerializer(cart, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Изменение количества товара в корзине (кнопки + / -)
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def cart_update_item(request, pk):
    # Ищем товар именно в корзине текущего юзера (безопасность!)
    item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)

    # Мы разрешаем менять только поле quantity
    serializer = CartItemSerializer(item, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        # Возвращаем обновленную корзину целиком, чтобы фронтенд сразу перерисовал итоговую сумму
        cart = request.user.cart
        return Response(
            CartSerializer(cart, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Удаление позиции из корзины
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def cart_remove_item(request, pk):
    item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
    item.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# Оформление заказа из корзины
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def order_create(request):
    user = request.user
    cart = user.cart
    delivery_method = request.data.get("delivery_method")

    # Если применяем остатки, используем не этот код, а код в транзакции
    # -------------------------------------------------
    cart_items = cart.items.select_related("product_size__product", "product_size__size")

    # 1. Проверяем, не пуста ли корзина
    if not cart_items.exists():
        return Response(
            {"error": "Ваша корзина пуста"}, status=status.HTTP_400_BAD_REQUEST
        )

    # 2. Валидация доступности товара перед созданием заказа
    for item in cart_items:
        product = item.product_size.product
        if not product.is_active:
            return Response(
                {"error": f"К сожалению, товар '{product.name}' больше недоступен."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    # ------------------------------------------------------------

    # 3. Получаем данные адреса (доставки или ПВЗ) и стоимости из запроса
    if delivery_method == "delivery":
        address_id = request.data.get("address_id")

        if not address_id:
            return Response(
                {"error": "Необходимо указать адрес доставки"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Ищем адрес именно этого пользователя
        address_obj = get_object_or_404(
            Address, id=address_id, profile__user=user.profile
        )
        city = address_obj.city

        if not city.is_active:
            return Response(
                {"error": "Доставка в этот город недоступна"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        address_text = address_obj.address_simple
        delivery_cost = city.delivery_cost
        pickup_point = None
    else:
        pickup_id = request.data.get("pickup_point_id")

        if not pickup_id:
            return Response(
                {"error": "Необходимо указать адрес ПВЗ"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        pickup_point = get_object_or_404(PickupPoint, id=pickup_id, is_active=True)
        city = pickup_point.city
        address_text = f"ПВЗ: {pickup_point.address} ({pickup_point.working_hours})"
        delivery_cost = 0

    total_price = cart.total_price + delivery_cost

    try:
        # Атомарная транзакция: либо выполняется всё, либо ничего
        with transaction.atomic():
            # Если будем использовать остатки товара (stock в ProductSize)
            # ------------------------------------------------------------
            # Блокируем строки ProductSize в базе данных для этого заказа
            # .select_for_update() гарантирует, что никто другой не изменит остатки, пока транзакция не завершиться
            # cart_items = cart.items.select_related(
            #     "product_size__product",
            #     "product_size__size"
            # ).select_for_update()

            # if not cart_items.exists():
            #     return Response(
            #         {"error": "Ваша корзина пуста"}, status=status.HTTP_400_BAD_REQUEST
            #     )

            # for item in cart_items:
            #     ps = item.product_size

            #     # Проверка активности и остатков
            #     if not ps.product.is_active or ps.stock < item.quantity:
            #         return Response(
            #             {
            #                 "error": f"Товар {ps.product.name} (размер {ps.size.name}) недоступен."
            #             },
            #             status=status.HTTP_400_BAD_REQUEST,
            #         )

            #     # Списываем остатки
            #     ps.stock -= item.quantity
            #     ps.save()

            # -----------------------------------------------------------

            # 4. Создаем объект заказа
            order = Order.objects.create(
                user=user,
                delivery_method=delivery_method,
                pickup_point=pickup_point,
                city=city,
                address_text=address_text,
                delivery_cost=delivery_cost,
                total_price=total_price,
                status="processing",
            )

            # 5. Переносим товары из корзины в OrderItem (делаем снимки)
            order_items = [
                OrderItem(
                    order=order,
                    product=item.product_size.product,
                    product_name=item.product_size.product.name,  # Снимок имени
                    size_name=item.product_size.size.name,  # Снимок размера
                    price_at_purchase=item.product_size.final_price,  # Снимок цены
                    quantity=item.quantity,
                )
                for item in cart_items
            ]

            # Массовое создание для экономии запросов к БД
            OrderItem.objects.bulk_create(order_items)

            # 6. Очищаем корзину
            cart_items.delete()

            # 7. Возвращаем созданный заказ
            serializer = OrderSerializer(order, context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response(
            {"error": f"Ошибка при оформлении заказа: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# Список всех заказов текущего пользователя
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def order_list(request):
    orders = request.user.orders.all().prefetch_related("items")
    serializer = OrderSerializer(orders, many=True, context={"request": request})
    return Response(serializer.data)
