import os
import string
import random
from uuid import uuid4
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from django.utils.deconstruct import deconstructible
from django.utils.html import format_html
from django.db.models import Prefetch, Min, Max, Q
from django.db import transaction

# from easy_thumbnails.files import get_thumbnailer
from easy_thumbnails.alias import aliases as et_aliases
from pytils.translit import slugify


# переименование изображения с указанием папки сохранения
# деконструируемый класс (используем вместо фабрики функции, так как выполнялся сброс миграций и при создании новых есть проблема с wrapper)
@deconstructible
class UploadToPath:

    def __init__(self, folder, prefix=None, use_category_subdir=False):
        self.folder = folder
        self.prefix = prefix
        self.use_category_subdir = use_category_subdir

    def __call__(self, instance, filename):
        """
        Этот метод заменяет нашу старую функцию wrapper.
        Django вызывает его, когда нужно получить путь.
        """
        # ext = filename.split(".")[-1]
        ext = "webp"  # Мы всегда конвертируем в webp
        subfolder = ""

        # Пытаемся получить продукт напрямую (если он есть)
        product = getattr(instance, "product", None)

        # Если напрямую не нашли, идем через вариант (наша новая структура)
        if not product and getattr(instance, "variant", None):
            product = instance.variant.product

        # 1. Если передан префикс - используем его
        if self.prefix:
            base_name = self.prefix
        # 2. Если префикса нет, определяем базовое имя товара (слаг)
        elif product:
            # Берем готовый слаг товара
            base_name = getattr(product, "slug", "product")

            # Если включена опция вложенных подпапок
            if self.use_category_subdir:
                # Достаем слаг категории
                category = getattr(product, "category", None)
                category_slug = (
                    category.slug
                    if category and getattr(category, "slug", None)
                    else "no-category"
                )
                # if category and hasattr(category, "slug"):
                #     subfolder = category.slug
                # else:
                #     subfolder = "no-category"

                # Достаем слаг бренда
                brand = getattr(product, "brand", None)
                brand_slug = (
                    brand.slug if brand and getattr(brand, "slug", None) else "no-brand"
                )

                # Формируем путь внутри основной папки: category-slug/brand-slug
                subfolder = os.path.join(category_slug, brand_slug)

        else:
            base_name = "file"

        # Уникальный идентификатор для защиты от перезаписи файлов с одинаковыми именами
        identifier = instance.pk if instance.pk else uuid4().hex[:5]
        new_filename = f"{base_name}_{identifier}.{ext}"

        # Формируем итоговый путь: media/folder/category-slug/brand-slug/file.webp
        return os.path.join(self.folder, subfolder, new_filename)


# преобразование имени изображения с указанием префикса и папки сохранения
# приём "фабрика функций"
# def get_upload_path(folder, prefix):
#     def wrapper(instance, filename):
#         ext = filename.split(".")[-1]

#         # Используем ID если объект уже сохранен, иначе UUID
#         if instance.pk:
#             identifier = instance.pk
#         else:
#             identifier = uuid4().hex[:8]

#         new_filename = f"{prefix}_{identifier}.{ext}"
#         return os.path.join(folder, new_filename)

#     return wrapper


# Конвертирование изображений в WebP
def convert_to_webp(image_field, quality=100):
    if not image_field:
        return

    img = Image.open(image_field)

    # Конвертируем в RGB для сохранения в WebP (убирает проблемы с прозрачностью)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    output = BytesIO()
    # Сохраняем с максимальным качеством для оригиналов
    img.save(output, format="WEBP", quality=quality, method=6)
    output.seek(0)

    return ContentFile(output.read())


def clean_thumbnail_namer(
    thumbnailer, prepared_options, source_filename, thumbnail_extension, **kwargs
):
    """
    Создает чистое имя миниатюры без двойных расширений.
    """
    # Отрезаем оригинальное расширение (например, '.webp' или '.jpg')
    base_name, _ = os.path.splitext(source_filename)

    # Собираем параметры миниатюры в строку через подчеркивание
    options_string = "_".join(prepared_options)

    # Склеиваем всё вместе с новым расширением
    return f"{base_name}_{options_string}.{thumbnail_extension}"


