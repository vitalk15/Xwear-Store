from decimal import Decimal, ROUND_HALF_UP
from django.core.validators import MinValueValidator, MaxValueValidator

# from django.core.exceptions import ValidationError
# from django.utils.html import format_html
from django.conf import settings
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from easy_thumbnails.fields import ThumbnailerImageField
from easy_thumbnails.files import generate_all_aliases
from .utils import (
    UploadToPath,
    generate_unique_slug,
    prepare_image_for_save,
)
from .validators import ImageValidator


class Category(MPTTModel):
    name = models.CharField(max_length=30, verbose_name="Название")
    singular_name = models.CharField(
        max_length=30,
        blank=True,
        default="",
        verbose_name="Название (ед. ч.)",
        help_text="Оставьте пустым, если совпадает с основным названием или не требуется",
    )
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

    def get_full_path(self):
        """Возвращает полный путь к категории, если она не корневая"""
        # Если это корень, возвращаем пустую строку или None
        if self.is_root_node():
            return ""

        # Только для вложенных категорий лезем в дерево за предками
        ancestors = self.get_ancestors(include_self=True)
        return "/".join([ancestor.slug for ancestor in ancestors])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, scope_field="parent")
        super().save(*args, **kwargs)

    def __str__(self):
        # корневая категория
        # if self.is_root_node():
        #     return self.name.upper()
        if self.parent_id is None:
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
    slug = models.SlugField(max_length=50, unique=True, verbose_name="Слаг")

    class Meta:
        verbose_name = "Бренд"
        verbose_name_plural = "Бренды"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Size(models.Model):
    name = models.CharField(max_length=10, verbose_name="Размер")
    order = models.PositiveSmallIntegerField(
        default=0, db_index=True, verbose_name="Порядок"
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Размер"
        verbose_name_plural = "Размеры"


class ProductSize(models.Model):
    variant = models.ForeignKey(
        "ProductVariant",
        on_delete=models.CASCADE,
        related_name="sizes",
        verbose_name="Вариант товара",
    )
    size = models.ForeignKey(Size, on_delete=models.CASCADE, verbose_name="Размер")
    # stock = models.PositiveIntegerField(default=0, verbose_name="Остаток")
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Цена",
    )
    discount_percent = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Скидка %",
    )

    final_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Итоговая цена",
        null=True,
        blank=True,
        editable=False,  # Скрываем из админки (пользователь не должен менять её вручную)
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
        return ""

    class Meta:
        ordering = ["size"]
        unique_together = ["variant", "size"]
        verbose_name = "Размер и цена"
        verbose_name_plural = (
            "Размеры и цены (Сохраните товар для автоматического проставления размеров)"
        )
        indexes = [models.Index(fields=["variant", "is_active"])]


class ProductImage(models.Model):
    variant = models.ForeignKey(
        "ProductVariant",
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Вариант товара",
    )
    image = ThumbnailerImageField(
        upload_to=UploadToPath("products", use_category_subdir=True),
        validators=[ImageValidator(min_width=500, min_height=600, max_mb=1.5)],
        verbose_name="Фото (min 500x600, max 1,5Мб)",
    )
    is_main = models.BooleanField(default=False, verbose_name="Главное фото")
    alt = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Alt текст",
        help_text="Оставьте пустым для автогенерации",
    )
    position = models.PositiveIntegerField(
        default=0, db_index=True, verbose_name="Порядок"
    )

    def save(self, *args, **kwargs):
        # Базовая сортировка
        # Если позиция не задана (новое фото)
        if self.position is None:
            last_image = (
                ProductImage.objects.filter(variant=self.variant)
                .order_by("-position")
                .first()
            )
            self.position = (last_image.position + 1) if last_image else 0

        # Конвертация загружаемого изображения в WebP и генерация миниатюр
        # 1. Обновляем продукт перед обработкой пути, чтобы подтянуть сгенерированный слаг
        # Если это новое изображение (еще нет PK) и у него привязан вариант
        if not self.pk and self.variant_id:
            try:
                self.product = self.variant.product
            except AttributeError:
                # На случай, если связь в моделях называется иначе
                pass

        # 2. Обработка загружаемого изображения
        is_new = prepare_image_for_save(
            self, "image", folder="products/", use_category_subdir=True
        )

        super().save(*args, **kwargs)

        # 3. Запускаем генерацию миниатюр
        if is_new:
            generate_all_aliases(self.image, include_global=True)

    def __str__(self):
        if self.is_main:
            return f"ГЛАВНОЕ ФОТО ({self.variant.full_name})"
        return f"Фото №{self.position + 1} ({self.variant.full_name})"

    class Meta:
        verbose_name = "Фото"
        verbose_name_plural = "Фото"
        # ordering = ["-is_main"]
        ordering = ["position"]


