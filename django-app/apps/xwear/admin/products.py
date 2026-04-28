# БАЗОВЫЕ ТОВАРЫ, ВАРИАНТЫ

from django.contrib import admin, messages
from django.db import transaction
from django.db.models import (
    Count,
    F,
    Q,
    Min,
    Max,
    OuterRef,
    Subquery,
)
from django.utils.html import format_html
from django.urls import reverse
from admin_auto_filters.filters import AutocompleteFilter
from adminsortable2.admin import SortableAdminBase, SortableInlineAdminMixin
from core.admin import NoAddMixin
from ..forms import (
    ProductAdminForm,
    ProductVariantAdminForm,
    ProductSizeForm,
    ProductSizeFormSet,
    ProductImageFormSet,
)
from ..models import (
    Category,
    Color,
    Product,
    ProductVariant,
    ProductImage,
    ProductSize,
    ProductMaterial,
)
from ..utils import add_validator_attrs_to_widget
from .base import ImagePreviewMixin, MainPreviewMixin


# ==========================================
# 1. ФИЛЬТРЫ
# ==========================================


class CategoryOptimizedFilter(admin.SimpleListFilter):
    title = "Категория"  # Заголовок в сайдбаре
    parameter_name = "category_id"  # Имя параметра в URL

    def lookups(self, request, model_admin):
        # 1. Получаем модель категории через _meta (без прямого импорта)
        CategoryModel = model_admin.model._meta.get_field("category").related_model
        # 2. Находим категории, где есть товары напрямую
        categories_with_products = CategoryModel.objects.filter(products__isnull=False)
        # 3. ОДНИМ запросом получаем их и всех их родителей (цепочки)
        # include_self=True оставит саму категорию в списке
        categories = (
            CategoryModel.objects.get_queryset_ancestors(
                categories_with_products, include_self=True
            )
            .select_related("parent")
            .distinct()
        )
        return [(c.pk, str(c)) for c in categories]

    def queryset(self, request, queryset):
        if self.value():
            selected_node = queryset.model._meta.get_field(
                "category"
            ).related_model.objects.get(pk=self.value())
            # Умная фильтрация: берем всех потомков узла по MPTT-индексам
            return queryset.filter(
                category__tree_id=selected_node.tree_id,
                category__lft__gte=selected_node.lft,
                category__lft__lte=selected_node.rght,
            )
        return queryset


class VariantCategoryOptimizedFilter(admin.SimpleListFilter):
    title = "Категория товара"
    parameter_name = "category_id"

    def lookups(self, request, model_admin):
        # 1. Добираемся до модели категории через модель варианта -> продукт -> категория
        # ProductVariant._meta.get_field("product").related_model -> это Product
        ProductModel = model_admin.model._meta.get_field("product").related_model
        CategoryModel = ProductModel._meta.get_field("category").related_model

        # 2. Находим категории, в которых есть товары, у которых есть варианты
        # Это исключит пустые категории из списка в фильтре
        categories_with_variants = CategoryModel.objects.filter(
            products__variants__isnull=False
        ).distinct()

        # 3. Получаем всю цепочку предков для этих категорий (для MPTT)
        categories = (
            CategoryModel.objects.get_queryset_ancestors(
                categories_with_variants, include_self=True
            )
            .select_related("parent")
            .distinct()
        )
        return [(c.pk, str(c)) for c in categories]

    def queryset(self, request, queryset):
        if self.value():
            # Получаем выбранный узел категории
            ProductModel = queryset.model._meta.get_field("product").related_model
            CategoryModel = ProductModel._meta.get_field("category").related_model

            try:
                selected_node = CategoryModel.objects.get(pk=self.value())
                # Фильтруем ВАРИАНТЫ через связь с продуктом
                return queryset.filter(
                    product__category__tree_id=selected_node.tree_id,
                    product__category__lft__gte=selected_node.lft,
                    product__category__lft__lte=selected_node.rght,
                )
            except CategoryModel.DoesNotExist:
                return queryset
        return queryset


