from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import status
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from .utils import (
    get_similar_products,
    get_category_sidebar_filters,
    get_filtered_products,
)
from .models import Category, ProductVariant, ProductSize, Favorite, SliderBanner
from .serializers import (
    CategorySerializer,
    BrandSerializer,
    ColorSerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    FavoriteSerializer,
    SliderBannerSerializer,
)

# ==========================================
# КАТЕГОРИИ И КАТАЛОГ
# ==========================================


# дерево категорий
@api_view(["GET"])
def category_tree_view(request):
    # Забираем ВСЕ активные категории одним запросом
    queryset = Category.objects.filter(is_active=True)

    # Строим дерево в памяти с помощью mptt метода - это исключает N+1 запросов в сериализаторе
    tree = queryset.get_cached_trees()

    # без корневой mptt-категории [node for node in tree if node.level == 1]
    categories = [node for node in tree if node.level == 0]
    serializer = CategorySerializer(categories, many=True, context={"request": request})
    return Response(serializer.data)


# товары категории
@api_view(["GET"])
def category_detail_view(request, pk):
    category = get_object_or_404(Category, pk=pk, is_active=True)

    # MPTT breadcrumbs
    breadcrumbs = [
        {"name": cat.name, "slug": cat.slug, "id": cat.id}
        for cat in category.get_ancestors(include_self=True)
    ]

    # Фильтрация для сайдбара
    # 1. Получаем саму категорию и всех её потомков (для MPTT)
    categories = category.get_descendants(include_self=True)

    # 2. Получаем данные для сайдбара
    filters_data = get_category_sidebar_filters(categories)

    # 3. Получаем отфильтрованные товары
    products_queryset = get_filtered_products(categories, request.query_params)

    # 4. Пагинация (из settings.py) и сериализация
    paginator = LimitOffsetPagination()
    page = paginator.paginate_queryset(products_queryset, request)
    serializer = ProductListSerializer(page, many=True, context={"request": request})

    # По стандарту REST API метаданные (категория, фильтры) должны лежать на одном уровне с ключами пагинации (count, next, previous), а сами товары — внутри списка results.
    # Получаем стандартный ответ DRF (где сериализованные товары лежат в "results")
    response = paginator.get_paginated_response(serializer.data)

    # Внедряем наши кастомные данные на верхний уровень JSON
    response.data["category"] = {
        "id": category.id,
        "name": category.name,
        "breadcrumbs": breadcrumbs,
    }
    response.data["filters"] = {
        "brands": BrandSerializer(filters_data["brands"], many=True).data,
        "colors": ColorSerializer(filters_data["colors"], many=True).data,
        "sizes": filters_data["sizes"],
        "price_range": filters_data["price_range"],
    }

    # В результате структура JSON-ответа будет:
    # {
    #   "count": 150,
    #   "next": "http://api.../?limit=20&offset=20",
    #   "previous": null,
    #   "category": { ... },
    #   "filters": { ... },
    #   "results": [ ...массив товаров... ]
    # }

    return response


# ==========================================
# ДЕТАЛИ ТОВАРА И РЕКОМЕНДАЦИИ
# ==========================================


# Детали товара
@api_view(["GET"])
def product_detail_view(request, pk):
    variant = get_object_or_404(
        ProductVariant.objects.filter(is_active=True, pk=pk)
        .select_related(
            "product__category",
            "product__brand",
            "color",
            "composition__material_outer",
            "composition__material_inner",
            "composition__material_sole",
        )
        .prefetch_related(
            "images",
            "product__variants__color",  # Подгружаем соседние цвета (через родительский товар)
            # Уже делаем сортировку в ProductImage, поэтому не используем здесь:
            # Prefetch("images", queryset=ProductImage.objects.order_by("-is_main", "id")),
            Prefetch("sizes", queryset=ProductSize.objects.select_related("size")),
        )
    )

    serializer = ProductDetailSerializer(variant, context={"request": request})
    return Response(serializer.data, status=status.HTTP_200_OK)


# Рекомендации товаров
@api_view(["GET"])
def product_recommends_view(request, pk):
    # Находим вариант товара
    variant = get_object_or_404(ProductVariant.objects.filter(is_active=True, pk=pk))

    # Получаем рекомендации
    recommends = get_similar_products(variant)

    serializer = ProductListSerializer(
        recommends, many=True, context={"request": request}
    )
    return Response(serializer.data)


# ==========================================
# ИЗБРАННОЕ И БАННЕРЫ
# ==========================================


# Список избранных товаров пользователя
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def favorite_list(request):
    favorites = Favorite.objects.filter(user=request.user).select_related(
        "variant__color", "variant__product__brand"
    )
    serializer = FavoriteSerializer(favorites, many=True, context={"request": request})

    return Response(serializer.data)


# Добавление/удаление товара из избранного
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def favorite_toggle(request, pk):
    # Добавляем в избранное конкретный цвет (вариант)
    variant = get_object_or_404(ProductVariant, pk=pk)
    favorite_qs = Favorite.objects.filter(user=request.user, variant=variant)

    if favorite_qs.exists():
        favorite_qs.delete()
        return Response(
            {"detail": "Удалено из избранного"}, status=status.HTTP_204_NO_CONTENT
        )

    Favorite.objects.create(user=request.user, variant=variant)
    return Response({"detail": "Добавлено в избранное"}, status=status.HTTP_201_CREATED)


# Слайдер
@api_view(["GET"])
def slider_banner_list_view(request):
    banners = SliderBanner.objects.filter(is_active=True)
    serializer = SliderBannerSerializer(banners, many=True, context={"request": request})

    return Response(serializer.data)
