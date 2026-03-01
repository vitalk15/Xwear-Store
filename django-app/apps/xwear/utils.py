import os
from uuid import uuid4
from django.utils.deconstruct import deconstructible
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from django.utils.text import slugify
from django.utils.html import format_html
from django.db.models import Prefetch, Min, Max, Q
from easy_thumbnails.files import get_thumbnailer


# преобразование имени изображения с указанием префикса и папки сохранения
# деконструируемый класс (используем вместо фабрики функции, так как выполнялся сброс миграций и при создании новых есть проблема с wrapper)
@deconstructible
class UploadToPath:
    def __init__(self, folder, prefix):
        self.folder = folder
        self.prefix = prefix

    def __call__(self, instance, filename):
        """
        Этот метод заменяет нашу старую функцию wrapper.
        Django вызывает его, когда нужно получить путь.
        """
        ext = filename.split(".")[-1]

        # Если объект сохранен - используем ID, иначе UUID
        if instance.pk:
            identifier = instance.pk
        else:
            identifier = uuid4().hex[:8]

        new_filename = f"{self.prefix}_{identifier}.{ext}"
        return os.path.join(self.folder, new_filename)


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


# Генератор уникальных слагов
def generate_unique_slug(model_instance, base_field="name", scope_field=None):
    """
    Args:
        model_instance: Экземпляр модели (Category/Product)
        base_field: Поле для slugify ('name')
        scope_field: Поле для уникальности ('parent', 'category')
    """
    slug_base = slugify(getattr(model_instance, base_field), allow_unicode=False)
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
def get_thumbnail_data(image_field, aliases, request):
    """
    Универсальная функция для получения словаря миниатюр.
    Возвращает URL, ширину и высоту для каждого алиаса.
    """
    if not image_field:
        return None

    thumbnailer = get_thumbnailer(image_field)
    data = {}

    for key, alias_name in aliases.items():
        try:
            thumb = thumbnailer.get_thumbnail({"alias": alias_name})
            # Если request есть - строим полный путь, если нет - отдаем относительный
            url = request.build_absolute_uri(thumb.url) if request else thumb.url

            data[key] = {
                "url": url,
                "width": thumb.width,
                "height": thumb.height,
            }
        except Exception:
            continue

    return data


# Генерация превью в админке
def get_admin_thumb(image_field, size=(100, 100)):
    if not image_field:
        return "Нет фото"
    try:
        # options = {"size": size, "crop": "smart", "quality": 85}
        thumbnailer = get_thumbnailer(image_field)
        thumb_url = thumbnailer.get_thumbnail().url
        return format_html(
            '<img src="{}" style="width: {}px; height: {}px; object-fit: cover; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.2);" />',
            thumb_url,
            size[0],
            size[1],
        )
    except Exception:
        return "Ошибка генерации превью"


# валидация загружаемых изображений для баннера
def validate_banner_image(image):
    width, height = get_image_dimensions(image)
    min_width = 1540
    min_height = 630
    if width < min_width or height < min_height:
        raise ValidationError(
            f"Размер слишком мал ({width}x{height})."
            f"Для слайдера требуются изображения не менее {min_width}x{min_height} px."
        )


# Собирает данные для сайдбара (бренды, размеры, диапазон цен),
# слайдер цены и список брендов в фильтре должны показывать все возможности категории
def get_category_sidebar_filters(categories):
    from .models import Product, ProductSize, Brand

    sidebar_data_qs = Product.objects.filter(category__in=categories, is_active=True)

    price_stats = sidebar_data_qs.annotate(
        p=Min("sizes__final_price", filter=Q(sizes__is_active=True))
    ).aggregate(min_p=Min("p"), max_p=Max("p"))

    brands = Brand.objects.filter(products__category__in=categories).distinct()
    sizes = (
        ProductSize.objects.filter(product__category__in=categories, is_active=True)
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


# Возвращает отфильтрованный QuerySet товаров для сайдбара
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

    # Применяем фильтры (из URL)
    brand_slugs = query_params.getlist("brands[]")
    if brand_slugs:
        queryset = queryset.filter(brand__slug__in=brand_slugs)

    size_names = query_params.getlist("sizes[]")
    if size_names:
        # Если фильтруем по размерам, нужен distinct, так как у товара много размеров
        queryset = queryset.filter(
            sizes__size__name__in=size_names, sizes__is_active=True
        ).distinct()

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
