import os
import string
import random
from uuid import uuid4
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from django.utils.deconstruct import deconstructible

# from django.utils.text import slugify
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

        # 1. Если передан префикс - используем его
        if self.prefix:
            base_name = self.prefix
        # 2. Если префикса нет, определяем базовое имя товара (слаг)
        elif hasattr(instance, "product") and instance.product:
            product = instance.product

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
            options = {"size": (80, 70), "crop": "smart", "quality": 85}

        # Генерируем миниатюру через метод поля ThumbnailerImageField (get_thumbnail)
        thumb = image_field.get_thumbnail(options)
        width, height = options.get("size", (80, 70))

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
    from .models import Product, ProductSize, Brand

    sidebar_data_qs = Product.objects.filter(category__in=categories, is_active=True)

    price_stats = sidebar_data_qs.aggregate(
        min_p=Min("sizes__final_price", filter=Q(sizes__is_active=True)),
        max_p=Max("sizes__final_price", filter=Q(sizes__is_active=True)),
    )

    brands = Brand.objects.filter(
        products__category__in=categories, products__is_active=True
    ).distinct()

    sizes = (
        ProductSize.objects.filter(
            product__category__in=categories, product__is_active=True, is_active=True
        )
        .values_list("size__name", flat=True)
        .distinct()
        .order_by("size__name")
    )

    return {
        "brands": brands,
        "sizes": list(sizes),
        "price_range": {
            "min": price_stats["min_p"] or 0,
            "max": price_stats["max_p"] or 0,
        },
    }


# Возвращает отфильтрованный QuerySet товаров для фильтров сайдбара
def get_filtered_products(categories, query_params):
    from .models import Product, ProductSize

    # Используем одну аннотацию для всех вычислений
    queryset = (
        Product.objects.filter(category__in=categories, is_active=True)
        .annotate(
            # Находим минимальную цену среди размеров для этого товара
            annotated_min_final_price=Min(
                "sizes__final_price", filter=Q(sizes__is_active=True)
            )
        )
        .select_related("brand", "category")
        .prefetch_related(
            "images",
            Prefetch(
                "sizes",
                queryset=ProductSize.objects.filter(is_active=True).select_related(
                    "size"
                ),
            ),
        )
        .order_by("-created_at")
    )

    # Применяем фильтры
    # 1. Современный подход через запятую (в URL: ?brands=nike,adidas)
    brands_param = query_params.get("brands")
    if brands_param:
        # brand_slugs = brands_param.split(",")
        # Убираем лишние пробелы и пустые элементы на всякий случай
        brand_slugs = [s.strip() for s in brands_param.split(",") if s.strip()]
        queryset = queryset.filter(brand__slug__in=brand_slugs)

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

    min_p = query_params.get("min_price")
    max_p = query_params.get("max_price")
    if min_p:
        queryset = queryset.filter(annotated_min_final_price__gte=min_p)
    if max_p:
        queryset = queryset.filter(annotated_min_final_price__lte=max_p)

    return queryset


# Показ рекомендаций
def get_similar_products(product, limit=8):
    """
    Возвращает товары из той же подкатегории в ценовом диапазоне +/- 20%.
    Если находит меньше 4, добивает список другими товарами из этой категории.
    """
    from .models import Product

    # 1. Находим минимальную финальную цену текущего товара
    # Используем агрегацию
    current_min_data = product.sizes.filter(is_active=True).aggregate(
        min_p=Min("final_price")
    )

    current_min_price = current_min_data["min_p"]

    if current_min_price is None:
        return []

    # 2. Расчет диапазона +/- 20%
    min_range = float(current_min_price) * 0.8
    max_range = float(current_min_price) * 1.2

    # 3. Запрос с аннотацией - ищем похожие: та же категория + цена в диапазоне + активен + не сам этот товар. Ограничиваем количество и обязательно добавляем prefetch_related('sizes'), так как сериализатор вызывает obj.sizes.all()
    similar_qs = (
        Product.objects.filter(is_active=True, category=product.category)
        .annotate(
            # Аннотируем каждый товар в базе его минимальной ценой
            annotated_min_final_price=Min(
                "sizes__final_price", filter=Q(sizes__is_active=True)
            )
        )
        .filter(annotated_min_final_price__range=(min_range, max_range))
        .exclude(id=product.id)
        .select_related("brand", "category")
        .prefetch_related("sizes")
        .order_by("?")[:limit]
    )

    # Выполняем запрос и превращаем в список (чтобы посчитать количество)
    similar_products = list(similar_qs)

    # Добор
    if len(similar_products) < 4:
        # Собираем ID тех товаров, что уже лежат в similar_products,
        # плюс ID самого текущего товара, чтобы не показать его в рекомендациях
        exclude_ids = [product.id] + [p.id for p in similar_products]

        # Сколько еще товаров нам нужно добрать до лимита?
        needed_count = limit - len(similar_products)

        # Резервный запрос: та же категория, но БЕЗ фильтра по цене
        fallback_qs = (
            Product.objects.filter(is_active=True, category=product.category)
            .exclude(id__in=exclude_ids)
            .annotate(
                # ВАЖНО: Мы все равно делаем аннотацию цены, чтобы наш
                # ProductListSerializer не упал и корректно отдал min_price на фронтенд!
                annotated_min_final_price=Min(
                    "sizes__final_price", filter=Q(sizes__is_active=True)
                )
            )
            .select_related("brand", "category")
            .prefetch_related("sizes")
            .order_by("?")[:needed_count]
        )

        # Добавляем найденные "резервные" товары к основному списку
        similar_products.extend(list(fallback_qs))

    return similar_products


