from django.urls import path
from .views import (
    city_list_view,
    document_list,
    contact_detail,
    commercial_config_detail,
    about_us_detail,
)


urlpatterns = [
    path("cities/", city_list_view, name="city-list"),
    path("documents/", document_list, name="document-list"),
    path("contacts/", contact_detail, name="contact-detail"),
    path("commercial-info/", commercial_config_detail, name="commercial-info"),
    path("about/", about_us_detail, name="about-us"),
]
