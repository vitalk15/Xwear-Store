from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from easy_thumbnails.fields import ThumbnailerImageField
from .utils import UploadToPath, generate_unique_slug, validate_banner_image


class Category(MPTTModel):
    name = models.CharField(max_length=30, verbose_name="Название")
    slug = models.SlugField(max_length=30, blank=True, verbose_name="Слаг")
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="Активна")
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="Родительская категория",
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, scope_field="parent")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
        # return f"{self.parent} -> {self.name}"

    class MPTTMeta:
        order_insertion_by = ["name"]

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        unique_together = [
            "parent",
            "slug",
        ]  # уникальная комбинация род.категории и слага


class GenderChoices(models.TextChoices):
    MALE = "M", "Мужской"
    FEMALE = "F", "Женский"
    UNISEX = "U", "Унисекс"


class Brand(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название")
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        verbose_name = "Бренд"
        verbose_name_plural = "Бренды"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Size(models.Model):
    name = models.CharField(max_length=10, verbose_name="Размер")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="Порядок")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Размер"
        verbose_name_plural = "Размеры"


class ProductSize(models.Model):
    product = models.ForeignKey(
        "Product", on_delete=models.CASCADE, related_name="sizes", verbose_name="Товар"
    )
    size = models.ForeignKey(Size, on_delete=models.CASCADE, verbose_name="Размер")
    # stock = models.PositiveIntegerField(default=0, verbose_name="Остаток")
    price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Цена")
    discount_percent = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Скидка %",
    )
    is_active = models.BooleanField(default=True, verbose_name="В наличии")

    @property
    def final_price(self):
        """Возвращает цену с учетом скидки если есть, округленную до целых. Иначе - обычную цену"""
        if self.discount_percent > 0:
            # Формула: NewPrice = Price * (1 - Discount / 100)
            new_price = self.price * (1 - self.discount_percent / 100)
            return round(new_price)
        return self.price

    @property
    def has_discount(self):
        return self.discount_percent > 0

    class Meta:
        unique_together = ["product", "size"]
        verbose_name = "Размер/цена товара"
        verbose_name_plural = "Размеры/цены товаров"


class ProductImage(models.Model):
    product = models.ForeignKey(
        "Product", on_delete=models.CASCADE, related_name="images", verbose_name="Товар"
    )
    image = ThumbnailerImageField(
        upload_to=UploadToPath("products", "prod"), verbose_name="Фото"
    )
    is_main = models.BooleanField(default=False, verbose_name="Главное фото")
    alt = models.CharField(max_length=200, blank=True, verbose_name="Alt текст")

    def save(self, *args, **kwargs):
        # Если ставим is_main=True, сбрасываем у всех остальных фото этого товара
        if self.is_main:
            ProductImage.objects.filter(product=self.product, id__ne=self.id).update(
                is_main=False  # __ne - не равно (альтернатива .exclude(id=self.id))
            )
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Если удаляем главное фото, первое другое фото становиться главным
        if self.is_main:
            other_main = self.product.images.filter(is_main=False).first()
            if other_main:
                other_main.is_main = True
                other_main.save()
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = "Фото товара"
        verbose_name_plural = "Фото товаров"
        ordering = ["-is_main", "id"]


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="products",
        verbose_name="Категория товара",
    )
    name = models.CharField(max_length=50, verbose_name="Наименование")
    slug = models.SlugField(max_length=50, blank=True, verbose_name="Слаг")
    description = models.TextField(blank=True, verbose_name="Описание")
    gender = models.CharField(
        max_length=1, choices=GenderChoices.choices, verbose_name="Пол"
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="products",
        verbose_name="Бренд",
    )
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    @property
    def get_main_image_obj(self):
        images = list(self.images.all())
        return images[0] if images else None

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, scope_field="category")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        unique_together = [
            "category",
            "slug",
        ]
        indexes = [
            models.Index(fields=["is_active", "category"]),
            models.Index(fields=["slug"]),
        ]


class ProductSpecification(models.Model):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name="specification",
        verbose_name="Характеристики",
    )
    article = models.CharField(max_length=50, verbose_name="Артикул", unique=True)
    season = models.CharField(max_length=50, verbose_name="Сезон")

    # Состав (общие и специфические поля)
    material_outer = models.CharField(max_length=255, verbose_name="Материал верха")
    material_inner = models.CharField(
        max_length=255,
        verbose_name="Материал подкладки",
        blank=True,
        null=True,
    )
    material_sole = models.CharField(
        max_length=255,
        verbose_name="Материал подошвы",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Характеристики товара"
        verbose_name_plural = "Характеристики товаров"

    # def __str__(self):
    #     return f"Характеристики для {self.product.name}"


class SliderBanner(models.Model):
    title = models.CharField(max_length=100, verbose_name="Заголовок")
    image = ThumbnailerImageField(
        upload_to=UploadToPath("slider", "slide"),
        validators=[validate_banner_image],
        verbose_name="Изображение (min 1540x630)",
    )
    link = models.URLField(blank=True, verbose_name="Ссылка")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    class Meta:
        verbose_name = "Слайд"
        verbose_name_plural = "Слайды"
        ordering = ["order", "-id"]

    def __str__(self):
        return self.title
