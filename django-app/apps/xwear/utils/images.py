# ОБРАБОТКА ИЗОБРАЖЕНИЙ

import os
from uuid import uuid4
from io import BytesIO
from PIL import Image
from django.db import transaction
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import UploadedFile
from django.utils.deconstruct import deconstructible
from django.utils.html import format_html
from easy_thumbnails.files import get_thumbnailer
from easy_thumbnails.alias import aliases as et_aliases
from .models import is_field_changed


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
    # 1. Базовая проверка на наличие файла
    if not image_field or not hasattr(image_field, "url") or not image_field.name:
        return "Нет фото"

    # 2. ПРОВЕРКА НА "НОВЫЙ" ФАЙЛ
    # Если файл только что загружен (UploadedFile) или его еще нет на диске
    is_uploaded = isinstance(image_field.file, UploadedFile)

    # Проверяем физическое наличие файла, чтобы не пугать ошибками
    try:
        exists = image_field.storage.exists(image_field.name)
    except Exception:
        exists = False

    if is_uploaded or not exists:
        return format_html(
            '<span style="color: #666; font-size: 11px; font-style: italic;">'
            "⚠️ Оформите правильно данные</span>"
        )

    try:
        # 2. Определяем настройки миниатюры (алиас)
        target = f"{image_field.instance._meta.app_label}.{image_field.instance._meta.object_name}.{image_field.field.name}"
        options = et_aliases.get(alias, target=target)
        # options = et_aliases.get("admin_preview", target="xwear.ProductImage.image")

        if not options:
            # Дефолтные настройки, если алиас не найден
            options = {"size": (80, 80), "crop": "smart", "quality": 90}

        # Генерируем миниатюру через метод поля ThumbnailerImageField (get_thumbnail)
        # thumb = image_field.get_thumbnail(options)

        thumbnailer = get_thumbnailer(image_field)
        thumb = thumbnailer.get_thumbnail(options)
        width, height = options.get("size", (80, 80))

        html = format_html(
            '<div class="admin-preview-wrapper" style="margin-bottom: 5px;">'
            '<a href="{2}" target="_blank" style="text-decoration: none;">'
            '<div style="width: {1}px; height: auto; display: flex; align-items: center; '
            "justify-content: center; background: #f8f9fa; border-radius: 4px; overflow: hidden; "
            'box-shadow: 0 1px 3px rgba(0,0,0,0.1); border: 1px solid #ddd;">'
            '<img src="{0}" style="flex-shrink: 0; max-width: 100%; max-height: 100%; object-fit: contain;" />'
            "</div>"
            "</a>",
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

    except Exception:
        # В продакшене логировать
        # return f"Ошибка генерации превью: {e}"
        return format_html(
            '<span title="Ошибка обработки изображения">⚠️ Ошибка превью</span>'
        )


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
