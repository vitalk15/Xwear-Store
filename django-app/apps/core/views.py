from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import City
from .serializers import CitySerializer


# Получение списка городов для доставки
@api_view(["GET"])
@permission_classes([AllowAny])
def city_list_view(request):
    cities = City.objects.filter(is_active=True)
    serializer = CitySerializer(cities, many=True)
    return Response(serializer.data)