# Генератор уникальных слагов
def generate_unique_slug(model_instance, base_field="name", scope_field=None):
    """
    Args:
        model_instance: Экземпляр модели (Category/Product)
        base_field: Поле для slugify ('name')
        scope_field: Поле для уникальности ('parent', 'category')
    """
    # slug_base = slugify(getattr(model_instance, base_field), allow_unicode=False)
    slug_base = slugify(getattr(model_instance, base_field))
    slug = slug_base

    counter = 1
    Model = model_instance.__class__

    while True:
        qs = Model.objects.filter(slug=slug)

        # Уникальность в scope (parent/category)
        if scope_field:
            scope_value = getattr(model_instance, scope_field)
            qs = qs.filter(**{scope_field: scope_value})

        qs = qs.exclude(pk=model_instance.pk)

        if not qs.exists():
            return slug

        slug = f"{slug_base}-{counter}"
        counter += 1


# получение данных миниатюр
# def get_thumbnail_data(image_field, aliases, request):
#     """
#     Универсальная функция для получения словаря миниатюр.
#     Возвращает URL, ширину и высоту для каждого алиаса.
#     """
#     if not image_field:
#         return None

#     thumbnailer = get_thumbnailer(image_field)
#     data = {}

#     for key, alias_name in aliases.items():
#         try:
#             thumb = thumbnailer.get_thumbnail({"alias": alias_name})
#             # Если request есть - строим полный путь, если нет - отдаем относительный
#             url = request.build_absolute_uri(thumb.url) if request else thumb.url

#             data[key] = {
#                 "url": url,
#                 "width": thumb.width,
#                 "height": thumb.height,
#             }
#         except Exception:
#             continue

#     return data


# Универсальная функция для получения словаря миниатюр
def get_thumbnail_data(image_field, aliases, request=None):
    if not image_field:
        return None

    data = {}

    # Динамически определяем target (например: 'xwear.ProductImage.image')
    # Это нужно, чтобы et_aliases.get() знал, в каком блоке настроек искать алиас
    target_path = ""
    if hasattr(image_field, "instance") and hasattr(image_field, "field"):
        app_label = image_field.instance._meta.app_label
        model_name = image_field.instance._meta.object_name
        field_name = image_field.field.name
        target_path = f"{app_label}.{model_name}.{field_name}"

    for key, alias_name in aliases.items():
        try:
            # 2. Правильно извлекаем словарь настроек по имени алиаса
            options = et_aliases.get(alias_name, target=target_path)

            # Если настройки не найдены в словаре — пропускаем
            if not options:
                continue

            # 3. Передаем словарь опций
            thumb = image_field.get_thumbnail(options)

            url = request.build_absolute_uri(thumb.url) if request else thumb.url

            data[key] = {
                "url": url,
                "width": thumb.width,
                "height": thumb.height,
            }
        except Exception as e:
            return f"Ошибка получения данных превью: {e}"
            # continue

    return data


