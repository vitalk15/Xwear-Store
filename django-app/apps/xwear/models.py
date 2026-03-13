from decimal import Decimal, ROUND_HALF_UP
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from easy_thumbnails.fields import ThumbnailerImageField
from easy_thumbnails.files import generate_all_aliases
from .utils import (
    UploadToPath,
    convert_to_webp,
    generate_unique_slug,
    generate_unique_article,
)
from .validators import ImageValidator


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
        # корневая категория
        if self.is_root_node():
            return self.name.upper()

        # для глубоких категорий
        indent = "--" * self.level
        return (
            f"{indent} {self.parent.name} / {self.name}"
            if self.level > 1
            else f"{indent} {self.name}"
        )
        # return (
        #     f"{self.parent.name} / {self.name}"
        #     if self.level > 1
        #     else f"{self.parent.name.upper()} > {self.name}"
        # )

    class MPTTMeta:
        order_insertion_by = ["name"]

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        unique_together = [
            "parent",
            "slug",
        ]  # уникальная комбинация род.категории и слага


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

    final_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Итоговая цена",
        blank=True,
        editable=False,  # Скрываем из админки (пользователь не должен менять её вручную)
        default=0,  # Временный дефолт для старых записей
    )

    is_active = models.BooleanField(default=True, verbose_name="В наличии")

    def save(self, *args, **kwargs):
        # 1. Рассчитываем итоговую цену перед сохранением
        if self.discount_percent > 0:
            # Формула: Цена * (1 - Скидка / 100)
            discount_multiplier = Decimal("1") - (
                Decimal(self.discount_percent) / Decimal("100")
            )
            new_price = self.price * discount_multiplier
            self.final_price = new_price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        else:
            self.final_price = self.price

        # 2. Вызываем оригинальный метод save() для записи в БД
        super().save(*args, **kwargs)

    @property
    def has_discount(self):
        return self.discount_percent > 0

    def __str__(self):
        return "Размерная шкала"

    class Meta:
        unique_together = ["product", "size"]
        verbose_name = "Размер/цена товара"
        verbose_name_plural = "Размеры/цены товаров"


class ProductImage(models.Model):
    product = models.ForeignKey(
        "Product", on_delete=models.CASCADE, related_name="images", verbose_name="Товар"
    )
    image = ThumbnailerImageField(
        upload_to=UploadToPath("products"),
        validators=[ImageValidator(min_width=670, min_height=490, max_mb=1.5)],
        verbose_name="Фото (min 670x490, max 1,5Мб)",
    )
    is_main = models.BooleanField(default=False, verbose_name="Главное фото")
    alt = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Alt текст",
        help_text="Оставьте пустым для автогенерации",
    )
    position = models.PositiveIntegerField(default=0, db_index=True)

    def save(self, *args, **kwargs):
        # Если позиция не задана (новое фото)
        if self.position is None:
            last_image = (
                ProductImage.objects.filter(product=self.product)
                .order_by("-position")
                .first()
            )
            self.position = (last_image.position + 1) if last_image else 0

        # Если файл новый или изменился
        is_new_image = not self.pk or self._image_changed()

        if self.image and is_new_image:
            # Принудительно получаем актуальный объект продукта из БД,
            # чтобы подтянуть сгенерированный слаг
            if self.product_id:
                prod = Product.objects.filter(pk=self.product_id).first()
                if prod:
                    self.product = prod

            # 1. Конвертируем
            webp_content = convert_to_webp(self.image)

            # 2. Генерируем имя
            upload_processor = UploadToPath("products/")
            # Передаем self, чтобы UploadToPath увидел обновленного self.product
            new_path = upload_processor(self, self.image.name)

            # 4. Подменяем файл (save=False, чтобы не зациклить)
            # self.image.save(new_filename, webp_content, save=False)

            # 4. Подменяем файл и путь напрямую в поле - СПЕЦИАЛЬНО ДЛЯ ThumbnailerImageField:
            # Это позволяет избежать лишних циклов сохранения.
            self.image.file = webp_content
            self.image.name = new_path

        super().save(*args, **kwargs)

        # 4. Запускаем генерацию миниатюр
        if self.image and is_new_image:
            generate_all_aliases(self.image, include_global=True)

    def _image_changed(self):
        """Проверка, изменился ли файл изображения"""
        try:
            old_obj = ProductImage.objects.get(pk=self.pk)
            return old_obj.image != self.image
        except ProductImage.DoesNotExist:
            return True

    def __str__(self):
        if self.is_main:
            return f"ГЛАВНОЕ ФОТО ({self.product.name})"
        return f"Фото №{self.position + 1} ({self.product.name})"

    class Meta:
        verbose_name = "Фото товара"
        verbose_name_plural = "Фото товаров"
        # ordering = ["-is_main"]
        ordering = ["position"]


