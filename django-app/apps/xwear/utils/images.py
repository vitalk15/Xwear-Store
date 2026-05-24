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
from django.templatetags.static import static
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


def generate_banner_html(obj, image_url, max_width, is_list=False):
    """Генератор HTML для баннера с адаптивностью через cqw"""

    if not image_url:
        return format_html('<span style="color: #999;">Нет изображения</span>')

    # Конфигурация стилей для карточки админки (распор контейнера)
    extra_styles = ""
    if not is_list:
        extra_styles = "min-width: 100%; width: calc(100vw - 350px);"

    # --- МАППИНГ СЕТКИ ПОЗИЦИОНИРОВАНИЯ (3х3) ---
    # Переводим grid_layout в flex-инструкции для абсолютного контейнера
    grid_maps = {
        "top_left": {
            "vertical": "flex-start",
            "horizontal": "flex-start",
            "text_align": "left",
        },
        "top_center": {
            "vertical": "flex-start",
            "horizontal": "center",
            "text_align": "center",
        },
        "top_right": {
            "vertical": "flex-start",
            "horizontal": "flex-end",
            "text_align": "right",
        },
        "center_left": {
            "vertical": "center",
            "horizontal": "flex-start",
            "text_align": "left",
        },
        "center_center": {
            "vertical": "center",
            "horizontal": "center",
            "text_align": "center",
        },
        "center_right": {
            "vertical": "center",
            "horizontal": "flex-end",
            "text_align": "right",
        },
        "bottom_left": {
            "vertical": "flex-end",
            "horizontal": "flex-start",
            "text_align": "left",
        },
        "bottom_center": {
            "vertical": "flex-end",
            "horizontal": "center",
            "text_align": "center",
        },
        "bottom_right": {
            "vertical": "flex-end",
            "horizontal": "flex-end",
            "text_align": "right",
        },
    }

    # Получаем настройки сетки (токены по умолчанию на случай отсутствия полей)
    layout_settings = grid_maps.get(
        getattr(obj, "grid_layout", "center_left"), grid_maps["center_left"]
    )

    # Стили для главного Flex-контейнера, покрывающего картинку
    flex_css = f"""
        justify-content: {layout_settings['vertical']};
        align-items: {layout_settings['horizontal']};
        padding: 4cqw;
    """

    # Динамические настройки из параметров модели
    font_size_title_val = getattr(obj, "font_size_title", "4.5cqw")
    font_size_link_val = getattr(obj, "font_size_link", "1.8cqw")
    content_width_val = getattr(obj, "content_width", 50)

    # Определяем цвет текста
    text_color = "#171819" if obj.text_color == "dark" else "#fff"
    # Легкая тень для читаемости даже без затемнения фона
    shadow_size = "0.1em"
    text_shadow = (
        f"0 {shadow_size} {shadow_size} rgba(0,0,0,0.5)"
        if obj.text_color == "light"
        else "none"
    )

    # Получаем заголовок и список ссылок
    title = obj.title or ""
    links = obj.links if isinstance(obj.links, list) else []

    # Выравнивание кнопок (ссылок) внутри контейнера кнопок
    btn_justify_map = {"left": "flex-start", "center": "center", "right": "flex-end"}
    btn_justify = btn_justify_map.get(layout_settings["text_align"], "flex-start")

    # Абсолютные пути к веб-шрифтам
    black_woff2 = static("admin/fonts/RFDewiExpanded-Black.woff2")
    black_woff = static("admin/fonts/RFDewiExpanded-Black.woff")

    ultrabold_woff2 = static("admin/fonts/RFDewiExpanded-Ultrabold.woff2")
    ultrabold_woff = static("admin/fonts/RFDewiExpanded-Ultrabold.woff")

    # Генерируем HTML для кнопок
    buttons_list = []
    for link in links:
        btn_title = link.get("title", "Кнопка")
        btn_style = link.get("style", "primary")

        # Базовые стили кнопки (размеры через cqw)
        style_parts = [
            "display: block",
            "margin: 0.4em",
            "padding: 1em 1.2em",
            "border-radius: 0.35em",
            "font-family: 'RF Dewi Expanded', 'Helvetica Neue', sans-serif !important",
            f"font-size: {font_size_link_val} !important",
            "font-weight: 800 !important",
        ]

        if btn_style == "primary":
            style_parts.extend(
                [
                    "background: #222222",
                    "color: #ffffff",
                ]
            )
        elif btn_style == "secondary":
            style_parts.extend(
                [
                    "background: #ffffff",
                    "color: #222222",
                ]
            )
        elif btn_style == "outline":
            style_parts.extend(
                [
                    "background: transparent",
                    f"color: {text_color}",
                ]
            )
        else:  # link
            style_parts.extend(
                [
                    "background: transparent",
                    f"color: {text_color}",
                    f"text-shadow: {text_shadow}",
                    "padding: 0.5em 0",
                ]
            )

        style_string = "; ".join(style_parts)
        buttons_list.append(f'<div style="{style_string}">{btn_title}</div>')

    buttons_html = "".join(buttons_list)

    # Итоговая сборка HTML
    # container-type: inline-size — это ключ, заставляющий cqw работать внутри этого div.
    html = f"""
        <style>
            /* Регистрируем шрифты */
            @font-face {{{{
                font-family: 'RF Dewi Expanded';
                src: url('{black_woff2}') format('woff2'),
                     url('{black_woff}') format('woff');
                font-weight: 900;
                font-style: normal;
                font-display: swap;
            }}}}
            @font-face {{{{
                font-family: 'RF Dewi Expanded';
                src: url('{ultrabold_woff2}') format('woff2'),
                     url('{ultrabold_woff}') format('woff');
                font-weight: 800;
                font-style: normal;
                font-display: swap;
            }}}}
        </style>

        <div style="
            display: block;
            {extra_styles}
            max-width: {max_width}; 
            position: relative; 
            container-type: inline-size; 
            border: 1px solid #ccc; 
            border-radius: 4px; 
            overflow: hidden;
            line-height: 1.2;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        ">
            <img src="{image_url}" style="
                display: block; 
                width: 100%; 
                height: auto;" />
            <div style="
                position: absolute; top: 0; left: 0; right: 0; bottom: 0; 
                display: flex; flex-direction: column; 
                {flex_css}
                pointer-events: none;
            ">
                <div style="
                    max-width: {content_width_val}%; 
                    text-align: {layout_settings['text_align']};
                    pointer-events: auto;
                ">
                    <h2 style="
                        background: none;
                        margin: 0 0 0.5em 0 !important;
                        padding: 0 !important;
                        color: {text_color}; 
                        text-shadow: {text_shadow};  
                        font-size: {font_size_title_val} !important; 
                        font-family: 'RF Dewi Expanded', 'Helvetica Neue', sans-serif !important;
                        font-weight: 900 !important;
                        text-align: inherit;
                        word-wrap: break-word;
                    ">{title}</h2>
                    <div style="
                        display: flex;
                        flex-direction: column;
                        flex-wrap: wrap;
                        justify-content: {btn_justify};
                        align-items: {btn_justify}; 
                    ">{buttons_html}</div>
                </div>
            </div>
        </div>
    """
    return format_html(html)
