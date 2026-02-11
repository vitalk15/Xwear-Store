from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.validators import RegexValidator, EmailValidator
from django.db import models


# Валидатор номеров телефонов для Беларуси (+375XXXXXXXXX)
phone_regex = RegexValidator(
    regex=r"^\+375(25|29|33|44)\d{7}$",
    message="Номер должен быть в формате +375XXXXXXXXX (МТС, А1, life:).",
)


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
    email = models.EmailField(
        unique=True, validators=[EmailValidator()], verbose_name="Эл.почта"
    )

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


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    first_name = models.CharField(max_length=150, blank=True, verbose_name="Имя")
    last_name = models.CharField(max_length=150, blank=True, verbose_name="Фамилия")
    phone = models.CharField(
        max_length=13,
        validators=[phone_regex],
        blank=True,
        null=True,
        unique=True,
        verbose_name="Номер телефона",
    )

    def __str__(self):
        return f"Профиль {self.user.email}"

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"


class City(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название города")
    is_active = models.BooleanField(default=True, verbose_name="Доступен для доставки")
    delivery_cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Стоимость доставки"
    )

    class Meta:
        verbose_name = "Город"
        verbose_name_plural = "Города"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Address(models.Model):
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="addresses",
        verbose_name="Профиль",
    )
    city = models.ForeignKey(
        City,
        on_delete=models.PROTECT,  # Не даем удалить город, если на него ссылаются адреса
        related_name="addresses",
        verbose_name="Город",
    )
    street = models.CharField(max_length=100, verbose_name="Улица")
    house = models.CharField(max_length=20, verbose_name="Номер дома")
    # Квартира может отсутствовать (частный дом), поэтому null=True
    apartment = models.CharField(
        max_length=10, blank=True, null=True, verbose_name="Квартира"
    )

    # Флаг "Адрес по умолчанию" для быстрого заказа
    is_default = models.BooleanField(default=False, verbose_name="Основной адрес")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Адрес доставки"
        verbose_name_plural = "Адреса доставки"
        ordering = ["-is_default", "-created_at"]  # Сначала основной, потом новые

    def __str__(self):
        addr = f"г. {self.city} | ул. {self.street}, {self.house}"
        if self.apartment:
            addr += f", кв. {self.apartment}"
        return addr

    def save(self, *args, **kwargs):
        """
        Если этот адрес помечается как default=True,
        снимаем флаг is_default со всех остальных адресов этого профиля.
        """
        if self.is_default:
            Address.objects.filter(profile=self.profile, is_default=True).update(
                is_default=False
            )
        super().save(*args, **kwargs)