class ActiveColorFilter(admin.SimpleListFilter):
    title = "Цвет"
    parameter_name = "color"

    def lookups(self, request, model_admin):
        # Получаем только те цвета, у которых есть хотя бы один товар,
        # и убираем дубликаты с помощью distinct()
        colors = Color.objects.filter(variants__isnull=False).distinct()
        result = []
        for c in colors:
            # Базовый стиль
            style = "display:inline-block; width:12px; height:12px; border-radius:50%; border:1px solid #aaa; vertical-align:middle; margin-right:6px;"
            # Логика приоритетов цвета
            if c.texture:
                style += f"background: url({c.texture.url}) center/cover no-repeat;"
            elif c.hex_code and c.hex_code_2:
                style += f"background: linear-gradient(135deg, {c.hex_code} 51%, {c.hex_code_2} 49%);"
            else:
                style += f"background-color: {c.hex_code or '#eee'};"

            # Собираем кружок и название цвета вместе
            display_name = format_html('<span style="{}"></span> {}', style, c.name)
            # Добавляем в итоговый список
            result.append((c.id, display_name))
        return result

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(color_id=self.value())
        return queryset


class DiscountFilter(admin.SimpleListFilter):
    title = "Наличие скидки"
    parameter_name = "has_discount"

    def lookups(self, request, model_admin):
        return (
            ("yes", "Со скидкой"),
            ("no", "Без скидки"),
        )

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(sizes__discount_percent__gt=0).distinct()
        if self.value() == "no":
            return queryset.filter(sizes__discount_percent=0).distinct()


class SizeFilter(AutocompleteFilter):
    title = "Размер"
    field_name = "actual_sizes"


class AvailabilityFilter(admin.SimpleListFilter):
    title = "Наличие размеров"
    parameter_name = "availability"

    def lookups(self, request, model_admin):
        # Определяем варианты для выбора в фильтре
        return (
            ("in_stock", "Есть в наличии"),
            ("full", "Все в наличии"),
            ("out_of_stock", "Нет размеров"),
        )

    def queryset(self, request, queryset):
        # Фильтруем запрос в зависимости от выбранного пункта
        if self.value() == "in_stock":
            # Хотя бы 1 размер активен
            return queryset.filter(active_count__gt=0)
        if self.value() == "out_of_stock":
            # Активных размеров 0
            return queryset.filter(active_count=0)
        if self.value() == "full":
            # Активные равны общему числу (и при этом товар вообще имеет размеры)
            return queryset.filter(active_count=F("total_count"), total_count__gt=0)

        return queryset


# ==========================================
# 2. ИНЛАЙНЫ
# ==========================================


class ProductImageInline(
    ImagePreviewMixin, SortableInlineAdminMixin, admin.TabularInline
):
    model = ProductImage
    formset = ProductImageFormSet
    # extra = 0
    fields = ["image", "is_main", "alt", "image_preview"]
    classes = ["collapse"]

    # добавление пустой строки для внесения данных
    def get_extra(self, request, obj=None, **kwargs):
        # Если у варианта еще нет фото, показываем 1 пустое поле
        # Если фото уже есть - не показываем лишних пустых строк
        if obj and obj.images.exists():
            return 0
        return 1

    def get_readonly_fields(self, request, obj=None):
        # Если у варианта еще нет фото - даём возможность выбрать главное фото чекбоксом
        # Если фото уже есть - поле is_main делаем только для чтения (будет уже работать перетаскивание)
        if obj and obj.images.exists():
            return ["image_preview", "is_main"]
        return ["image_preview"]

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == "image":
            # Прокидываем лимиты ImageValidator в админку (добавляем полю формы "image" data-атрибуты)
            add_validator_attrs_to_widget(db_field, formfield)
        return formfield

    def get_queryset(self, request):
        # Оптимизируем получение картинок внутри инлайна
        return (
            super()
            .get_queryset(request)
            .select_related("variant__product__category", "variant__product__brand")
        )

    class Media:
        js = ("admin/js/image_preview.js",)


class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    form = ProductSizeForm
    formset = ProductSizeFormSet
    extra = 0
    fields = ["size", "price", "discount_percent", "display_final_price", "is_active"]
    # Это делает выбор размера быстрым поиском (требует search_fields в SizeAdmin)
    autocomplete_fields = ["size"]
    readonly_fields = ["display_final_price"]
    classes = ["collapse"]

    @admin.display(description="Итоговая цена")
    def display_final_price(self, obj):
        if obj and obj.pk and obj.final_price:
            return format_html(
                '<strong style="color: #28a745;">{} </strong>', obj.final_price
            )
        return "-"

    def has_add_permission(self, request, obj=None):
        # Разрешаем добавлять новые размеры (вдруг появился нестандартный)
        return True

    def get_queryset(self, request):
        # Оптимизируем запрос, чтобы не тянуть размеры по одному
        return (
            super().get_queryset(request).select_related("size").order_by("size__order")
        )

    class Media:
        js = ("admin/js/product_price_preview.js",)
        css = {"all": ("admin/css/select2.css",)}


