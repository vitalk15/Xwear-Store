from django.urls import path
from .views import (
    category_tree_view,
    product_detail_view,
    category_detail_view,
    slider_banner_list_view,
    favorite_list,
    favorite_toggle,
    product_recommends_view,
)


urlpatterns = [
    path("slider/", slider_banner_list_view, name="slider-list"),
    path("categories/", category_tree_view, name="category_tree"),
    path("categories/<int:pk>/products/", category_detail_view, name="category_detail"),
    path("products/<int:pk>/", product_detail_view, name="product_detail"),
    path(
        "products/<int:pk>/recommends/",
        product_recommends_view,
        name="product_recommends",
    ),
    path("favorites/", favorite_list, name="favorite-list"),
    path("favorites/toggle/<int:pk>/", favorite_toggle, name="favorite-toggle"),
]
