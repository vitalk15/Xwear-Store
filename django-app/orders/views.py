from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer


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
