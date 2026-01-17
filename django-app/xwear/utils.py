import os
from uuid import uuid4
from django.utils.text import slugify
from django.utils.html import format_html
from easy_thumbnails.files import get_thumbnailer


# изменение имени изображения товара
def rename_image_prod(instance, filename):
    upload_to = "products"
    ext = filename.split(".")[-1]

    # 1. Если у объекта уже есть ID (редактирование), используем его
    if instance.pk:
        new_filename = f"prod_{instance.pk}.{ext}"
    # 2. Если ID еще нет (новый товар), используем UUID
    else:
        new_filename = f"prod_{uuid4().hex[:8]}.{ext}"

    return os.path.join(upload_to, new_filename)


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


# Генерация превью в админке
def get_admin_thumb(image_field, size=(100, 90)):
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