class ProductMaterialInline(admin.StackedInline):
    model = ProductMaterial
    can_delete = False
    # Ограничиваем количество, так как это OneToOne
    max_num = 1  # Не больше одного
    min_num = 1  # Обязательно наличие хотя бы одной записи
    validate_min = True  # ВКЛЮЧАЕМ проверку минимального количества
    autocomplete_fields = ["material_outer", "material_inner", "material_sole"]
    classes = ["collapse"]

    class Media:
        # Прячем заголовок h3 внутри инлайна (появляется при StackedInline)
        css = {"all": ("admin/css/hide_inline_header.css",)}


class ProductVariantInline(MainPreviewMixin, admin.TabularInline):
    """Инлайн для отображения вариантов (цветов) внутри базового товара"""

    model = ProductVariant
    # extra = 0
    fields = ("color", "article", "get_main_preview", "is_active")
    readonly_fields = ["get_main_preview", "article"]
    show_change_link = True  # Позволяет быстро перейти в ProductVariantAdmin
    verbose_name = "Вариант товара"
    verbose_name_plural = "Варианты товара (Создается выключенным. Сначала оформите его, а затем активируйте.)"
    classes = ["collapse"]

    # добавление пустой строки для внесения данных
    def get_extra(self, request, obj=None, **kwargs):
        if obj:  # Если объект уже существует в базе (редактирование)
            return 0
        return 1  # Если это создание нового товара

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("color")
            .prefetch_related("images")
        )


