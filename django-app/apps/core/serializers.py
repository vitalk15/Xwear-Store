import json
from rest_framework import serializers
from .models import City, Document, ContactSettings, CommercialConfig, AboutUs


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ["id", "name", "delivery_cost"]


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ["id", "title", "file"]


class ContactSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactSettings
        fields = "__all__"


class CommercialConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommercialConfig
        fields = "__all__"


class AboutUsSerializer(serializers.ModelSerializer):
    # Переопределяем поле контента, чтобы отдавать чистый Delta JSON
    content = serializers.SerializerMethodField()

    class Meta:
        model = AboutUs
        fields = ["id", "title", "content", "is_active"]

    def get_content(self, obj):
        if obj.content:
            try:
                # Извлекаем Delta-формат из QuillField
                return json.loads(obj.content.delta)
            except (ValueError, AttributeError):
                # На случай, если в базе оказался невалидный JSON или пустая строка
                return None
        return None
