# ВЫБОРКА И ФИЛЬТРАЦИЯ ДАННЫХ ДЛЯ КАТАЛОГА, РЕКОМЕНДАЦИИ

import random
from django.db.models import Prefetch, Min, Max, Q


# Собирает только доступные значения для сайдбара (бренды, размеры, диапазон цен, цвета)
def get_category_sidebar_filters(categories, query_params):
    # from ..models import ProductVariant, ProductSize, Brand, Color
    from ..models import ProductSize, Brand, Color

    # 1. Цены (Применяем все фильтры КРОМЕ цен)
    qs_for_prices = get_filtered_products(categories, query_params, exclude_group="prices")
    price_stats = qs_for_prices.aggregate(
        min_p=Min("annotated_min_final_price"),
        max_p=Max("annotated_min_final_price"),
    )

    # 2. Бренды (Применяем все фильтры КРОМЕ брендов)
    qs_for_brands = get_filtered_products(categories, query_params, exclude_group="brands")
    # Достаем ID доступных брендов и возвращаем QuerySet брендов
    brand_ids = qs_for_brands.values_list("product__brand_id", flat=True).distinct()
    brands = Brand.objects.filter(id__in=brand_ids)

    # 3. Цвета (Применяем все фильтры КРОМЕ цветов)
    qs_for_colors = get_filtered_products(categories, query_params, exclude_group="colors")
    color_ids = qs_for_colors.values_list("color_id", flat=True).distinct()
    colors = Color.objects.filter(id__in=color_ids)

    # 4. Размеры (Применяем все фильтры КРОМЕ размеров)
    qs_for_sizes = get_filtered_products(categories, query_params, exclude_group="sizes")
    sizes = (
        ProductSize.objects.filter(
            variant__in=qs_for_sizes,
            is_active=True,
        )
        .values_list("size__name", flat=True)
        .distinct()
    )

    # # Базовый кверисет — только активные варианты активных базовых товаров
    # sidebar_data_qs = ProductVariant.objects.filter(
    #     product__category__in=categories, is_active=True, product__is_active=True
    # )

    # # 1. Цены, доступные в этой категории
    # price_stats = sidebar_data_qs.aggregate(
    #     min_p=Min("sizes__final_price", filter=Q(sizes__is_active=True)),
    #     max_p=Max("sizes__final_price", filter=Q(sizes__is_active=True)),
    # )

    # # 2. Бренды, доступные в этой категории
    # brands = Brand.objects.filter(
    #     products__variants__is_active=True,
    #     products__category__in=categories,
    #     products__is_active=True,
    # ).distinct()

    # # 3. Размеры, доступные в этой категории
    # sizes = (
    #     ProductSize.objects.filter(
    #         variant__product__category__in=categories,
    #         variant__is_active=True,
    #         variant__product__is_active=True,
    #         is_active=True,
    #     )
    #     .values_list("size__name", flat=True)
    #     .distinct()
    #     # .order_by("size__name")
    # )

    # # 4. Цвета, доступные в этой категории
    # colors = Color.objects.filter(
    #     variants__product__category__in=categories,
    #     variants__is_active=True,
    #     variants__product__is_active=True,
    # ).distinct()

    return {
        "brands": brands,
        "sizes": list(sizes),
        "colors": colors,
        "price_range": {
            "min": price_stats["min_p"] or 0,
            "max": price_stats["max_p"] or 0,
        },
    }


