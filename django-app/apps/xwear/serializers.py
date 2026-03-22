from rest_framework import serializers
from .models import (
    Category,
    Brand,
    Product,
    ProductImage,
    ProductSize,
    Material,
    ProductSpecification,
    Favorite,
    SliderBanner,
)
from .utils import get_thumbnail_data


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    full_path = serializers.CharField(source="get_full_path", read_only=True)
    is_clickable = serializers.SerializerMethodField()
    # has_children = serializers.SerializerMethodField()

    def get_is_clickable(self, obj):
        # Кликабельны все категории, кроме корневых (level 0)
        return not obj.is_root_node()

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "level", "full_path", "is_clickable", "children"]

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
    has_discount = serializers.ReadOnlyField()
    is_available = serializers.SerializerMethodField()

    # Если будем использовать остатки
    # def get_is_available(self, obj):
    #     return obj.stock > 0 and obj.product.is_active

    def get_is_available(self, obj):
        return obj.product.is_active

    class Meta:
        model = ProductSize
        fields = [
            "id",
            "size_name",
            "final_price",
            "price",
            "discount_percent",
            "has_discount",
            "is_available",
        ]


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ["id", "name"]


class SpecificationSerializer(serializers.ModelSerializer):
    # Показываем названия вместо ID
    material_outer = MaterialSerializer(read_only=True)
    material_inner = MaterialSerializer(read_only=True)
    material_sole = MaterialSerializer(read_only=True)

    class Meta:
        model = ProductSpecification
        fields = [
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
    gender_display = serializers.CharField(source="get_gender_display", read_only=True)
    naming = serializers.SerializerMethodField()
    pricing = serializers.SerializerMethodField()

    # min_price = serializers.SerializerMethodField()
    # old_min_price = serializers.SerializerMethodField()
    # discount_percent = serializers.SerializerMethodField()
    main_image = serializers.SerializerMethodField()
    frontend_url = serializers.SerializerMethodField()

    def get_naming(self, obj):
        return {
            "type": obj.type_name,
            "brand": {
                "name": obj.brand.name,
                "slug": obj.brand.slug,
            },
            "model": obj.model_name,
            "category": {
                "name": obj.category.name,
                "slug": obj.category.slug,
            },
            # Полезно для заголовка вкладки в браузере
            "full_title": obj.full_name,
        }

    def get_pricing(self, obj):
        # Используем аннотацию, если она есть (для скорости)
        annotated_price = getattr(obj, "annotated_min_final_price", None)

        if annotated_price is not None:
            return {
                "min_price": annotated_price,
                "old_price": getattr(obj, "annotated_old_price", None),
                "discount": getattr(obj, "annotated_discount", 0),
            }

        # Фоллбек (запасной вариант), если аннотации нет
        # ВАЖНО: убедитесь, что во вьюхе сделан prefetch_related('sizes')
        active_sizes = [s for s in obj.sizes.all() if s.is_active]
        if not active_sizes:
            return {"min_price": 0, "old_price": None, "discount": 0}

        cheapest = min(active_sizes, key=lambda s: s.final_price)
        return {
            "min_price": cheapest.final_price,
            "old_price": cheapest.price if cheapest.has_discount else None,
            "discount": cheapest.discount_percent if cheapest.has_discount else 0,
        }

    # def _get_cheapest_size(self, obj):
    #     """Вспомогательный метод для поиска самого дешевого активного размера"""
    #     active_sizes = [s for s in obj.sizes.all() if s.is_active]
    #     if not active_sizes:
    #         return None
    #     # Находим объект размера с минимальной ценой final_price
    #     return min(active_sizes, key=lambda s: s.final_price)

    # def get_min_price(self, obj):
    #     # Если мы пришли из вьюхи рекомендаций, цена уже посчитана в БД
    #     annotated_price = getattr(obj, "annotated_min_final_price", None)
    #     if annotated_price is not None:
    #         return annotated_price

    #     # В остальных случаях используем
    #     size = self._get_cheapest_size(obj)
    #     return size.final_price if size else 0

    # def get_old_min_price(self, obj):
    #     size = self._get_cheapest_size(obj)
    #     # Показываем старую цену только если на этот конкретный размер есть скидка
    #     if size and size.has_discount:
    #         return size.price
    #     return None

    # def get_discount_percent(self, obj):
    #     size = self._get_cheapest_size(obj)
    #     if size and size.has_discount:
    #         return size.discount_percent
    #     return 0

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

    def get_frontend_url(self, obj):
        # Собираем путь: /catalog/полный-путь-категории/слаг-товара-ID
        category_path = obj.category.get_full_path()
        return f"/catalog/{category_path}/{obj.slug}-{obj.id}/"

    class Meta:
        model = Product
        fields = [
            "id",
            "slug",
            "article",
            "gender",
            "gender_display",
            "naming",
            "pricing",
            "main_image",
            "frontend_url",
            "is_active",
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    gender_display = serializers.CharField(source="get_gender_display", read_only=True)
    sizes = ProductSizeSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    specification = SpecificationSerializer(read_only=True)
    naming = serializers.SerializerMethodField()
    breadcrumbs = serializers.SerializerMethodField()

    def get_breadcrumbs(self, obj):
        # MPTT метод get_ancestors возвращает всю цепочку от корня до текущей категории
        ancestors = obj.category.get_ancestors(include_self=True)
        return [{"name": cat.name, "slug": cat.slug} for cat in ancestors]

    def get_naming(self, obj):
        return {
            "type": obj.type_name,
            "brand": {
                "name": obj.brand.name,
                "slug": obj.brand.slug,
            },
            "model": obj.model_name,
            "category": {
                "name": obj.category.name,
                "slug": obj.category.slug,
            },
            # Полезно для заголовка вкладки в браузере
            "full_title": obj.full_name,
        }

    class Meta:
        model = Product
        fields = [
            "id",
            "slug",
            "article",
            "gender",
            "gender_display",
            "naming",
            "breadcrumbs",
            "description",
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
            "large": "slider_large",
        }
        return get_thumbnail_data(obj.image, aliases, request)

    class Meta:
        model = SliderBanner
        fields = ["id", "title", "link", "thumbnails"]
