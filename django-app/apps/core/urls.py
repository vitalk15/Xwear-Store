from django.urls import path
from .views import city_list_view


urlpatterns = [
    path("cities/", city_list_view, name="city-list"),
]