class Color(models.Model):
    name = models.CharField(verbose_name="Название цвета", max_length=50, unique=True)
    slug = models.SlugField(verbose_name="Слаг", max_length=50, unique=True)
    hex_code = models.CharField(
        verbose_name="Основной HEX-код",
        max_length=7,
        help_text="Обязательно для однотонных и двухцветных",
        default="#000000",
    )
    hex_code_2 = models.CharField(
        verbose_name="Дополнительный HEX",
        max_length=7,
        blank=True,
        help_text="Заполните для двухцветных товаров (например, черно-белый)",
    )
    texture = models.ImageField(
        verbose_name="Текстура (Паттерн)",
        upload_to="color_textures/",
        blank=True,
        help_text="Загрузите картинку (например, камуфляж). Если загружена, HEX-коды игнорируются.",
    )
    order = models.PositiveSmallIntegerField(
        default=0, db_index=True, verbose_name="Порядок"
    )

    class Meta:
        verbose_name = "Цвет"
        verbose_name_plural = "Цвета"
        ordering = ["order"]

    def __str__(self):
        return self.name


class Product(models.Model):
    class GenderChoices(models.TextChoices):
        MALE = "M", "Мужской"
        FEMALE = "F", "Женский"
        UNISEX = "U", "Унисекс"

    class SeasonChoices(models.TextChoices):
        WINTER = "WINTER", "Зима"
        SUMMER = "SUMMER", "Лето"
        AUTUMN_SPRING = "AUTUMN_SPRING", "Демисезон"
        ALL_SEASON = "ALL_SEASON", "Всесезонный"

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="Категория",
    )
    brand = models.ForeignKey(
        Brand, on_delete=models.PROTECT, related_name="products", verbose_name="Бренд"
    )
    available_sizes = models.ManyToManyField(
        Size,
        blank=True,
        verbose_name="Размеры",
        help_text="Этот перечень размеров будет автоматически добавляться при создании новых вариантов товара.",
    )
    name = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Вид товара",
        help_text="Оставьте пустым, для автогенерации из категории",
    )
    model_name = models.CharField(max_length=50, verbose_name="Модель")
    gender = models.CharField(
        max_length=1, choices=GenderChoices.choices, verbose_name="Пол"
    )
    season = models.CharField(
        max_length=20, choices=SeasonChoices.choices, verbose_name="Сезон"
    )
    description = models.TextField(blank=True, verbose_name="Общее описание")

    # Слаг базовой модели (например: sneakers-nike-air-force-1)
    slug = models.SlugField(
        max_length=150,
        blank=True,
        unique=True,
        verbose_name="Слаг базовой модели",
        help_text="Генерируется автоматически на основе вида, бренда и модели",
    )
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    @property
    def type_name(self):
        return self.name or self.category.singular_name or self.category.name

    @property
    def full_name(self):
        return f"{self.type_name} {self.brand.name} {self.model_name}".strip()

    def save(self, *args, **kwargs):
        # 1. Генерация слага, если он пуст
        if not self.slug:
            self.slug = generate_unique_slug(
                self, base_field="full_name", scope_field="category"
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name

    class Meta:
        # ordering = ["brand", "model_name"]
        verbose_name = "Базовый товар"
        verbose_name_plural = "Базовые товары"
        indexes = [models.Index(fields=["is_active", "category"])]


class ProductVariant(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants",
        verbose_name="Базовая модель",
    )
    color = models.ForeignKey(
        Color, on_delete=models.PROTECT, related_name="variants", verbose_name="Цвет"
    )
    article = models.CharField(
        max_length=50,
        verbose_name="Артикул",
        unique=True,
        blank=True,
        help_text="Генерируется автоматически '[BRAND(2)][GENDER(1)][CAT_ID(3)]-[PROD_ID(5)][RAND(3)]'",
    )

    # Слаг для конкретного цвета (например: sneakers-nike-air-force-1-krasnyj)
    slug = models.SlugField(
        max_length=200,
        blank=True,
        unique=True,
        verbose_name="Слаг варианта",
        help_text="Генерируется автоматически на основе вида, бренда, модели и цвета",
    )
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    @property
    def full_name(self):
        return f"{self.product.full_name} ({self.color.name})"

    @property
    def get_main_image_obj(self):
        # .all() возвращает кэшированный список, если был prefetch_related
        images_list = self.images.all()
        # Работаем со списком в памяти Python
        return images_list[0] if images_list else None

    def save(self, *args, **kwargs):
        # 1. Генерация слага, если он пуст (ID не нужен)
        if not self.slug:
            # Собираем слаг из базового товара и слага цвета
            self.slug = f"{self.product.slug}-{self.color.slug}"

        # Проверяем, создается ли объект впервые
        is_new = self.pk is None

        # 2. ОСНОВНОЕ СОХРАНЕНИЕ
        # Здесь Django создаст запись (если новый) или обновит (если существующий)
        # После этого шага у нас 100% есть self.pk (даже у новых товаров)
        super().save(*args, **kwargs)

        # 3. Генерация (если пуст)/обновление артикула
        if not self.article:
            from .utils import generate_unique_article

            self.article = generate_unique_article(self)
            # Используем update_fields, чтобы обновить только артикул.
            # Используем .update() вместо super().save(update_fields=...)
            # Это быстрее и НЕ вызывает повторные сигналы или методы save().
            self.__class__.objects.filter(pk=self.pk).update(article=self.article)

        # 3. Автогенерация перечня размеров
        # Если это новый вариант и у родителя задана размерная сетка
        if is_new and self.product.available_sizes.exists():
            # Генерируем размеры
            sizes_to_create = [
                ProductSize(variant=self, size=size, is_active=False)
                for size in self.product.available_sizes.all()
            ]
            # Массово сохраняем в базу одним запросом
            ProductSize.objects.bulk_create(sizes_to_create)

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "Ассортимент"
        verbose_name_plural = "Ассортимент"
        unique_together = ["product", "color"]  # Исключает создание двух цветовых дублей
        indexes = [models.Index(fields=["product", "is_active"])]


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


class ProductMaterial(models.Model):
    variant = models.OneToOneField(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="composition",
        verbose_name="Вариант товара",
    )

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

    class Meta:
        verbose_name = "Состав"
        verbose_name_plural = "Состав"


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Пользователь",
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="favorited_by",
        verbose_name="Вариант товара",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Добавлено")

    class Meta:
        # Это гарантирует, что пользователь не сможет добавить один и тот же товар в избранное дважды
        unique_together = ("user", "variant")
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"

    def __str__(self):
        return f"{self.user} -> {self.variant.full_name}"


class SliderBanner(models.Model):
    title = models.CharField(max_length=100, verbose_name="Заголовок")
    image = ThumbnailerImageField(
        upload_to=UploadToPath("banner", "slide"),
        validators=[ImageValidator(min_width=1540, min_height=630, max_mb=2.0)],
        verbose_name="Изображение (min 1540x630, max 2Мб)",
    )
    link = models.URLField(blank=True, verbose_name="Ссылка")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    def save(self, *args, **kwargs):
        # Конвертация загружаемого изображения в WebP и генерация миниатюр
        # 1. Обработка загружаемого изображения
        is_new = prepare_image_for_save(
            self, "image", folder="banner", prefix="slide", quality=100
        )

        super().save(*args, **kwargs)

        # 2. Генерируем миниатюры
        if is_new:
            generate_all_aliases(self.image, include_global=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Баннер"
        verbose_name_plural = "Баннеры"
        ordering = ["order", "-id"]