# Генерация превью в админке и показ информации о фото
def get_admin_thumb(image_field, alias="admin_preview", show_info=False):
    if not image_field or not hasattr(image_field, "url"):
        return "Нет фото"
    try:
        # Автоматически определяем target для алиаса на основе модели
        target = f"{image_field.instance._meta.app_label}.{image_field.instance._meta.object_name}.{image_field.field.name}"
        options = et_aliases.get(alias, target=target)
        # options = et_aliases.get("admin_preview", target="xwear.ProductImage.image")

        if not options:
            # Дефолтные настройки, если алиас не найден
            options = {"size": (80, 80), "crop": "smart", "quality": 90}

        # Генерируем миниатюру через метод поля ThumbnailerImageField (get_thumbnail)
        thumb = image_field.get_thumbnail(options)
        width, height = options.get("size", (80, 80))

        html = format_html(
            '<div class="admin-preview-wrapper" style="margin-bottom: 5px;">'
            '<a href="{2}" target="_blank" style="text-decoration: none;">'
            '<div style="width: {1}px; height: auto; display: flex; align-items: center; '
            "justify-content: center; background: #f8f9fa; border-radius: 4px; overflow: hidden; "
            'box-shadow: 0 1px 3px rgba(0,0,0,0.1); border: 1px solid #ddd;">'
            '<img src="{0}" style="flex-shrink: 0; max-width: 100%; max-height: 100%; object-fit: contain;" />'
            "</div>",
            thumb.url,
            width,
            image_field.url,
        )

        if show_info:
            # Получаем размер файла и разрешение
            try:
                size_kb = round(image_field.size / 1024, 2)
                size_str = (
                    f"{size_kb} KB" if size_kb < 1000 else f"{round(size_kb/1024, 2)} MB"
                )
                info_html = format_html(
                    '<div style="font-size: 10px; color: #666; margin-top: 3px; line-height: 1.2;">'
                    "📏 {0}x{1} px<br>💾 {2}"
                    "</div>",
                    image_field.width,
                    image_field.height,
                    size_str,
                )
                html += info_html
            except:
                pass

        return html + format_html("</div>")

    except Exception as e:
        # В продакшене логировать
        return f"Ошибка генерации превью: {e}"


# Собирает данные для сайдбара (бренды, размеры, диапазон цен),
# слайдер цены и список брендов в фильтре должны показывать все возможности категории
def get_category_sidebar_filters(categories):
    from .models import ProductVariant, ProductSize, Brand, Color

    # Базовый кверисет — только активные варианты активных базовых товаров
    sidebar_data_qs = ProductVariant.objects.filter(
        product__category__in=categories, is_active=True, product__is_active=True
    )

    # 1. Цены, доступные в этой категории
    price_stats = sidebar_data_qs.aggregate(
        min_p=Min("sizes__final_price", filter=Q(sizes__is_active=True)),
        max_p=Max("sizes__final_price", filter=Q(sizes__is_active=True)),
    )

    # 2. Бренды, доступные в этой категории
    brands = Brand.objects.filter(
        products__variants__is_active=True,
        products__category__in=categories,
        products__is_active=True,
    ).distinct()

    # 3. Размеры, доступные в этой категории
    sizes = (
        ProductSize.objects.filter(
            variant__product__category__in=categories,
            variant__is_active=True,
            variant__product__is_active=True,
            is_active=True,
        )
        .values_list("size__name", flat=True)
        .distinct()
        # .order_by("size__name")
    )

    # 4. Цвета, доступные в этой категории
    colors = Color.objects.filter(
        variants__product__category__in=categories,
        variants__is_active=True,
        variants__product__is_active=True,
    ).distinct()

    return {
        "brands": brands,
        "sizes": list(sizes),
        "colors": colors,
        "price_range": {
            "min": price_stats["min_p"] or 0,
            "max": price_stats["max_p"] or 0,
        },
    }


