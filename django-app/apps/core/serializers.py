from rest_framework import serializers
from .models import City, Document, ContactSettings, CommercialConfig


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
