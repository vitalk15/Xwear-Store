# from django.utils.text import slugify
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from easy_thumbnails.fields import ThumbnailerImageField
from .utils import rename_image_prod, generate_unique_slug


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Требуется email")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name="Эл.почта")
    first_name = models.CharField(max_length=150, blank=True, verbose_name="Имя")
    last_name = models.CharField(max_length=150, blank=True, verbose_name="Фамилия")
    phone = models.CharField(max_length=30, blank=True, verbose_name="Номер телефона")
    # для инвалидации старых токенов (вместо blacklist)
    token_version = models.PositiveIntegerField(default=1)

    is_active = models.BooleanField(default=True, verbose_name="Активный")
    is_staff = models.BooleanField(default=False, verbose_name="Персонал")
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")
    last_login = models.DateTimeField(
        null=True, blank=True, verbose_name="Последний вход"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    # инвалидация старых токенов (вместо blacklist)
    def increment_token_version(self):
        self.token_version += 1
        self.save(update_fields=["token_version"])

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["date_joined"]


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

    # def save(self, *args, **kwargs):
    #     if not self.slug:
    #         self.slug = self.generate_unique_slug()
    #     super().save(*args, **kwargs)

    # def generate_unique_slug(self):
    #     slug_base = slugify(self.name, allow_unicode=False)
    #     slug = slug_base

    #     # Проверяем уникальность в рамках родителя, если совпадает - добавляем число
    #     counter = 1
    #     while (
    #         self.__class__.objects.filter(slug=slug, parent=self.parent)
    #         .exclude(pk=self.pk)
    #         .exists()
    #     ):
    #         slug = f"{slug_base}-{counter}"
    #         counter += 1

    #     return slug

    def __str__(self):
        return self.name

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


class Size(models.Model):
    name = models.CharField(max_length=10, verbose_name="Размер")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="Порядок")

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Размер"
        verbose_name_plural = "Размеры"

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(
        "Product", on_delete=models.CASCADE, related_name="images", verbose_name="Товар"
    )
    # image = models.ImageField(upload_to=rename_image_prod, verbose_name="Фото")
    image = ThumbnailerImageField(upload_to=rename_image_prod, verbose_name="Фото")
    is_main = models.BooleanField(default=False, verbose_name="Главное фото")
    alt = models.CharField(max_length=200, blank=True, verbose_name="Alt текст")

    class Meta:
        verbose_name = "Фото товара"
        verbose_name_plural = "Фото товаров"

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


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
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
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, scope_field="category")
        super().save(*args, **kwargs)

    # def save(self, *args, **kwargs):
    #     if not self.slug:
    #         self.slug = self.generate_unique_slug()
    #     super().save(*args, **kwargs)

    # def generate_unique_slug(self):
    #     slug_base = slugify(self.name, allow_unicode=False)
    #     slug = slug_base

    #     # Уникальность в рамках категории
    #     counter = 1
    #     while (
    #         self.__class__.objects.filter(slug=slug, category=self.category)
    #         .exclude(pk=self.pk)
    #         .exists()
    #     ):
    #         slug = f"{slug_base}-{counter}"
    #         counter += 1

    #     return slug

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


class ProductSize(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="sizes", verbose_name="Товар"
    )
    size = models.ForeignKey(Size, on_delete=models.CASCADE, verbose_name="Размер")
    # stock = models.PositiveIntegerField(default=0, verbose_name="Остаток")
    price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Цена")
    is_active = models.BooleanField(default=True, verbose_name="В наличии")

    class Meta:
        unique_together = ["product", "size"]
        verbose_name = "Размер/цена товара"
        verbose_name_plural = "Размеры/цены товаров"