# Возвращает отфильтрованный QuerySet товаров для фильтров сайдбара
def get_filtered_products(categories, query_params):
    from .models import ProductVariant, ProductSize

    queryset = (
        ProductVariant.objects.filter(
            product__category__in=categories, is_active=True, product__is_active=True
        )
        .annotate(
            # Находим минимальную цену среди размеров для этого товара
            annotated_min_final_price=Min(
                "sizes__final_price", filter=Q(sizes__is_active=True)
            )
        )
        .select_related("product__brand", "product__category", "color")
        .prefetch_related(
            "images",
            "product__variants__color",  # Соседние цвета для кружочков
            Prefetch(
                "sizes",
                queryset=ProductSize.objects.filter(is_active=True).select_related(
                    "size"
                ),
            ),
        )
        # .order_by("-product__created_at", "-id") # сортируем по дате создания родителя
        .order_by("-created_at", "-id")  # сортируем по дате создания варианта
    )

    # Применяем фильтры
    # 1. Современный подход через запятую (в URL: ?brands=nike,adidas)
    # Фильтр по брендам
    brands_param = query_params.get("brands")
    if brands_param:
        # brand_slugs = brands_param.split(",")
        # Убираем лишние пробелы и пустые элементы на всякий случай
        brand_slugs = [s.strip() for s in brands_param.split(",") if s.strip()]
        queryset = queryset.filter(product__brand__slug__in=brand_slugs)

    # Фильтр по цветам
    colors_param = query_params.get("colors")
    if colors_param:
        color_slugs = [s.strip() for s in colors_param.split(",") if s.strip()]
        queryset = queryset.filter(color__slug__in=color_slugs)

    # Фильтр по размерам
    sizes_param = query_params.get("sizes")
    if sizes_param:
        # size_names = sizes_param.split(",")
        size_names = [s.strip() for s in sizes_param.split(",") if s.strip()]
        # Если фильтруем по размерам, нужен distinct, так как у товара много размеров
        queryset = queryset.filter(
            sizes__size__name__in=size_names, sizes__is_active=True
        ).distinct()

    # Применяем фильтры
    # 2. Стандартный подход (в URL: ?brands=nike&brands=adidas)
    # brand_slugs = query_params.getlist("brands")
    # if brand_slugs:
    #     queryset = queryset.filter(brand__slug__in=brand_slugs)

    # size_names = query_params.getlist("sizes")
    # if size_names:
    #     # Если фильтруем по размерам, нужен distinct, так как у товара много размеров
    #     queryset = queryset.filter(
    #         sizes__size__name__in=size_names, sizes__is_active=True
    #     ).distinct()

    # Фильтр по цене
    min_p = query_params.get("min_price")
    max_p = query_params.get("max_price")
    if min_p:
        queryset = queryset.filter(annotated_min_final_price__gte=min_p)
    if max_p:
        queryset = queryset.filter(annotated_min_final_price__lte=max_p)

    return queryset


# Показ рекомендаций
def get_similar_products(variant, limit=8):
    """
    Возвращает товары из той же подкатегории в ценовом диапазоне +/- 20% рандомно.
    В блок рекомендаций всегда попадает только один цвет от одной базовой модели.
    """
    from .models import ProductVariant, ProductSize

    # 1. Получаем минимальную финальную цену текущего варианта для расчета диапазона
    # (Берем из аннотации, если она была во вьюхе, или считаем)
    current_min_price = getattr(variant, "annotated_min_final_price", None)
    if current_min_price is None:
        price_data = variant.sizes.filter(is_active=True).aggregate(
            min_p=Min("final_price")
        )
        current_min_price = price_data["min_p"]

    if current_min_price is None:
        return []

    # 2. Расчет диапазона +/- 20%
    min_range = float(current_min_price) * 0.8
    max_range = float(current_min_price) * 1.2

    # 3. Ищем подходящие варианты (исключаем всю семью текущего базового товара)
    candidates = (
        ProductVariant.objects.filter(
            is_active=True,
            product__is_active=True,
            product__category=variant.product.category,
        )
        .exclude(product_id=variant.product_id)  # Исключаем всю текущую семью
        .annotate(
            # Аннотируем каждый товар в базе его минимальной ценой
            annotated_min_p=Min("sizes__final_price", filter=Q(sizes__is_active=True))
        )
        .filter(annotated_min_p__range=(min_range, max_range))
    )

    # 4. Дедупликация: берем только один вариант от каждого базового товара
    candidate_data = list(candidates.values("id", "product_id"))
    seen_products = set()
    unique_variant_ids = []

    for v in candidate_data:
        if v["product_id"] not in seen_products:
            seen_products.add(v["product_id"])
            unique_variant_ids.append(v["id"])

    # 5. Если товаров мало, добираем без учета цены (но тоже уникальные модели)
    if len(unique_variant_ids) < 4:
        extra_candidates = (
            ProductVariant.objects.filter(
                is_active=True,
                product__is_active=True,
                product__category=variant.product.category,
            )
            .exclude(product_id=variant.product_id)
            .exclude(id__in=unique_variant_ids)
        )

        extra_data = list(extra_candidates.values("id", "product_id"))
        for v in extra_data:
            if v["product_id"] not in seen_products:
                seen_products.add(v["product_id"])
                unique_variant_ids.append(v["id"])

    # 6. Выбираем случайные ID, в количестве = limit
    sample_size = min(len(unique_variant_ids), limit)
    random_ids = random.sample(unique_variant_ids, sample_size)

    # 7. Финальный запрос с полной подгрузкой данных
    return (
        ProductVariant.objects.filter(id__in=random_ids)
        .annotate(
            annotated_min_final_price=Min(
                "sizes__final_price", filter=Q(sizes__is_active=True)
            )
        )
        .select_related("product__brand", "product__category", "color")
        .prefetch_related(
            "images",
            "product__variants__color",
            Prefetch(
                "sizes",
                queryset=ProductSize.objects.filter(is_active=True).select_related(
                    "size"
                ),
            ),
        )
    )


