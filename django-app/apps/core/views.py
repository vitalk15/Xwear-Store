from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import City, Document, ContactSettings, CommercialConfig
from .serializers import (
    CitySerializer,
    DocumentSerializer,
    ContactSettingsSerializer,
    CommercialConfigSerializer,
)


# Получение списка городов для доставки
@api_view(["GET"])
@permission_classes([AllowAny])
def city_list_view(request):
    cities = City.objects.filter(is_active=True)
    serializer = CitySerializer(cities, many=True)
    return Response(serializer.data)


# Получение списка юр.документов
@api_view(["GET"])
@permission_classes([AllowAny])
def document_list(request):
    documents = Document.objects.all().order_by("-created_at")
    serializer = DocumentSerializer(documents, many=True)
    return Response(serializer.data)


# Получение списка контактов
@api_view(["GET"])
@permission_classes([AllowAny])
def contact_detail(request):
    # Возвращаем первую запись или создаем пустую (с дефолтными значениями), если её нет
    config, _ = ContactSettings.objects.get_or_create(id=1)
    serializer = ContactSettingsSerializer(config)
    return Response(serializer.data)


# Получение условий доставки и оплаты
@api_view(["GET"])
@permission_classes([AllowAny])
def commercial_config_detail(request):
    # Возвращаем первую запись или создаем пустую (с дефолтными значениями), если её нет
    config, _ = CommercialConfig.objects.get_or_create(id=1)
    serializer = CommercialConfigSerializer(config)
    return Response(serializer.data)
