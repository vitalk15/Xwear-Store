from rest_framework import serializers
from .models import (
    Category,
    Brand,
    Color,
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
    color = ColorSerializer(read_only=True)
    naming = serializers.SerializerMethodField()
    pricing = serializers.SerializerMethodField()
    available_colors = serializers.SerializerMethodField()

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

    def get_available_colors(self, obj):
        """
        Собирает все варианты цветов для текущей группы товаров.
        Возвращает список с данными цвета и ссылочными данными товара.
        """
        # 1. Определяем "корень" группы (либо текущий товар, либо его родитель)
        root = obj if obj.base_product_id is None else obj.base_product

        # 2. Собираем всех участников группы: корень + все его дочерние варианты
        # Используем .all(), чтобы не делать лишних запросов (при условии prefetch_related во вьюхе)
        family = [root]
        if hasattr(root, "variants"):
            family.extend(root.variants.all())

        results = []
        for p in family:
            if p.color:
                results.append(
                    {
                        "color": ColorSerializer(p.color, context=self.context).data,
                        # "product_id": p.id,
                        # "product_slug": p.slug,
                        # Опционально: можно сразу пробросить URL для фронтенда
                        "frontend_url": self.get_frontend_url(p),
                    }
                )

        # Сортируем (например, по названию цвета), чтобы порядок был всегда одинаковым
        return sorted(results, key=lambda x: x["color"]["name"])

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
            "color",
            "available_colors",
            "main_image",
            "frontend_url",
            "is_active",
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    gender_display = serializers.CharField(source="get_gender_display", read_only=True)
    sizes = ProductSizeSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    specification = SpecificationSerializer(read_only=True)
    color = ColorSerializer(read_only=True)
    available_colors = serializers.SerializerMethodField()
    naming = serializers.SerializerMethodField()
    breadcrumbs = serializers.SerializerMethodField()
    frontend_url = serializers.SerializerMethodField()

    def get_breadcrumbs(self, obj):
        # MPTT метод get_ancestors возвращает всю цепочку от корня до текущей категории
        ancestors = obj.category.get_ancestors(include_self=True)
        return [{"name": cat.name, "slug": cat.slug} for cat in ancestors]

    def get_frontend_url(self, obj):
        category_path = obj.category.get_full_path()
        return f"/catalog/{category_path}/{obj.slug}-{obj.id}/"

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

    def get_available_colors(self, obj):
        # находим корень и собираем всех "родственников"
        root = obj if obj.base_product_id is None else obj.base_product

        family = [root]
        if hasattr(root, "variants"):
            family.extend(root.variants.all())

        results = []
        for p in family:
            if p.color:
                results.append(
                    {
                        "color": ColorSerializer(p.color, context=self.context).data,
                        # "product_id": p.id,
                        # "product_slug": p.slug,
                        "frontend_url": self.get_frontend_url(p),
                        "is_current": p.id
                        == obj.id,  # Флаг, чтобы фронтенд выделил текущий цвет
                    }
                )

        return sorted(results, key=lambda x: x["color"]["name"])

    class Meta:
        model = Product
        fields = [
            "id",
            "slug",
            "article",
            "gender",
            "gender_display",
            "naming",
            "color",
            "available_colors",
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
