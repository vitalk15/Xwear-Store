from django.urls import path
from .views import (
    category_tree_view,
    product_detail_view,
    category_detail_view,
    slider_banner_list_view,
    favorite_list,
    favorite_toggle,
)


urlpatterns = [
    path("slider/", slider_banner_list_view, name="slider-list"),
    path("categories/", category_tree_view, name="category_tree"),
    path(
        "categories/<slug:category_slug>/", category_detail_view, name="category_detail"
    ),
    path(
        "categories/<slug:category_slug>/<slug:product_slug>/",
        product_detail_view,
        name="product_detail",
    ),
    path("favorites/", favorite_list, name="favorite-list"),
    path("favorites/toggle/<int:pk>/", favorite_toggle, name="favorite-toggle"),
]
