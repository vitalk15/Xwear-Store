from django.urls import path
from . import views

urlpatterns = [
    # Корзина
    path("cart/", views.cart_view, name="cart-detail"),
    path("cart/add/", views.cart_add_item, name="cart-add"),
    path("cart/item/<int:pk>/", views.cart_update_item, name="cart-update"),
    path("cart/item/<int:pk>/delete/", views.cart_remove_item, name="cart-delete"),
    # Заказы
    path("orders/checkout/", views.order_create, name="order-checkout"),
    path("orders/", views.order_list, name="order-list"),
]
