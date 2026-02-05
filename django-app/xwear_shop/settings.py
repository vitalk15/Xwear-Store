from pathlib import Path
from datetime import timedelta
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS", default="localhost", cast=lambda v: [s.strip() for s in v.split(",")]
)


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "xwear.apps.XwearConfig",
    "accounts",
    "orders",
    "easy_thumbnails",
    "django_cleanup",
    "mptt",
    "django_mptt_admin",
    "rest_framework",
    "corsheaders",
    "drf_spectacular",
    # 'rest_framework_simplejwt',  # НЕ обязательно для базового JWT
    # 'rest_framework_simplejwt.token_blacklist',  # Только для blacklist
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "xwear_shop.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "xwear_shop.wsgi.application"

AUTH_USER_MODEL = "accounts.User"

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": {
        # "ENGINE": "django.db.backends.sqlite3",
        # "NAME": BASE_DIR / "db.sqlite3",
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST"),
        "PORT": config("DB_PORT"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "ru"

TIME_ZONE = "Europe/Minsk"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Медиафайлы и миниатюры
# -----------------------

MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "media/"

THUMBNAIL_BASEDIR = "thumbnails"
THUMBNAIL_EXTENSION = "webp"
THUMBNAIL_CACHE_DIMENSIONS = True
THUMBNAIL_ALIASES = {
    "xwear.ProductImage.image": {
        "product_small": {  # для превью в корзине или мини-карточек
            "size": (105, 95),
            "crop": "smart",
            "quality": 75,
        },
        "product_medium": {  # для плитки товаров
            "size": (320, 320),
            "crop": "smart",
            "quality": 80,
        },
        "product_large": {  # для детальной страницы товара
            "size": (670, 490),
            "crop": "smart",
            "quality": 90,
        },
    },
    "xwear.SliderBanner.image": {
        "slider_main": {
            "size": (1540, 630),
            "crop": "smart",
            "quality": 90,
        },
    },
}

THUMBNAIL_WIDGET_OPTIONS = {
    "size": (100, 90),  # Размер превью в админке
    "crop": "smart",  # Умная обрезка (фокус на деталях)
    "quality": 75,
    "format": "WEBP",
}


# Настройки доступа с других доменов (CORS)
# ------------------------------------------

# разрешает/запрещает запросы из всех источников (True только в режиме разработки!!!)
CORS_ALLOW_ALL_ORIGINS = config("CORS_ALLOW_ALL_ORIGINS", default=False, cast=bool)

# источники, доступ с которых разрешён (указать, если CORS_ALLOW_ALL_ORIGINS = False),
# для локального Vite:
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:5173",
#     "http://127.0.0.1:5173",
# ]
CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default="http://localhost:5173,http://127.0.0.1:5173",
    cast=lambda v: [s.strip() for s in v.split(",") if s.strip()],
)

# разрешает/запрещает использование cookies и заголовков для управления учётными данными,
# если True, то д.б. CORS_ALLOW_ALL_ORIGINS: False
CORS_ALLOW_CREDENTIALS = config("CORS_ALLOW_CREDENTIALS", default=True, cast=bool)

# источники, доступ с которых разрешён для cross-origin запросов с cookie (защита от CSRF-атак),
# нужно указывать, если CORS_ALLOW_CREDENTIALS: True;
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS

# заголовки CORS будут отправляться только на все REST-эндпоинты (не всегда указывается)
CORS_URLS_REGEX = r"^/api/.*$"


# CSRF настройки для JWT + cookie
# -------------------------------

# если True, csrftoken в cookies отправляется только по HTTPS (для Production)
CSRF_COOKIE_SECURE = config("HTTPS_ONLY", default=True, cast=bool)
# если False, JavaScript читает csrftoken из cookie для X-CSRFToken заголовка
CSRF_COOKIE_HTTPONLY = False
# csrftoken в cookies отправляется только с запросов с нашего домена ('Strict' — максимальная безопасность (для Production), 'Lax' — позволяет переходы по ссылкам (Dev), 'None' — для кросс-доменных (редко))
CSRF_COOKIE_SAMESITE = config("SAMESITE")


# JWT для API авторизации
# -----------------------