# генерация артикула для варианта товара
def generate_unique_article(variant):
    """
    Генерирует артикул: [BRAND(2)][GENDER(1)][CAT(3)]-[VAR(5)][RAND(3)]
    Пример: ADM025-00142X8Z
    """
    # 1. Проверяем наличие связи с базовым товаром и категорией.
    # Обращаемся к родительскому товару через variant.product
    # Используем category_id вместо category.id - это спасает от лишнего запроса к БД, если объект категории еще не загружен в память.
    if not variant.product_id or not variant.product.category_id:
        return None

    try:
        base_product = variant.product

        # 2. Код бренда (2 символа)
        brand_code = base_product.brand.slug[:2].upper() if base_product.brand else "NB"

        # 3. Код пола (1 символ)
        # Берем значение из choices (M, F, U)
        gender_code = base_product.gender if base_product.gender else "U"

        # 4. ID категории с дополнением до 3 знаков
        cat_id = str(base_product.category_id).zfill(3)

        # 5. ID варианта товара с дополнением до 5 знаков
        # Если вариант еще не сохранен (id=None), ставим нули
        var_id = str(variant.id).zfill(5) if variant.id else "00000"

        # 6. Случайный хвост (3 символа) для защиты от перебора и уникальности
        random_suffix = "".join(
            random.choices(string.ascii_uppercase + string.digits, k=3)
        )

        return f"{brand_code}{gender_code}{cat_id}-{var_id}{random_suffix}"

    except Exception as e:
        print(f"Ошибка при генерации артикула: {e}")
        return None


# синхронизация изображений варианта товара (главная, порядок) и генерация alt-текста в админке
# @transaction.atomic
# def sync_product_images(variant, manual_selected_id=None):
#     # 1. Получаем все фото, отсортированные по позиции
#     images = list(variant.images.all().order_by("position", "id"))
#     if not images:
#         return

#     # 2. Шаблон для проверки alt-текста: "Название товара - фото"
#     base_pattern = f"{variant.full_name} - фото"

#     # 3. Генерация alt-текста
#     def get_smart_alt(instance, target_number):
#         current_alt = instance.alt or ""
#         # Если Alt пустой ИЛИ он совпадает со стандартным шаблоном
#         if not current_alt or current_alt.startswith(base_pattern):
#             return f"{base_pattern} {target_number}"
#         # В противном случае оставляем то, что ввел пользователь
#         return current_alt

#     # 4. Определяем главное фото
#     if manual_selected_id:
#         # ПРИОРИТЕТ 1: Если пользователь явно кликнул на галочку (передано из admin.py)
#         target_main = variant.images.filter(pk=manual_selected_id).first()
#     else:
#         # ПРИОРИТЕТ 2: В остальных случаях (включая перетаскивание)
#         # главным становится тот, кто фактически первый в списке
#         target_main = images[0]

#     if not target_main:
#         target_main = images[0]

#     # 5. Синхронизируем флаги
#     variant.images.all().update(is_main=False)
#     variant.images.filter(pk=target_main.pk).update(
#         is_main=True, position=0, alt=get_smart_alt(target_main, 1)
#     )