# ==========================================
# 3. АДМИН-КЛАССЫ
# ==========================================


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Управление БАЗОВЫМИ товарами (моделями)"""

    form = ProductAdminForm
    inlines = [ProductVariantInline]

    list_display = [
        "get_full_name",
        "gender",
        "season",
        "get_root_category",
        "variants_count",
        "is_active",
    ]
    list_display_links = ["get_full_name"]
    list_filter = ["is_active", "gender", "brand", CategoryOptimizedFilter, "season"]
    search_fields = ["brand__name", "model_name", "name"]
    autocomplete_fields = ["category", "brand"]
    list_editable = ["is_active"]
    readonly_fields = ["slug"]
    filter_horizontal = ["available_sizes"]

    fieldsets = (
        (None, {"fields": ("is_active",)}),
        (
            "Классификация",
            {"fields": (("brand", "model_name"), ("category", "gender"))},
        ),
        (
            "Идентификация (Авто)",
            {"classes": ("collapse",), "fields": ("name", "slug", "regen_slug")},
        ),
        (
            "Описание товара",
            {"classes": ("collapse",), "fields": ("season", "description")},
        ),
        ("Размерная сетка", {"classes": ("collapse",), "fields": ("available_sizes",)}),
        # (None, {"fields": ("is_active",)}),
    )

    # Кол-во показываемых товаров на одной странице пагинации
    list_per_page = 20
    # Заменяет подсчёт количества найденных записей на ссылку "Показать всё" (ускорение загрузки)
    show_full_result_count = False

    @admin.display(description="Базовый товар")
    def get_full_name(self, obj):
        return obj.full_name

    @admin.display(description="Пол")
    def gender_display(self, obj):
        return obj.get_gender_display()

    @admin.display(description="Сезон")
    def season_display(self, obj):
        return obj.get_season_display()

    # @admin.display(description="Категория", ordering="category")
    # def get_short_category(self, obj):
    #     """
    #     Отображает только последнюю часть категории (после разделителя)
    #     """
    #     if obj.category:
    #         full_path = str(obj.category)
    #         return full_path.rsplit(" / ", maxsplit=1)[-1]
    #     return "-"

    @admin.display(description="Группа")
    def get_root_category(self, obj):
        # """
        # Отображает только корневую категорию (Обувь, Одежда и т.д.)
        # Использование метода библиотеки django-mptt, get_root(),
        # делает отдельный SELECT, чтобы найти в базе запись с тем же tree_id и parent_id IS NULL
        # - если текущая категория не является корневой
        # """
        # if obj.category:
        #     # Метод get_root() возвращает самый верхний объект в дереве (level 0)
        #     return obj.category.get_root().name
        # return "-"
        """
        Отображает только корневую категорию (Обувь, Одежда и т.д.)
        Используем подзапрос в аннотации
        """

        # Если категория есть и подзапрос что-то нашел, выводим. Иначе "-"
        return getattr(obj, "root_category_name", None) or "-"

    @admin.display(description="Варианты", ordering="variants_count_annotated")
    def variants_count(self, obj):
        count = obj.variants_count_annotated

        # Если вариантов нет, просто выводим 0 красным цветом
        if count == 0:
            return format_html('<span style="color: #dc3545;">0</span>')

        # Динамически получаем имя приложения и имя связанной модели (ProductVariant через related_name)
        target_model = obj.variants.model
        app_label = target_model._meta.app_label
        model_name = target_model._meta.model_name

        # Формируем URL для списка вариантов с фильтром по ID текущего базового товара
        url = (
            reverse(f"admin:{app_label}_{model_name}_changelist")
            + f"?product__id__exact={obj.id}"
        )

        # Возвращаем ссылку
        return format_html('<a href="{}" style="color: #007bff;">{} ➔</a>', url, count)

    def get_queryset(self, request):
        # Создаем подзапрос: ищем категорию с уровнем 0 и таким же tree_id, как у товара
        root_category_subquery = Category.objects.filter(
            tree_id=OuterRef("category__tree_id"), level=0
        ).values("name")[:1]

        return (
            super()
            .get_queryset(request)
            .select_related("category", "category__parent", "brand")
            .annotate(
                # Добавляем имя корневой категории в SQL запрос
                root_category_name=Subquery(root_category_subquery),
                # Считаем варианты
                variants_count_annotated=Count("variants", distinct=True),
            )
        )

    def save_model(self, request, obj, form, change):
        # 1. Сброс слага при необходимости
        # Если в карточке варианта товара чекбокс перегенерации нажат — очищаем поле прямо перед сохранением
        if form.cleaned_data.get("regen_slug"):
            obj.slug = None
        # 2. Защита от включения товара без вариантов через галочку в списке (changelist)
        if request.resolver_match and "changelist" in request.resolver_match.url_name:
            if obj.is_active and obj.variants.count() == 0:
                obj.is_active = False  # Блокируем активацию
                messages.error(
                    request,
                    f"Товар '{obj}' не активирован: добавьте хотя бы один вариант.",
                )
        # 3. Предупреждение о деактивации вариантов при деактивации базового товара
        # change = True, если мы редактируем существующий товар, а не создаем новый
        if change:
            # Проверяем, изменился ли статус именно сейчас (был True, стал False)
            was_active = form.initial.get("is_active")
            is_active_now = obj.is_active

            # Сообщение появится только в момент самого переключения галочки
            if was_active and not is_active_now:
                messages.warning(
                    request,
                    f"Товар «{obj}» деактивирован. Все связанные с ним варианты также автоматически деактивированы.",
                )

        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        # 1. Сначала даем Django сохранить все инлайны и позиции от Sortable2
        super().save_related(request, form, formsets, change)

        obj = form.instance

        # 2. Авто-отключение товара, если сохранили карточку, а вариантов нет
        if obj.is_active and not obj.variants.exists():
            obj.is_active = False
            # Сохраняем только поле активности, чтобы не триггерить полное обновление
            obj.save(update_fields=["is_active"])

            messages.warning(
                request,
                f"Товар '{obj}' деактивирован, так как у него нет ни одного варианта.",
            )

    class Media:
        js = (
            "admin/js/product_gender_auto.js",
            "admin/js/no_active_product.js",
        )
        css = {
            "all": (
                "admin/css/product_admin.css",
                "admin/css/display_inactive_products.css",
                "admin/css/custom_quill.css",
            )
        }


