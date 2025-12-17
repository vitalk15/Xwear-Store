from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.text import slugify
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


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
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистации")
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
            self.slug = self.generate_unique_slug()
        super().save(*args, **kwargs)

    def generate_unique_slug(self):
        slug_base = slugify(self.name, allow_unicode=False)
        slug = slug_base

        # Проверяем уникальность в рамках родителя, если совпадает - добавляем число
        counter = 1
        while (
            self.__class__.objects.filter(slug=slug, parent=self.parent)
            .exclude(pk=self.pk)
            .exists()
        ):
            slug = f"{slug_base}-{counter}"
            counter += 1

        return slug

    def __str__(self):
        return self.name

    class MPTTMeta:
        order_insertion_by = ["name"]

    class Meta:
        unique_together = [
            "parent",
            "slug",
        ]  # уникальная комбинация род.категории и слага
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
