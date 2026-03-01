from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import status
from django.db.models import Prefetch, F, ExpressionWrapper, DecimalField, Min, Max, Q
from django.db.models.functions import Round
from django.shortcuts import get_object_or_404
from .utils import get_similar_products
from .models import Category, Brand, Product, ProductSize, Favorite, SliderBanner
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

    # 2. Определяем формулу финальной цены
    final_price_expression = Round(
        ExpressionWrapper(
            F("sizes__price") * (1.0 - F("sizes__discount_percent") / 100.0),
            output_field=DecimalField(),
        )
    )

    # 3. Базовый QuerySet
    # Используем одну аннотацию для всех вычислений
    products_queryset = (
        Product.objects.filter(category__in=categories, is_active=True)
        .annotate(
            # Находим минимальную цену среди размеров для этого товара
            annotated_min_final_price=Min(
                final_price_expression,
                filter=Q(sizes__is_active=True),
            )
        )
        .select_related("brand", "category")
        .prefetch_related(
            "images",
            Prefetch(
                "sizes",
                queryset=ProductSize.objects.filter(is_active=True).select_related(
                    "size"
                ),
            ),
        )
        .order_by("-created_at")
    )

    # 4. Собираем данные для сайдбара ДО применения фильтров
    # Это важно: слайдер цены и список брендов должны показывать все возможности категории
    sidebar_data_qs = Product.objects.filter(category__in=categories, is_active=True)

    price_stats = sidebar_data_qs.annotate(
        p=Min(final_price_expression, filter=Q(sizes__is_active=True))
    ).aggregate(min_p=Min("p"), max_p=Max("p"))

    available_brands = Brand.objects.filter(products__category__in=categories).distinct()
    available_sizes = (
        ProductSize.objects.filter(product__category__in=categories, is_active=True)
        .values_list("size__name", flat=True)
        .distinct()
        .order_by("size__name")
    )

    # 5. Применяем фильтры из URL
    brand_slugs = request.query_params.getlist("brands[]")
    if brand_slugs:
        products_queryset = products_queryset.filter(brand__slug__in=brand_slugs)

    size_names = request.query_params.getlist("sizes[]")
    if size_names:
        # Если фильтруем по размерам, нужен distinct, так как у товара много размеров
        products_queryset = products_queryset.filter(
            sizes__size__name__in=size_names, sizes__is_active=True
        ).distinct()

    min_p = request.query_params.get("min_price")
    max_p = request.query_params.get("max_price")
    if min_p:
        products_queryset = products_queryset.filter(annotated_min_final_price__gte=min_p)
    if max_p:
        products_queryset = products_queryset.filter(annotated_min_final_price__lte=max_p)

    # Пагинация из settings.py
    paginator = LimitOffsetPagination()
    page = paginator.paginate_queryset(products_queryset, request)

    # Передаем контекст для формирования полных ссылок на изображения
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
                "brands": BrandSerializer(available_brands, many=True).data,
                "sizes": list(available_sizes),
                "price_range": {
                    "min": price_stats["min_p"] or 0,
                    "max": price_stats["max_p"] or 0,
                },
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