# Возвращает отфильтрованный QuerySet товаров для фильтров сайдбара
def get_filtered_products(categories, query_params, exclude_group=None):
    from ..models import ProductVariant, ProductSize

    queryset = (
        ProductVariant.objects.filter(
            product__category__in=categories, is_active=True, product__is_active=True
        )
        .annotate(
            # Находим минимальную цену среди размеров для этого товара
            annotated_min_final_price=Min(
                "sizes__final_price", filter=Q(sizes__is_active=True)
            )
        )
        .select_related("product__brand", "product__category", "color")
        .prefetch_related(
            "images",
            "product__variants__color",  # Соседние цвета для кружочков
            Prefetch(
                "sizes",
                queryset=ProductSize.objects.filter(is_active=True).select_related(
                    "size"
                ),
            ),
        )
        # .order_by("-product__created_at", "-id") # сортируем по дате создания родителя
        # .order_by("-created_at", "-id")  # сортируем по дате создания варианта
    )

    # -------------- ПРИМЕНЯЕМ ФИЛЬТРЫ (если группа не исключена) --------------
    # 1. Современный подход через запятую (в URL: ?brands=nike,adidas)
    # Фильтр по брендам
    brands_param = query_params.get("brands")
    if brands_param and exclude_group != "brands":
        # brand_slugs = brands_param.split(",")
        # Убираем лишние пробелы и пустые элементы на всякий случай
        brand_slugs = [s.strip() for s in brands_param.split(",") if s.strip()]
        queryset = queryset.filter(product__brand__slug__in=brand_slugs)

    # Фильтр по цветам
    colors_param = query_params.get("colors")
    if colors_param and exclude_group != "colors":
        color_slugs = [s.strip() for s in colors_param.split(",") if s.strip()]
        queryset = queryset.filter(color__slug__in=color_slugs)

    # Фильтр по размерам
    sizes_param = query_params.get("sizes")
    if sizes_param and exclude_group != "sizes":
        # size_names = sizes_param.split(",")
        size_names = [s.strip() for s in sizes_param.split(",") if s.strip()]
        # Если фильтруем по размерам, нужен distinct, так как у товара много размеров
        queryset = queryset.filter(
            sizes__size__name__in=size_names, sizes__is_active=True
        ).distinct()

    # 2. Стандартный подход (в URL: ?brands=nike&brands=adidas)
    # brand_slugs = query_params.getlist("brands")
    # if brand_slugs:
    #     queryset = queryset.filter(brand__slug__in=brand_slugs)

    # size_names = query_params.getlist("sizes")
    # if size_names:
    #     # Если фильтруем по размерам, нужен distinct, так как у товара много размеров
    #     queryset = queryset.filter(
    #         sizes__size__name__in=size_names, sizes__is_active=True
    #     ).distinct()

    # Фильтр по цене
    if exclude_group != "prices":
        min_p = query_params.get("min_price")
        max_p = query_params.get("max_price")
        if min_p:
            queryset = queryset.filter(annotated_min_final_price__gte=min_p)
        if max_p:
            queryset = queryset.filter(annotated_min_final_price__lte=max_p)

    # ------------------ СОРТИРОВКА (обработка параметра `sort`) ------------------
    sort_param = query_params.get("sort", "default")

    if sort_param == "price_asc":
        # Сначала дешевые (по возрастанию аннотированной цены)
        queryset = queryset.order_by("annotated_min_final_price", "-id")
    elif sort_param == "price_desc":
        # Сначала дорогие (по убыванию аннотированной цены)
        queryset = queryset.order_by("-annotated_min_final_price", "-id")
    elif sort_param == "newest":
        # Сначала новинки
        queryset = queryset.order_by("-created_at", "-id")
    else:
        # По умолчанию - Сначала новинки (по дате добавления)
        queryset = queryset.order_by("-created_at", "-id")

    return queryset


# Показ рекомендаций
def get_similar_products(variant, limit=8):
    """
    Возвращает товары из той же подкатегории в ценовом диапазоне +/- 20% рандомно.
    В блок рекомендаций всегда попадает только один цвет от одной базовой модели.
    """
    from ..models import ProductVariant, ProductSize

    # 1. Получаем минимальную финальную цену текущего варианта для расчета диапазона
    # (Берем из аннотации, если она была во вьюхе, или считаем)
    current_min_price = getattr(variant, "annotated_min_final_price", None)
    if current_min_price is None:
        price_data = variant.sizes.filter(is_active=True).aggregate(
            min_p=Min("final_price")
        )
        current_min_price = price_data["min_p"]

    if current_min_price is None:
        return []

    # 2. Расчет диапазона +/- 20%
    min_range = float(current_min_price) * 0.8
    max_range = float(current_min_price) * 1.2

    # 3. Ищем подходящие варианты (исключаем всю семью текущего базового товара)
    candidates = (
        ProductVariant.objects.filter(
            is_active=True,
            product__is_active=True,
            product__category=variant.product.category,
        )
        .exclude(product_id=variant.product_id)  # Исключаем всю текущую семью
        .annotate(
            # Аннотируем каждый товар в базе его минимальной ценой
            annotated_min_p=Min("sizes__final_price", filter=Q(sizes__is_active=True))
        )
        .filter(annotated_min_p__range=(min_range, max_range))
    )

    # 4. Дедупликация: берем только один вариант от каждого базового товара
    candidate_data = list(candidates.values("id", "product_id"))
    seen_products = set()
    unique_variant_ids = []

    for v in candidate_data:
        if v["product_id"] not in seen_products:
            seen_products.add(v["product_id"])
            unique_variant_ids.append(v["id"])

    # 5. Если товаров мало, добираем без учета цены (но тоже уникальные модели)
    if len(unique_variant_ids) < 4:
        extra_candidates = (
            ProductVariant.objects.filter(
                is_active=True,
                product__is_active=True,
                product__category=variant.product.category,
            )
            .exclude(product_id=variant.product_id)
            .exclude(id__in=unique_variant_ids)
        )

        extra_data = list(extra_candidates.values("id", "product_id"))
        for v in extra_data:
            if v["product_id"] not in seen_products:
                seen_products.add(v["product_id"])
                unique_variant_ids.append(v["id"])

    # 6. Выбираем случайные ID, в количестве = limit
    sample_size = min(len(unique_variant_ids), limit)
    random_ids = random.sample(unique_variant_ids, sample_size)

    # 7. Финальный запрос с полной подгрузкой данных
    return (
        ProductVariant.objects.filter(id__in=random_ids)
        .annotate(
            annotated_min_final_price=Min(
                "sizes__final_price", filter=Q(sizes__is_active=True)
            )
        )
        .select_related("product__brand", "product__category", "color")
        .prefetch_related(
            "images",
            "product__variants__color",
            Prefetch(
                "sizes",
                queryset=ProductSize.objects.filter(is_active=True).select_related(
                    "size"
                ),
            ),
        )
    )