#     # 6. Выравниваем позиции остальных (чтобы не было двух нулевых)
#     others = variant.images.exclude(pk=target_main.pk).order_by("position", "id")
#     for i, img in enumerate(others, start=2):
#         variant.images.filter(pk=img.pk).update(position=i - 1, alt=get_smart_alt(img, i))


# синхронизация изображений варианта товара (главная, порядок) и генерация alt-текста в админке
@transaction.atomic
def sync_product_images(variant, manual_selected_id=None):
    """
    Синхронизация изображений варианта товара (главная, порядок)
    и генерация alt-текста в админке.
    """
    # 1. Получаем все фото, отсортированные по позиции
    images = list(variant.images.all().order_by("position", "id"))
    if not images:
        return

    # 2. Шаблон для alt-текста
    base_pattern = f"{variant.full_name} - фото"

    # 3. Генерация alt-текста
    def get_smart_alt(instance, target_number):
        current_alt = instance.alt or ""
        # Если Alt пустой ИЛИ он совпадает со стандартным шаблоном (чтобы пересчитать номера)
        if not current_alt or current_alt.startswith(base_pattern):
            return f"{base_pattern} {target_number}"
        # В противном случае оставляем то, что ввел пользователь
        return current_alt

    # 4. Определяем главное фото.
    if manual_selected_id:
        # ПРИОРИТЕТ 1: Если пользователь явно кликнул на галочку (передано из admin.py)
        target_main = variant.images.filter(pk=manual_selected_id).first()
    else:
        # ПРИОРИТЕТ 2: В остальных случаях (включая перетаскивание)
        # главным становится тот, кто фактически первый в списке
        target_main = images[0]

    if not target_main:
        target_main = images[0]

    # 5. Синхронизируем флаги
    # Сначала сбрасываем у всех
    variant.images.all().update(is_main=False)
    # Затем жестко ставим первому позицию 0 и флаг True
    variant.images.filter(pk=target_main.pk).update(
        is_main=True, position=0, alt=get_smart_alt(target_main, 1)
    )

    # 6. Выравниваем позиции остальных (чтобы не было двух нулевых позиций)
    others = variant.images.exclude(pk=target_main.pk).order_by("position", "id")
    for i, img in enumerate(others, start=2):
        variant.images.filter(pk=img.pk).update(position=i - 1, alt=get_smart_alt(img, i))


# Извлекает лимиты из ImageValidator и добавляет их в data-атрибуты виджета
def add_validator_attrs_to_widget(db_field, formfield):
    if not formfield:
        return formfield

    from .validators import ImageValidator

    # Ищем наш валидатор ImageValidator среди всех валидаторов поля
    for v in db_field.validators:
        if isinstance(v, ImageValidator):
            # Прокидываем значения в атрибуты виджета
            formfield.widget.attrs.update(
                {
                    "data-min-width": v.min_width or 0,
                    "data-min-height": v.min_height or 0,
                    "data-max-mb": v.max_mb or 0,
                }
            )
            break
    return formfield


# Универсальная проверка: изменился ли файл в поле модели
def is_field_changed(instance, field_name):
    if not instance.pk:
        return True
    try:
        old_obj = instance.__class__.objects.get(pk=instance.pk)
        return getattr(old_obj, field_name) != getattr(instance, field_name)
    except instance.__class__.DoesNotExist:
        return True


# Полный цикл подготовки загружаемого изображения: конвертация в WebP и генерация пути.
def prepare_image_for_save(
    instance, field_name, folder, prefix=None, use_category_subdir=False, quality=85
):
    """
    Возвращает True, если файл был обновлен.
    """
    image_field = getattr(instance, field_name)

    # Если файла нет или он не менялся — ничего не делаем
    if not image_field or not is_field_changed(instance, field_name):
        return False

    # 1. Конвертируем в WebP
    webp_content = convert_to_webp(image_field, quality=quality)

    # 2. Формируем путь
    upload_processor = UploadToPath(
        folder, prefix=prefix, use_category_subdir=use_category_subdir
    )
    new_path = upload_processor(instance, image_field.name)

    # 3. Подменяем данные в поле
    image_field.file = webp_content
    image_field.name = new_path

    return True
