import os
from uuid import uuid4
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from django.utils.text import slugify
from django.utils.html import format_html
from easy_thumbnails.files import get_thumbnailer


# преобразование имени изображения с указанием префикса и папки сохранения
# приём "фабрика функций"
def get_upload_path(folder, prefix):
    def wrapper(instance, filename):
        ext = filename.split(".")[-1]

        # Используем ID если объект уже сохранен, иначе UUID
        if instance.pk:
            identifier = instance.pk
        else:
            identifier = uuid4().hex[:8]

        new_filename = f"{prefix}_{identifier}.{ext}"
        return os.path.join(folder, new_filename)

    return wrapper


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
