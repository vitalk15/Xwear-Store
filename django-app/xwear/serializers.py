from rest_framework import serializers
from .models import (
    Category,
    Brand,
    Product,
    ProductImage,
    ProductSize,
    ProductSpecification,
    Favorite,
    SliderBanner,
)
from .utils import get_thumbnail_data


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    # has_children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "level", "children"]

    # рекурсивная сериализация активных дочерних элементов (до 300-500 категорий)
    def get_children(self, obj):
        # get_children() в MPTT при использовании get_cached_trees
        # берет данные из кэша объекта, а не из БД
        if obj.is_leaf_node():
            return []

        # Если дерево было кэшировано через get_cached_trees,
        # этот цикл не будет делать запросов к БД
        children = [child for child in obj.get_children() if child.is_active]
        serializer = CategorySerializer(children, many=True, context=self.context)
        return serializer.data

    # для ленивой загрузки подкатегорий на фронте (1000 и более категорий)
    # def get_has_children(self, obj):
    #     # Проверяем наличие активных детей в кэше
    #     return any(child.is_active for child in obj.get_children())


class ProductImageSerializer(serializers.ModelSerializer):
    thumbnails = serializers.SerializerMethodField()

    def get_thumbnails(self, obj):
        request = self.context.get("request")
        aliases = {
            "small": "product_small",
            "large": "product_large",
        }
        data = get_thumbnail_data(obj.image, aliases, request)

        if data and obj.image:
            data["original"] = request.build_absolute_uri(obj.image.url)

        return data

    class Meta:
        model = ProductImage
        fields = ["id", "thumbnails", "is_main", "alt"]


class ProductSizeSerializer(serializers.ModelSerializer):
    size_name = serializers.CharField(source="size.name", read_only=True)
    # final_price — метод-свойство модели (цена со скидкой или обычная)
    final_price = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    # old_price — это исходная цена из поля price
    old_price = serializers.DecimalField(
        source="price", max_digits=6, decimal_places=2, read_only=True
    )
    # has_discount — метод-свойство модели
    has_discount = serializers.BooleanField(read_only=True)

    # Если планируем только отдавать данные (read-only), и не нужна специальная валидация на входе, можно использовать serializers.ReadOnlyField. Он просто берет значение «как есть»:
    # size_name = serializers.ReadOnlyField(source="size.name")
    # final_price = serializers.ReadOnlyField()
    # old_price = serializers.ReadOnlyField(source="price")
    # has_discount = serializers.ReadOnlyField()

    is_available = serializers.SerializerMethodField()

    class Meta:
        model = ProductSize
        fields = [
            "id",
            "size_name",
            "final_price",
            "old_price",
            "discount_percent",
            "has_discount",
            "is_available",
        ]

    # Если будем использовать остатки
    # def get_is_available(self, obj):
    #     return obj.stock > 0 and obj.product.is_active

    def get_is_available(self, obj):
        return obj.product.is_active


class SpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSpecification
        fields = [
            "article",
            "season",
            "material_outer",
            "material_inner",
            "material_sole",
        ]


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ["id", "name", "slug"]


class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    category_slug = serializers.CharField(source="category.slug", read_only=True)
    brand_name = serializers.CharField(source="brand.name", read_only=True)
    min_price = serializers.SerializerMethodField()
    old_min_price = serializers.SerializerMethodField()
    discount_percent = serializers.SerializerMethodField()
    main_image = serializers.SerializerMethodField()
    # gender_display = serializers.CharField(source="get_gender_display", read_only=True)

    def _get_cheapest_size(self, obj):
        """Вспомогательный метод для поиска самого дешевого активного размера"""
        active_sizes = [s for s in obj.sizes.all() if s.is_active]
        if not active_sizes:
            return None
        # Находим объект размера с минимальной ценой final_price
        return min(active_sizes, key=lambda s: s.final_price)

    def get_min_price(self, obj):
        size = self._get_cheapest_size(obj)
        return size.final_price if size else 0

    def get_old_min_price(self, obj):
        size = self._get_cheapest_size(obj)
        # Показываем старую цену только если на этот конкретный размер есть скидка
        if size and size.has_discount:
            return size.price
        return None

    def get_discount_percent(self, obj):
        size = self._get_cheapest_size(obj)
        if size and size.has_discount:
            return size.discount_percent
        return 0

    def get_main_image(self, obj):
        img_obj = obj.get_main_image_obj
        if img_obj:
            return {
                "thumbnails": get_thumbnail_data(
                    img_obj.image, {"medium": "product_medium"}, self.context["request"]
                ),
                "alt": img_obj.alt,
            }
        return None

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "category_name",
            "category_slug",
            "brand_name",
            "gender",
            "min_price",
            "old_min_price",
            "discount_percent",
            "main_image",
            "is_active",
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    category_slug = serializers.CharField(source="category.slug", read_only=True)
    brand = BrandSerializer(read_only=True)
    sizes = ProductSizeSerializer(
        source='sizes.order_by("-size")', many=True, read_only=True
    )
    # gender_display = serializers.CharField(source="get_gender_display", read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    specification = SpecificationSerializer(read_only=True)
    breadcrumbs = serializers.SerializerMethodField()

    def get_breadcrumbs(self, obj):
        # MPTT метод get_ancestors возвращает всю цепочку от корня до текущей категории
        ancestors = obj.category.get_ancestors(include_self=True)
        return [{"name": cat.name, "slug": cat.slug} for cat in ancestors]

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "category_name",
            "category_slug",
            "brand",
            "breadcrumbs",
            "description",
            "gender",
            "sizes",
            "images",
            "specification",
            "is_active",
        ]


class FavoriteSerializer(serializers.ModelSerializer):
    # При получении списка избранного будем разворачивать данные о товаре
    product_details = ProductListSerializer(source="product", read_only=True)

    class Meta:
        model = Favorite
        fields = ["id", "product", "product_details", "created_at"]
        read_only_fields = ["id", "created_at"]


class SliderBannerSerializer(serializers.ModelSerializer):
    thumbnails = serializers.SerializerMethodField()

    def get_thumbnails(self, obj):
        request = self.context.get("request")
        aliases = {
            "main": "slider_main",
        }
        return get_thumbnail_data(obj.image, aliases, request)

    class Meta:
        model = SliderBanner
        fields = ["id", "title", "link", "thumbnails"]
