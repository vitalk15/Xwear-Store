from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from easy_thumbnails.files import get_thumbnailer
from xwear.models import (
    Category,
    Product,
    ProductImage,
    ProductSize,
    ProductSpecification,
)
from .utils import get_thumbnail_data

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "email", "password", "password_confirm")

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError("Пароли не совпадают")
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        user = User.objects.create_user(
            email=validated_data["email"], password=validated_data["password"]
        )
        return user
        # return User.objects.create_user(**validated_data)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(write_only=True, required=True)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Старый пароль неверный")
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError("Пароли не совпадают")
        return attrs

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        uid = self.context.get("uid")
        token = self.context.get("token")

        if not uid or not token:
            raise serializers.ValidationError("Неверный uid или token")

        # Валидация uid
        try:
            decoded_uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=decoded_uid)
        except (TypeError, ValueError, User.DoesNotExist) as exc:
            raise serializers.ValidationError("Неверная ссылка") from exc

        # Валидация токена
        if not default_token_generator.check_token(user, token):
            raise serializers.ValidationError("Неверный или истёкший токен")

        # Сохраняем user для view
        self.user = user

        # Валидация паролей
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError("Пароли не совпадают")

        return attrs

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


# кастомный сериализатор, добавляем в payload токена кроме user_id, exp, iat ещё token_version
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["user_id"] = user.id
        token["token_version"] = user.token_version  # Добавляем в payload
        return token

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    has_children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "level", "children", "has_children"]

    # рекурсивная сериализация активных дочерних элементов
    def get_children(self, obj):
        if obj.is_leaf_node():
            return []

        children = obj.get_children().filter(is_active=True)
        serializer = CategorySerializer(children, many=True, context=self.context)
        return serializer.data

    # есть ли активные дочерние элементы (для ленивой загрузки подкатегорий на фронте, если их будет много)
    def get_has_children(self, obj):
        return obj.get_children().filter(is_active=True).exists()

    # есть ли дочерние элементы, без фильтра активности
    # def get_has_children(self, obj):
    #     return not obj.is_leaf_node()


class ProductImageSerializer(serializers.ModelSerializer):
    thumbnails = serializers.SerializerMethodField()

    def get_thumbnails(self, obj):
        request = self.context.get("request")
        if not obj.image:
            return None

        thumbnailer = get_thumbnailer(obj.image)

        aliases = {
            "small": "product_small",
            "medium": "product_medium",
            "large": "product_large",
        }

        data = {}
        for key, alias_name in aliases.items():
            try:
                thumb = thumbnailer.get_thumbnail({"alias": alias_name})
                data[key] = {
                    "url": request.build_absolute_uri(thumb.url),
                    "width": thumb.width,  # Берется из кэша БД (THUMBNAIL_CACHE_DIMENSIONS)
                    "height": thumb.height,
                }
            except Exception:
                # Если файл поврежден, просто пропускаем этот размер
                continue

        data["original"] = request.build_absolute_uri(obj.image.url)
        return data

    class Meta:
        model = ProductImage
        fields = ["id", "thumbnails", "is_main", "alt"]


class ProductSizeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="size.name", read_only=True)

    class Meta:
        model = ProductSize
        fields = ["id", "name", "price", "is_active"]


class SpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSpecification
        fields = [
            "article",
            "season",
            "material_outer",
            "material_inner",
            "material_sole",
        ]


class ProductListSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    category_slug = serializers.CharField(source="category.slug", read_only=True)
    min_price = serializers.SerializerMethodField()
    main_image = serializers.SerializerMethodField()
    sizes = ProductSizeSerializer(
        source='sizes.order_by("-size")', many=True, read_only=True
    )
    # gender_display = serializers.CharField(source="get_gender_display", read_only=True)

    def get_min_price(self, obj):
        active_sizes = obj.sizes.filter(is_active=True)
        return (
            min(active_sizes.values_list("price", flat=True))
            if active_sizes.exists()
            else 0
        )

    def get_main_image(self, obj):
        main = getattr(obj, "main_image_preview", [])
        main_img = main[0] if main else None

        if main_img:
            return {
                "medium": get_thumbnail_data(
                    main_img.image, "product_medium", self.context["request"]
                ),
                "alt": main_img.alt,
            }
        return None

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "category",
            "category_slug",
            "gender",
            "sizes",
            "min_price",
            "main_image",
            "is_active",
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    category_slug = serializers.CharField(source="category.slug", read_only=True)
    sizes = ProductSizeSerializer(
        source='sizes.order_by("-size")', many=True, read_only=True
    )
    # gender_display = serializers.CharField(source="get_gender_display", read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    specification = SpecificationSerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "category",
            "category_slug",
            "description",
            "gender",
            "sizes",
            "images",
            "specification",
            "is_active",
        ]