@admin.register(ProductVariant)
class ProductVariantAdmin(
    NoAddMixin, MainPreviewMixin, SortableAdminBase, admin.ModelAdmin
):
    """
    Управление вариантами товаров.
    """

    form = ProductVariantAdminForm
    inlines = [ProductImageInline, ProductMaterialInline, ProductSizeInline]

    list_display = [
        "article",
        "get_product_name",
        "get_color_display",
        "get_gender",
        "get_season",
        "active_sizes_count",
        "get_price_range",
        "get_main_preview",
        "is_active",
    ]
    list_display_links = ["article"]
    list_filter = [
        "is_active",
        "product__brand",
        "product__gender",
        VariantCategoryOptimizedFilter,
        "product__season",
        ActiveColorFilter,
        DiscountFilter,
        AvailabilityFilter,
        SizeFilter,
    ]
    search_fields = ["article", "product__model_name", "product__brand__name"]
    autocomplete_fields = ["color", "actual_sizes"]
    list_editable = ["is_active"]
    readonly_fields = ["product", "article", "slug"]

    fieldsets = (
        ("Привязка", {"fields": ("product", "color")}),
        ("Идентификация (Авто)", {"fields": ("article", "slug")}),
        ("Опции", {"fields": ("set_discount_all_sizes", "is_active")}),
        (
            "Служебные действия",
            {
                "classes": ("collapse",),
                "description": (
                    '<div style="color: #ba2121; font-weight: bold; margin-bottom: 10px;">'
                    "⚠️ Если вы изменили ВИД, БРЕНД, МОДЕЛЬ или КАТЕГОРИЮ у базового товара:<br>"
                    '1. Отметьте галочки ниже и нажмите "Сохранить".<br>'
                    "2. Чтобы фото назывались правильно и лежали в правильных папках на сервере — удалите старые изображения и загрузите их заново."
                    "</div>"
                ),
                "fields": ("regen_article", "regen_slug"),
            },
        ),
    )

    # Кол-во показываемых товаров на одной странице пагинации
    list_per_page = 10
    # Заменяет подсчёт количества найденных записей на ссылку "Показать всё" (ускорение загрузки)
    show_full_result_count = False
    # Сортировка по дате создания родителя
    ordering = ("-product__created_at", "-id")

    # --- ОТОБРАЖЕНИЕ ДАННЫХ ---

    @admin.display(description="Товар")
    def get_product_name(self, obj):
        if not obj.product:
            return "-"
        # Возвращаем статус базового товара в скрытом теге для JS
        status = "active" if obj.product.is_active else "inactive"
        # Динамически получаем данные для URL
        app_label = obj.product._meta.app_label
        model_name = obj.product._meta.model_name
        # Генерируем URL
        url = reverse(f"admin:{app_label}_{model_name}_change", args=[obj.product.pk])

        return format_html(
            '<a href="{}" target="_blank" text-decoration: none; color: #447e9b;">'
            "{}"
            "</a>"
            '<span class="product-status-data" style="display:none;">{}</span>',
            url,
            obj.product.full_name,
            status,
        )

    @admin.display(description="Сезон")
    def get_season(self, obj):
        return obj.product.get_season_display()

    @admin.display(description="Пол")
    def get_gender(self, obj):
        return obj.product.get_gender_display()

    # @admin.display(description="Группа")
    # def get_root_category(self, obj):
    #     """Отображает корневую категорию (уровень 0) через аннотацию"""
    #     return getattr(obj, "root_category_name", "-") or "-"

    @admin.display(description="Цвет")
    def get_color_display(self, obj):
        if not obj.color:
            return "—"

        # Базовые стили
        style = "display:inline-block; width:16px; height:16px; border-radius:50%; border:1px solid #aaa; vertical-align:middle; cursor: help;"

        # Логика фона
        if obj.color.texture:
            style += f"background-image: url({obj.color.texture.url}); background-size: cover; background-position: center;"
        elif obj.color.hex_code and obj.color.hex_code_2:
            style += f"background: linear-gradient(135deg, {obj.color.hex_code} 51%, {obj.color.hex_code_2} 49%);"
        elif obj.color.hex_code:
            style += f"background-color: {obj.color.hex_code};"

        return format_html('<span title="{}" style="{}"></span>', obj.color.name, style)

    @admin.display(description="Размеры", ordering="active_sizes")
    def active_sizes_count(self, obj):
        # 1.вар - через цикл (не оптимально для большого кол-ва данных)
        # Получаем все размеры один раз (они уже в кеше благодаря prefetch_related)
        # all_sizes = obj.sizes.all()
        # all_count = len(all_sizes)
        # Считаем активные без создания лишних списков в памяти - способ 2
        # active_count = sum(1 for s in all_sizes if s.is_active)

        # Считаем в памяти через список - способ 1 (менее оптимально)
        # active_count = len([s for s in obj.sizes.all() if s.is_active])

        # return f"{active_count} / {all_count}"

        # 2.вар - подсчет на уровне SQL через annotate в get_queryset (работает быстро и поддерживает сортировку в столбце)
        active = obj.active_count
        total = obj.total_count

        # По умолчанию цвет обычный
        text_color = "inherit"
        if active == 0:
            text_color = "#dc3545"
        elif active == total and total > 0:
            text_color = "#28a745"
        elif active < total / 2:
            text_color = "#800000"
        return format_html(
            '<span style="color: {};">{} / {}</span>', text_color, active, total
        )

    @admin.display(description="Цены", ordering="min_price")
    def get_price_range(self, obj):
        # 1 вар. - Через список - не оптимально
        # prices = [s.final_price for s in obj.sizes.all() if s.is_active]
        # if prices:
        #     return f"{min(prices)} - {max(prices)}"
        # return "Цена не задана"

        # 2.вар - подсчет на уровне SQL через annotate в get_queryset (работает быстро и поддерживает сортировку в столбце)
        if obj.min_price is not None:
            # Если мин и макс совпадают, выводим одно число, иначе диапазон
            if obj.min_price == obj.max_price:
                return f"{obj.min_price}"
            return f"{obj.min_price} – {obj.max_price}"
        return format_html('<span style="color: #999;">Нет цен</span>')

    # --- ЛОГИКА И ОПТИМИЗАЦИЯ ---

    # Оптимизация запросов
    def get_queryset(self, request):
        # Подзапрос: ищем в дереве категорию с level=0, у которой tree_id совпадает
        # с tree_id категории связанного товара
        # root_category_subquery = Category.objects.filter(
        #     tree_id=OuterRef("product__category__tree_id"), level=0
        # ).values("name")[:1]
        return (
            super()
            .get_queryset(request)
            .select_related(
                "product", "product__brand", "product__category", "color", "composition"
            )
            .prefetch_related("images")
            .annotate(
                # Прокидываем имя корневой категории в каждый вариант
                # root_category_name=Subquery(root_category_subquery),
                # Считаем общее количество связанных размеров
                total_count=Count("sizes"),
                # Считаем только активные размеры, используя фильтр Q
                active_count=Count("sizes", filter=Q(sizes__is_active=True)),
                # Расчет цен
                min_price=Min("sizes__final_price", filter=Q(sizes__is_active=True)),
                max_price=Max("sizes__final_price", filter=Q(sizes__is_active=True)),
            )
        )

    def save_model(self, request, obj, form, change):
        # 1. Сброс артикула/слага при необходимости
        # Если в карточке варианта товара чекбокс перегенерации нажат — очищаем поле прямо перед сохранением
        if form.cleaned_data.get("regen_article"):
            obj.article = None
        if form.cleaned_data.get("regen_slug"):
            obj.slug = None

        # 2. Валидация активации из списка (Changelist)
        if request.resolver_match and "changelist" in request.resolver_match.url_name:
            # Если менеджер попытался включить товар без размеров через чекбокс в списке
            if obj.is_active and obj.sizes.filter(is_active=True).count() == 0:
                # Отменяем активацию
                obj.is_active = False
                messages.error(
                    request,
                    f"Вариант '{obj}' не активирован: добавьте размеры.",
                )

        # Сохраняем сам вариант
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        # 1. Сохраняем инлайны (размеры, фото, материалы)
        super().save_related(request, form, formsets, change)

        variant = form.instance

        # 2. Проверяем, была ли введена массовая скидка
        discount_value = form.cleaned_data.get("set_discount_all_sizes")

        if discount_value is not None:
            # Получаем все активные размеры варианта
            sizes = variant.sizes.filter(is_active=True)

            # Используем транзакцию для надежности
            with transaction.atomic():
                for size in sizes:
                    # Устанавливаем скидку
                    size.discount_percent = discount_value
                    # Вызываем .save(), чтобы сработал расчет final_price
                    size.save()

            self.message_user(
                request,
                f"Скидка {discount_value}% успешно применена для всех размеров.",
            )

        # 3. Ищем, в какой форме был изменен или установлен флаг is_main
        manual_id = None
        for formset in formsets:
            if formset.model == ProductImage:
                for f in formset.forms:
                    # Если галочка is_main изменилась или она True в новой форме
                    if "is_main" in f.changed_data and f.cleaned_data.get("is_main"):
                        if f.instance.pk:
                            manual_id = f.instance.pk
                break

        # 4. Передаем этот ID в функцию синхронизации
        from ..utils import sync_product_images

        sync_product_images(variant, manual_selected_id=manual_id)

    class Media:
        js = ("admin/js/no_active_product.js",)
        css = {
            "all": (
                "admin/css/display_inactive_products.css",
                "admin/css/changelist-filter.css",
            )
        }