SIMPLE_JWT = {
    # задаём время жизни для access-token (он храниться в LocalStorage)
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=10),
    # задаём время жизни для refresh-token (он храниться в Cookie)
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    # задаём имя для refresh-token в cookie
    "AUTH_COOKIE": "refresh_token",
    # если True, refresh-token в cookie не доступен JS
    "AUTH_COOKIE_HTTP_ONLY": True,
    # если True, refresh-token в cookie отправляется только по HTTPS (для Production)
    "AUTH_COOKIE_SECURE": config("HTTPS_ONLY", default=True, cast=bool),
    # refresh-token в cookies отправляется только с запросов с нашего домена ('Strict' — максимальная безопасность (для Production), 'Lax' — позволяет GET-переходы (Dev), 'None' — для кросс-доменных (редко))
    "AUTH_COOKIE_SAMESITE": config("SAMESITE"),
    # если True - включаем обновление refresh-токена после истечения срока действия, а также при logout и последующем login - в этом случае старый refresh-токен продолжает работать до истечения срока вместе с новым (если False - refresh-token неизменный)
    "ROTATE_REFRESH_TOKENS": True,
    # если True - старые или после logout refresh-токены аннулируются и попадают в blacklist (храниться в БД)
    # "BLACKLIST_AFTER_ROTATION": True,
    # Обновление поля last_login в БД при входе пользователя (False - по умолчанию)
    "UPDATE_LAST_LOGIN": True,
    # алгоритм шифрования (HS256 - по-умолчанию)
    "ALGORITHM": "HS256",
    # ключ подписи (SECRET_KEY - по умолчанию)
    "SIGNING_KEY": SECRET_KEY,
    # ключ верификации ("" - для алгоритма шифрования HMAC)
    "VERIFYING_KEY": "",
    # тип заголовка авторизации, формат - Authorization: Bearer <token> ("Bearer" - по умочанию)
    "AUTH_HEADER_TYPES": ("Bearer",),
    # имя заголовка авторизации ("HTTP_AUTHORIZATION" - по умолчанию)
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    # поле из модели пользователя, которое будет включено в создаваемые токены для идентификации.
    "USER_ID_FIELD": "id",
    # параметр для хранения идентификаторов пользователей в сгенерированных токенах
    "USER_ID_CLAIM": "user_id",
    # Кастомный сериализатор, определяет, какие данные попадут в payload токена при login/register (по умолчанию {user_id, exp, iat}). Добавляем token_version
    "TOKEN_OBTAIN_SERIALIZER": "accounts.serializers.CustomTokenObtainPairSerializer",
    # Проверка payload при каждом API запросе (кроме user_id проверка token_version), извлекает пользователя из токена.
    "JWT_GET_USER_ID_FROM_PAYLOAD_HANDLER": "accounts.utils.jwt_get_user_id_from_payload_handler",
}


# Конфигурация DRF
# ----------------

REST_FRAMEWORK = {
    # использование JWT-аутентификации
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    # возвращает только JSON, отключает HTML-формы и браузерные страницы
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    # "spectacular"
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    # Пагинация
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 10,
}


# Настройка SPECTACULAR (SWAGGER)
# -------------------------------

SPECTACULAR_SETTINGS = {
    "TITLE": "XWEAR API",
    "DESCRIPTION": "Online clothing store",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}


# Логирование
# -----------
# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "handlers": {
#         "file": {
#             "level": "INFO",
#             "class": "logging.FileHandler",
#             "filename": "/var/log/django/shop.log",
#         },
#     },
#     "loggers": {
#         "django": {
#             "handlers": ["file"],
#             "level": "INFO",
#             "propagate": True,
#         },
#     },
# }

# Срок жизни reset-токена
PASSWORD_RESET_TIMEOUT = 3600  # 1 час

# Адрес для reset-ссылки
RESET_URL = config("RESET_URL", default="http://localhost:5173")

# Email для разработки (консоль)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Email (SMTP)
# -------------
# EMAIL_BACKEND = config(
#     "EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
# )
# EMAIL_HOST = config("EMAIL_HOST", default="localhost")
# EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
# EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
# EMAIL_HOST_USER = config("EMAIL_HOST_USER")
# EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="xwear@example.by")


# Security (production)
# ---------------------
# SECURE_BROWSER_XSS_FILTER = True
# SECURE_CONTENT_TYPE_NOSNIFF = True
# X_FRAME_OPTIONS = "DENY"
# SECURE_HSTS_SECONDS = 31536000  # 1 год
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True
# SECURE_REDIRECT_EXEMPT = []
# SECURE_SSL_REDIRECT = config("HTTPS_ONLY", default=True, cast=bool)
