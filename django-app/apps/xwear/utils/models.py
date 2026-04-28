# СЛАГИ, АРТИКУЛА, ПРОВЕРКА ИЗМЕНЕНИЙ В БД

import string
import random
from pytils.translit import slugify


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


# Универсальная проверка: изменился ли файл в поле модели
def is_field_changed(instance, field_name):
    if not instance.pk:
        return True
    try:
        old_obj = instance.__class__.objects.get(pk=instance.pk)
        return getattr(old_obj, field_name) != getattr(instance, field_name)
    except instance.__class__.DoesNotExist:
        return True