# генерация артикула для товара
def generate_unique_article(product):
    """
    Генерирует артикул: [BRAND(2)][GENDER(1)][CAT(3)]-[PROD(5)][RAND(3)]
    Пример: ADM025-00142X8Z
    """

    # 1. Используем category_id вместо category.id.
    # Это спасает от лишнего запроса к БД, если объект категории еще не загружен в память.
    # (Мы уже сделали поле category обязательным в базе, но оставим проверку для надежности)
    if not product.category_id:
        return None

    try:
        # 2. Код бренда (2 символа)
        brand_code = product.brand.slug[:2].upper() if product.brand else "NB"

        # 3. Код пола (1 символ)
        # Берем значение из choices (M, F, U)
        gender_code = product.gender if product.gender else "U"

        # 4. ID категории с дополнением до 3 знаков
        cat_id = str(product.category_id).zfill(3)

        # 5. ID товара с дополнением до 5 знаков
        # Если товар еще не сохранен (id=None), ставим нули
        prod_id = str(product.id).zfill(5) if product.id else "00000"

        # 6. Случайный хвост (3 символа) для защиты от перебора и уникальности
        random_suffix = "".join(
            random.choices(string.ascii_uppercase + string.digits, k=3)
        )

        return f"{brand_code}{gender_code}{cat_id}-{prod_id}{random_suffix}"

    except Exception as e:
        print(f"Ошибка при генерации артикула: {e}")
        return None


# синхронизация изображений товара (главная, порядок) и генерация alt-текста в админке
@transaction.atomic
def sync_product_images(product, manual_selected_id=None):
    # 1. Получаем все фото, отсортированные по позиции
    images = list(product.images.all().order_by("position", "id"))
    if not images:
        return

    # 2. Шаблон для проверки alt-текста: "Название товара - фото"
    base_pattern = f"{product.full_name} - фото"

    # 3. Генерация alt-текста
    def get_smart_alt(instance, target_number):
        current_alt = instance.alt or ""
        # Если Alt пустой ИЛИ он совпадает со стандартным шаблоном
        if not current_alt or current_alt.startswith(base_pattern):
            return f"{base_pattern} {target_number}"
        # В противном случае оставляем то, что ввел пользователь
        return current_alt

    # 4. Определяем главное фото
    if manual_selected_id:
        # ПРИОРИТЕТ 1: Если пользователь явно кликнул на галочку (передано из admin.py)
        target_main = product.images.filter(pk=manual_selected_id).first()
    else:
        # ПРИОРИТЕТ 2: В остальных случаях (включая перетаскивание)
        # главным становится тот, кто фактически первый в списке
        target_main = images[0]

    if not target_main:
        target_main = images[0]

    # 5. Синхронизируем флаги
    product.images.all().update(is_main=False)
    product.images.filter(pk=target_main.pk).update(
        is_main=True, position=0, alt=get_smart_alt(target_main, 1)
    )

    # 6. Выравниваем позиции остальных (чтобы не было двух нулевых)
    others = product.images.exclude(pk=target_main.pk).order_by("position", "id")
    for i, img in enumerate(others, start=2):
        product.images.filter(pk=img.pk).update(position=i - 1, alt=get_smart_alt(img, i))


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
