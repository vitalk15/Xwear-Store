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
from .models import Category, Product, ProductSize, Favorite, SliderBanner
from .serializers import (
    CategorySerializer,
    BrandSerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    FavoriteSerializer,
    SliderBannerSerializer,
)


# дерево категорий
@api_view(["GET"])
def category_tree_view(request):
    # Забираем ВСЕ активные категории одним запросом
    queryset = Category.objects.filter(is_active=True)

    # Строим дерево в памяти с помощью mptt метода - это исключает N+1 запросов в сериализаторе
    tree = queryset.get_cached_trees()

    # без корневой mptt-категории
    categories = [node for node in tree if node.level == 1]
    serializer = CategorySerializer(categories, many=True, context={"request": request})
    return Response(serializer.data)


# товары категории
@api_view(["GET"])
def category_detail_view(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug, is_active=True)

    # MPTT breadcrumbs
    breadcrumbs = [
        {"name": cat.name, "slug": cat.slug}
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

    return paginator.get_paginated_response(
        {
            "category": {
                "id": category.id,
                "name": category.name,
                "slug": category.slug,
                "breadcrumbs": breadcrumbs,
            },
            "filters": {
                "brands": BrandSerializer(filters_data["brands"], many=True).data,
                "sizes": filters_data["sizes"],
                "price_range": filters_data["price_range"],
            },
            "products": serializer.data,
        }
    )


# Детали товара
@api_view(["GET"])
def product_detail_view(request, category_slug, product_slug):
    product = get_object_or_404(
        Product.objects.filter(
            is_active=True, category__slug=category_slug, slug=product_slug
        )
        .select_related("category", "brand", "specification")
        .prefetch_related(
            "images",
            # Уже делаем сортировку в ProductImage, поэтому не используем здесь:
            # Prefetch("images", queryset=ProductImage.objects.order_by("-is_main", "id")),
            Prefetch(
                "sizes",
                queryset=ProductSize.objects.filter(is_active=True).select_related(
                    "size"
                ),
            ),
        )
    )

    serializer = ProductDetailSerializer(product, context={"request": request})
    return Response(serializer.data, status=status.HTTP_200_OK)


# Список избранных товаров пользователя
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def favorite_list(request):
    favorites = Favorite.objects.filter(user=request.user).select_related(
        "product", "product__brand"
    )
    serializer = FavoriteSerializer(favorites, many=True, context={"request": request})

    return Response(serializer.data)


# Добавление/удаление товара из избранного
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def favorite_toggle(request, pk):
    product = get_object_or_404(Product, pk=pk)
    favorite_qs = Favorite.objects.filter(user=request.user, product=product)

    if favorite_qs.exists():
        favorite_qs.delete()
        return Response(
            {"detail": "Удалено из избранного"}, status=status.HTTP_204_NO_CONTENT
        )

    Favorite.objects.create(user=request.user, product=product)
    return Response({"detail": "Добавлено в избранное"}, status=status.HTTP_201_CREATED)


# Слайдер
@api_view(["GET"])
def slider_banner_list_view(request):
    banners = SliderBanner.objects.filter(is_active=True)
    serializer = SliderBannerSerializer(banners, many=True, context={"request": request})

    return Response(serializer.data)


# Рекомендации товаров
@api_view(["GET"])
def product_recommendations_view(request, category_slug, product_slug):
    # Находим основной товар
    product = get_object_or_404(
        Product.objects.filter(
            is_active=True, category__slug=category_slug, slug=product_slug
        )
    )

    # Получаем рекомендации
    recommendations = get_similar_products(product)

    serializer = ProductListSerializer(
        recommendations, many=True, context={"request": request}
    )
    return Response(serializer.data)