class Product(models.Model):
    class GenderChoices(models.TextChoices):
        MALE = "M", "Мужской"
        FEMALE = "F", "Женский"
        UNISEX = "U", "Унисекс"

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="products",
        verbose_name="Категория",
    )
    name = models.CharField(max_length=50, verbose_name="Название")
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
        return self.images.first()

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


class Material(models.Model):
    class MaterialType(models.TextChoices):
        OUTER = "OUTER", "Верх"
        INNER = "INNER", "Подкладка"
        SOLE = "SOLE", "Подошва"

    name = models.CharField(max_length=100, verbose_name="Название")
    material_type = models.CharField(
        max_length=10, choices=MaterialType.choices, verbose_name="Назначение"
    )

    class Meta:
        verbose_name = "Материал"
        verbose_name_plural = "Материалы"
        unique_together = (
            "name",
            "material_type",
        )

    def __str__(self):
        # return f"{self.name} ({self.get_material_type_display()})"
        return self.name


class ProductSpecification(models.Model):
    class SeasonChoices(models.TextChoices):
        WINTER = "WINTER", "Зима"
        SUMMER = "SUMMER", "Лето"
        AUTUMN_SPRING = "AUTUMN_SPRING", "Демисезон"
        ALL_SEASON = "ALL_SEASON", "Всесезонный"

    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name="specification",
        verbose_name="Характеристики",
    )
    article = models.CharField(
        max_length=50,
        verbose_name="Артикул",
        unique=True,
        blank=True,
        help_text="Оставьте пустым для автогенерации (BRAND-CAT-ID-RANDOM) или введите вручную.",
    )
    season = models.CharField(
        max_length=20,
        choices=SeasonChoices.choices,
        verbose_name="Сезон",
    )

    # Состав (общие и специфические поля)
    material_outer = models.ForeignKey(
        Material,
        on_delete=models.PROTECT,
        limit_choices_to={"material_type": "OUTER"},  # Фильтр только для верха
        related_name="outer_material",
        verbose_name="Материал верха",
    )
    material_inner = models.ForeignKey(
        Material,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"material_type": "INNER"},  # Фильтр только для подкладки
        related_name="inner_material",
        verbose_name="Материал подкладки",
    )
    material_sole = models.ForeignKey(
        Material,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"material_type": "SOLE"},  # Фильтр только для подошвы
        related_name="sole_material",
        verbose_name="Материал подошвы",
    )

    def save(self, *args, **kwargs):
        if not self.article:
            # Генерируем, пока не найдем уникальный (на всякий случай)
            new_article = generate_unique_article(self)
            while ProductSpecification.objects.filter(article=new_article).exists():
                new_article = generate_unique_article(self)
            self.article = new_article

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Характеристики товара"
        verbose_name_plural = "Характеристики товаров"

    # def __str__(self):
    #     return f"Характеристики для {self.product.name}"


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Пользователь",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="favorited_by",
        verbose_name="Товар",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Добавлено")

    class Meta:
        # Это гарантирует, что пользователь не сможет добавить один и тот же товар в избранное дважды
        unique_together = ("user", "product")
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"

    def __str__(self):
        return f"{self.user} -> {self.product.name}"


class SliderBanner(models.Model):
    title = models.CharField(max_length=100, verbose_name="Заголовок")
    image = ThumbnailerImageField(
        upload_to=UploadToPath("slider", "slide"),
        validators=[ImageValidator(min_width=1540, min_height=630, max_mb=2.0)],
        verbose_name="Изображение (min 1540x630, max 2Мб)",
    )
    link = models.URLField(blank=True, verbose_name="Ссылка")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    def save(self, *args, **kwargs):
        # Если позиция не задана (новое фото)
        # if self.position is None:
        #     last_image = (
        #         ProductImage.objects.filter(product=self.product)
        #         .order_by("-position")
        #         .first()
        #     )
        #     self.position = (last_image.position + 1) if last_image else 0

        # Если файл новый или изменился
        if not self.pk or self._image_changed():
            convert_to_webp(self.image, quality=100)

        super().save(*args, **kwargs)

    def _image_changed(self):
        """Проверка, изменился ли файл изображения"""
        try:
            old_obj = ProductImage.objects.get(pk=self.pk)
            return old_obj.image != self.image
        except ProductImage.DoesNotExist:
            return True

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Слайд"
        verbose_name_plural = "Слайды"
        ordering = ["order", "-id"]
