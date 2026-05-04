import json
from rest_framework import serializers
from .models import (
    Category,
    Brand,
    Color,
    ProductVariant,
    ProductImage,
    ProductSize,
    Material,
    ProductMaterial,
    Favorite,
    SliderBanner,
)
from .utils import get_thumbnail_data

# ==========================================
# БАЗОВЫЕ СЕРИАЛИЗАТОРЫ
# ==========================================


class CategorySerializer(serializers.ModelSerializer):
    full_path = serializers.CharField(source="get_full_path", read_only=True)
    children = serializers.SerializerMethodField()
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


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ["id", "name", "slug", "hex_code", "hex_code_2", "texture"]


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ["id", "name"]


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ["id", "name", "slug"]


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
        # Размер доступен, если активен сам вариант и активен базовый товар
        return obj.variant.is_active and obj.variant.product.is_active

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


class ProductMaterialSerializer(serializers.ModelSerializer):
    # Показываем названия вместо ID
    material_outer = MaterialSerializer(read_only=True)
    material_inner = MaterialSerializer(read_only=True)
    material_sole = MaterialSerializer(read_only=True)

    class Meta:
        model = ProductMaterial
        fields = [
            "material_outer",
            "material_inner",
            "material_sole",
        ]


# ===================================
# СЕРИАЛИЗАТОРЫ ТОВАРОВ
# ===================================


class ProductListSerializer(serializers.ModelSerializer):
    gender_display = serializers.CharField(
        source="product.get_gender_display", read_only=True
    )
    color = ColorSerializer(read_only=True)
    naming = serializers.SerializerMethodField()
    pricing = serializers.SerializerMethodField()
    available_colors = serializers.SerializerMethodField()
    main_image = serializers.SerializerMethodField()
    frontend_url = serializers.SerializerMethodField()

    def get_naming(self, obj):
        product = obj.product
        return {
            "type": product.type_name,
            "brand": {
                "name": product.brand.name,
                "slug": product.brand.slug,
            },
            "model": product.model_name,
            "category": {
                "name": product.category.name,
                "slug": product.category.slug,
            },
            # для заголовка вкладки в браузере
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

        # если аннотации нет
        active_sizes = [s for s in obj.sizes.all() if s.is_active]
        if not active_sizes:
            return {"min_price": 0, "old_price": None, "discount": 0}

        cheapest = min(active_sizes, key=lambda s: s.final_price)
        return {
            "min_price": cheapest.final_price,
            "old_price": cheapest.price if cheapest.has_discount else None,
            "discount": cheapest.discount_percent if cheapest.has_discount else 0,
        }

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
        category_path = obj.product.category.get_full_path()
        return f"/catalog/{category_path}/{obj.slug}-{obj.id}/"

    def get_available_colors(self, obj):
        """
        Собирает все варианты текущего базового товара.
        """
        # Берем все активные варианты базового товара
        #!!! Нужно ли проверять активность базового товара? Проверяется во вьюхе
        variants = obj.product.variants.filter(is_active=True).select_related("color")

        results = []
        for v in variants:
            if v.color:
                results.append(
                    {
                        "color": ColorSerializer(v.color, context=self.context).data,
                        "frontend_url": self.get_frontend_url(v),
                    }
                )
        return results

    class Meta:
        model = ProductVariant
        fields = [
            "id",
            "slug",
            "article",
            "gender",
            "gender_display",
            "naming",
            "pricing",
            "color",
            "available_colors",
            "main_image",
            "frontend_url",
            "is_active",
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    # Общие данные из базового товара
    gender_display = serializers.CharField(
        source="product.get_gender_display", read_only=True
    )
    season_display = serializers.CharField(
        source="product.get_season_display", read_only=True
    )
    description = serializers.SerializerMethodField()

    # Специфичные данные варианта
    sizes = ProductSizeSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    composition = ProductMaterialSerializer(read_only=True)
    color = ColorSerializer(read_only=True)

    # Динамические поля
    available_colors = serializers.SerializerMethodField()
    naming = serializers.SerializerMethodField()
    breadcrumbs = serializers.SerializerMethodField()
    frontend_url = serializers.SerializerMethodField()

    def get_breadcrumbs(self, obj):
        # MPTT метод get_ancestors возвращает всю цепочку от корня до текущей категории
        ancestors = obj.product.category.get_ancestors(include_self=True)
        return [{"name": cat.name, "slug": cat.slug} for cat in ancestors]

    def get_frontend_url(self, obj):
        category_path = obj.product.category.get_full_path()
        return f"/catalog/{category_path}/{obj.slug}-{obj.id}/"

    def get_naming(self, obj):
        product = obj.product
        return {
            "type": product.type_name,
            "brand": {
                "name": product.brand.name,
                "slug": product.brand.slug,
            },
            "model": product.model_name,
            "category": {
                "name": product.category.name,
                "slug": product.category.slug,
            },
            # для заголовка вкладки в браузере
            "full_title": obj.full_name,
        }

    def get_available_colors(self, obj):
        """
        Собирает все варианты текущего базового товара.
        """
        # Берем все активные варианты базового товара
        #!!! Нужно ли проверять активность базового товара?
        variants = obj.product.variants.filter(is_active=True).select_related("color")

        results = []
        for v in variants:
            if v.color:
                results.append(
                    {
                        "color": ColorSerializer(v.color, context=self.context).data,
                        "frontend_url": self.get_frontend_url(v),
                        "is_current": v.id
                        == obj.id,  # Флаг, для выделения текущего цвета
                    }
                )
        return results

    def get_description(self, obj):
        if obj.product and obj.product.description:
            try:
                # Возвращаем Delta JSON
                return json.loads(obj.product.description.delta)
            except (ValueError, AttributeError):
                # На случай, если в базе оказался невалидный JSON или пустая строка
                return None
        return None

    class Meta:
        model = ProductVariant
        fields = [
            "id",
            "slug",
            "article",
            "gender_display",
            "naming",
            "season_display",
            "color",
            "available_colors",
            "breadcrumbs",
            "description",
            "sizes",
            "images",
            "composition",
            "is_active",
        ]


# ==========================================
# ОСТАЛЬНЫЕ СЕРИАЛИЗАТОРЫ
# ==========================================


class FavoriteSerializer(serializers.ModelSerializer):
    # При получении списка избранного будем разворачивать данные о товаре
    variant_details = ProductListSerializer(source="variant", read_only=True)

    class Meta:
        model = Favorite
        fields = ["id", "variant", "variant_details", "created_at"]
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
        fields = ["id", "title", "links", "thumbnails"]
