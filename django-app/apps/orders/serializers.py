from rest_framework import serializers
from xwear.utils import get_thumbnail_data
from xwear.models import Product, ProductSize
from core.serializers import CitySerializer
from .models import Cart, CartItem, Order, OrderItem, PickupPoint


# --- КОРЗИНА ---


class ProductCartSerializer(serializers.ModelSerializer):
    # Данные о самом товаре для корзины

    main_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id", "name", "slug", "main_image"]

    def get_main_image(self, obj):
        img_obj = obj.get_main_image_obj
        if img_obj:
            return {
                "thumbnail": get_thumbnail_data(
                    img_obj.image,
                    {"product_small": "product_small"},
                    self.context.get("request"),
                ),
                "alt": img_obj.alt,
            }
        return None


class CartItemSerializer(serializers.ModelSerializer):
    # Для проверки входящих ID (поле используется только для POST и PATCH запросов - write_only=True)
    product_size = serializers.PrimaryKeyRelatedField(
        queryset=ProductSize.objects.all(), write_only=True
    )
    # Данные о товаре (имя, фото)
    product_info = ProductCartSerializer(source="product_size.product", read_only=True)
    # Данные о размере
    size_name = serializers.CharField(source="product_size.size.name", read_only=True)
    # Цена за одну единицу (уже со скидкой)
    unit_price = serializers.DecimalField(
        source="product_size.final_price", max_digits=10, decimal_places=2, read_only=True
    )
    total_item_price = serializers.ReadOnlyField()

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product_size",
            "product_info",
            "size_name",
            "quantity",
            "unit_price",
            "total_item_price",
        ]

    # Проверяем, активен ли товар и есть ли он в наличии
    def validate_product_size(self, value):
        # value — это объект ProductSize, так как PrimaryKeyRelatedField его уже нашел
        product = value.product

        if not product.is_active:
            raise serializers.ValidationError(
                "Этот товар временно недоступен для заказа."
            )

        # Для поля остатка в ProductSize
        # if value.stock <= 0:
        #     raise serializers.ValidationError("Данного размера нет в наличии.")

        return value

    # Валидация количества товаров в корзине и их остатков
    # def validate(self, data):
    #     product_size = data.get("product_size")
    #     requested_quantity = data.get("quantity")

    #     # Если это PATCH, ищем объект в self.instance
    #     if not product_size and self.instance:
    #         product_size = self.instance.product_size

    #     if product_size.stock < requested_quantity:
    #         raise serializers.ValidationError(
    #             {"quantity": f"На складе осталось всего {product_size.stock} шт."}
    #         )

    #     return data


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = Cart
        fields = ["id", "items", "total_price"]


# --- ЗАКАЗЫ ---


class PickupPointSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source="city.name", read_only=True)

    class Meta:
        model = PickupPoint
        fields = [
            "id",
            "city_name",
            "address",
            "work_schedule",
            "phone",
            "lat",
            "lon",
            "is_active",
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    # Если товар еще существует, можем показать его актуальное фото
    # Если удален — product_info будет None, но product_name останется!
    product_info = ProductCartSerializer(source="product", read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_info",
            "product_name",
            "size_name",
            "price_at_purchase",
            "quantity",
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    city_details = CitySerializer(source="city", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    delivery_method_display = serializers.CharField(
        source="get_delivery_method_display", read_only=True
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "status",
            "status_display",
            "delivery_method",
            "delivery_method_display",
            "city",
            "city_details",
            "address_text",
            "total_price",
            "delivery_cost",
            "created_at",
            "updated_at",
            "items",
        ]
