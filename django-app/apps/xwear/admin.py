from django import forms
from django.core.exceptions import ValidationError
from django.contrib import admin, messages
from django.db.models import Count, Q, F, Min, Max, OuterRef, Subquery
from django.utils.html import format_html
from django.urls import reverse
from django.utils.http import urlencode
from django_mptt_admin.admin import DjangoMpttAdmin
from adminsortable2.admin import (
    SortableAdminBase,
    SortableAdminMixin,
    SortableInlineAdminMixin,
    CustomInlineFormSet,
)

# from mptt.forms import TreeNodeChoiceField
from core.admin import ReadOnlyAdminMixin
from .models import (
    Category,
    Brand,
    Color,
    Product,
    ProductImage,
    Size,
    ProductSize,
    Material,
    ProductSpecification,
    Favorite,
    SliderBanner,
)
from .utils import get_admin_thumb, add_validator_attrs_to_widget


# ------ КАТЕГОРИИ --------


@admin.register(Category)
class CategoryAdmin(DjangoMpttAdmin):
    # атр. prepopulated_fields - автогенерация slug по name (показ подсказки в админке)
    prepopulated_fields = {"slug": ("name",)}
    list_display = ["name", "slug", "level", "is_active"]
    list_display_links = ["name"]
    list_filter = ["is_active", "level"]
    list_editable = ["is_active"]
    search_fields = ["name"]

    # Это ускорит работу __str__, так как родители будут в памяти
    def get_queryset(self, request):
        return super().get_queryset(request).select_related("parent")


# ------ ЦВЕТА --------


class ColorAdminForm(forms.ModelForm):
    class Meta:
        model = Color
        fields = "__all__"
        widgets = {
            # HTML5 type="color" превращает обычный input в системную палитру выбора цвета
            "hex_code": forms.TextInput(
                attrs={
                    "type": "color",
                    "style": "height: 40px; width: 60px; padding: 0; cursor: pointer;",
                }
            ),
        }


@admin.register(Color)
class ColorAdmin(SortableAdminMixin, admin.ModelAdmin):
    form = ColorAdminForm
    list_display = ["name", "color_preview", "slug", "hex_code"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}

    @admin.display(description="Цвет")
    def color_preview(self, obj):
        # Базовые стили для кружочка
        base_style = (
            "width: 24px; height: 24px; border-radius: 50%; border: 1px solid #ccc;"
        )

        # 1. Приоритет отдаем текстуре (картинке)
        if obj.texture:
            return format_html(
                '<div style="{} background-image: url({}); background-size: cover; background-position: center;" title="{}"></div>',
                base_style,
                obj.texture.url,
                obj.name,
            )

        # 2. Если есть второй цвет — делаем диагональный градиент
        elif obj.hex_code_2:
            return format_html(
                '<div style="{} background: linear-gradient(135deg, {} 51%, {} 49%);" title="{}"></div>',
                base_style,
                obj.hex_code,
                obj.hex_code_2,
                obj.name,
            )

        # 3. Обычный однотонный цвет
        elif obj.hex_code:
            return format_html(
                '<div style="{} background-color: {};" title="{}"></div>',
                base_style,
                obj.hex_code,
                obj.name,
            )

        return "-"


# ------ ИЗОБРАЖЕНИЯ --------


class ProductImageFormSet(CustomInlineFormSet):
    """Проверяет, что загружено хотя бы одно изображение"""

    def clean(self):
        super().clean()
        # Считаем количество форм, которые не помечены на удаление и содержат файлы
        count = 0
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get("DELETE"):
                count += 1

        if count < 1:
            raise ValidationError("У товара должно быть хотя бы одно изображение.")


class ProductImageInline(SortableInlineAdminMixin, admin.TabularInline):
    model = ProductImage
    formset = ProductImageFormSet
    extra = 1  # 1 пустая строка для изображения
    fields = ["image", "is_main", "alt", "image_preview"]
    sortable_field_name = "position"
    verbose_name_plural = "Фото товара (При создании выберите главное фото, при редактировании - перетащите наверх)"

    @admin.display(description="Превью")
    def image_preview(self, obj):
        return get_admin_thumb(obj.image, alias="admin_preview")

    def get_readonly_fields(self, request, obj=None):
        # obj — это сам Товар (Product).
        # Если он существует (obj is not None), значит мы в режиме редактирования.
        if obj:
            return ["image_preview", "is_main"]
        # Если товара еще нет (режим создания), все поля доступны для редактирования
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
            .select_related("product__category", "product__brand")
        )

    class Media:
        js = ("admin/js/image_preview.js",)


# ------ РАЗМЕРЫ --------


@admin.register(Size)
class SizeAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ["name"]
    list_display_links = ["name"]
    search_fields = ["name"]
    # list_editable = ["order"]
    # fields = (("name", "order"),)


class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1  # 1 пустой размер
    fields = ["size", "price", "discount_percent", "display_final_price", "is_active"]
    # Это делает выбор размера быстрым поиском (требует search_fields в SizeAdmin)
    autocomplete_fields = ["size"]
    readonly_fields = ["display_final_price"]

    @admin.display(description="Итоговая цена")
    def display_final_price(self, obj):
        if obj.final_price:
            return format_html(
                '<strong style="color: #28a745;">{} </strong>', obj.final_price
            )
        return "-"

    def get_queryset(self, request):
        # Оптимизируем запрос, чтобы не тянуть размеры по одному
        return super().get_queryset(request).select_related("size")


# ------ ХАРАКТЕРИСТИКИ --------


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ("name", "material_type")
    list_filter = ("material_type",)

    # Поиск по названию (обязательно для работы autocomplete_fields)
    search_fields = ("name",)

    # Сортировка: сначала по типу, потом по алфавиту
    ordering = ("material_type", "name")


class SpecificationInline(admin.StackedInline):
    model = ProductSpecification
    can_delete = False
    # Ограничиваем количество, так как это OneToOne
    max_num = 1

    autocomplete_fields = ["material_outer", "material_inner", "material_sole"]

    class Media:
        # Прячем заголовок h3 внутри инлайна (появляется при StackedInline)
        css = {"all": ("admin/css/hide_inline_header.css",)}


# ------ ТОВАРЫ --------


class ProductAdminForm(forms.ModelForm):
    # Указываем специальное поле для выбора категории
    # level_indicator — это символы, которые будут показывать вложенность
    # category = TreeNodeChoiceField(queryset=Category.objects.all(), level_indicator="---")
    # Фильтруем категории так, чтобы можно было выбрать только "листья" (leaf nodes)
    # category = TreeNodeChoiceField(
    #     queryset=Category.objects.filter(children__isnull=True), level_indicator="--"
    # )

    # Добавляем виртуальное поле для установки массовой скидки
    set_discount_all_sizes = forms.IntegerField(
        label="Установить скидку (%) на все размеры",
        required=False,
        min_value=0,
        max_value=100,
        help_text="Введите число, чтобы массово обновить скидку",
    )

    regen_article = forms.BooleanField(
        required=False,
        label="Сбросить артикул",
        help_text="Отметьте, чтобы создать новый артикул при сохранении",
    )
    regen_slug = forms.BooleanField(
        required=False,
        label="Сбросить слаг",
        help_text="Отметьте, чтобы обновить ссылку на товар",
    )

    class Meta:
        model = Product
        fields = "__all__"

    # метод проверки данных поля формы
    def clean_category(self):
        category = self.cleaned_data.get("category")

        # Проверяем, является ли категория "листом" (т.е. нет ли у неё детей)
        # В django-mptt для этого есть встроенный метод is_leaf_node()
        if category and not category.is_leaf_node():
            raise ValidationError(
                f"Категория '{category.name}' является групповой. "
                "Пожалуйста, выберите конечную подкатегорию."
            )

        return category


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


class SizeFilter(admin.SimpleListFilter):
    title = "Размер"
    parameter_name = "size"

    def lookups(self, request, model_admin):
        # 1. Получаем список ID размеров, которые реально используются в товарах.
        # model_admin.model — это наша модель Product.
        # values_list(..., flat=True) достает только колонку с ID.
        # distinct() убирает дубликаты, чтобы база не вернула [42, 42, 42, 43, 43...].
        used_size_ids = model_admin.model.objects.values_list(
            "sizes__size_id", flat=True
        ).distinct()

        # 2. Достаем из базы только те размеры, ID которых есть в нашем списке
        # exclude(id=None) на всякий случай отсекает товары вообще без размеров
        sizes = (
            Size.objects.filter(id__in=used_size_ids).exclude(id=None).order_by("name")
        )

        # 3. Возвращаем чистый список
        return [(s.id, s.name) for s in sizes]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(sizes__size_id=self.value())
        return queryset


class AvailabilityFilter(admin.SimpleListFilter):
    # Название фильтра в правой панели
    title = "Наличие размеров"
    # Имя параметра в URL (например, ?availability=in_stock)
    parameter_name = "availability"

    def lookups(self, request, model_admin):
        """Определяем варианты для выбора в фильтре"""
        return (
            ("in_stock", "Есть в наличии"),
            ("full", "Все в наличии"),
            ("out_of_stock", "Нет размеров"),
        )

    def queryset(self, request, queryset):
        """Фильтруем запрос в зависимости от выбранного пункта"""
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


class CategoryOptimizedFilter(admin.SimpleListFilter):
    title = "Категория"  # Заголовок в сайдбаре
    parameter_name = "category_id"  # Имя параметра в URL

    def lookups(self, request, model_admin):
        # делаем ОДИН запрос с select_related('parent')
        categories = (
            model_admin.model._meta.get_field("category")
            .related_model.objects.select_related("parent")
            .all()
        )
        # Возвращаем список кортежей (id, имя_с_отступами)
        # Так как мы использовали select_related, метод __str__ не будет дергать базу
        return [(c.pk, str(c)) for c in categories]

    def queryset(self, request, queryset):
        # Фильтруем основной список товаров
        if self.value():
            return queryset.filter(category_id=self.value())
        return queryset


class ActiveColorFilter(admin.SimpleListFilter):
    title = "Цвет"
    parameter_name = "color"

    def lookups(self, request, model_admin):
        # Получаем только те цвета, у которых есть хотя бы один товар,
        # и убираем дубликаты с помощью distinct()
        colors = Color.objects.filter(products__isnull=False).distinct()
        return [(c.id, c.name) for c in colors]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(color_id=self.value())
        return queryset


@admin.register(Product)
class ProductAdmin(SortableAdminBase, admin.ModelAdmin):
    form = ProductAdminForm
    inlines = [ProductImageInline, ProductSizeInline, SpecificationInline]

    list_display = [
        "article",
        "get_full_name",
        "get_color_name",
        "get_colors_count",
        "gender",
        "get_root_category",
        "get_season",
        "active_sizes_count",
        "get_price_range",
        "image_main",
        "is_active",
    ]
    list_display_links = ["get_full_name", "article"]
    list_filter = [
        "is_active",
        "gender",
        "brand",
        ActiveColorFilter,
        "specification__season",
        CategoryOptimizedFilter,
        AvailabilityFilter,
        SizeFilter,
        DiscountFilter,
    ]
    # search_fields = ["get_full_name", "article", "brand__name"]
    search_fields = ["brand__name", "model_name", "article"]

    # Если категорий и брендов будет много (заменяет выбор из выпадающего списка на удобный поиск)
    # search_fields = ["name", "brand__name", "category__name"] # в BrandAdmin и CategoryAdmin name уже указано
    # autocomplete_fields = ["brand", "category"]
    autocomplete_fields = ["category", "base_product", "color"]

    # Редактирование в списке
    list_editable = ["is_active"]

    # Артикул и слаг всегда только для чтения
    readonly_fields = ["article", "slug"]

    # Форма редактирования
    fieldsets = (
        (
            "Классификация",
            {
                "fields": (
                    ("brand", "model_name"),
                    ("category", "gender"),
                    "color",
                    "base_product",
                ),
            },
        ),
        (
            "Информация",
            {
                "fields": ("description",),
            },
        ),
        (
            "Настройки и Статус",
            {
                "fields": (
                    "set_discount_all_sizes",
                    "is_active",
                ),
            },
        ),
        (
            "Идентификация (Авто)",
            {
                "classes": ("collapse",),  # Делаем блок свернутым по умолчанию
                "fields": ("name", "article", "slug"),
            },
        ),
        (
            "Служебные действия",
            {
                "classes": ("collapse",),
                "description": (
                    '<div style="color: #ba2121; font-weight: bold; margin-bottom: 10px;">'
                    "⚠️ ИНСТРУКЦИЯ: Если вы изменили ВИД, БРЕНД, МОДЕЛЬ или КАТЕГОРИЮ у существующего товара:<br>"
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

    # show_full_result_count = False

    @admin.display(description="Полное название")
    def get_full_name(self, obj):
        return obj.full_name

    @admin.display(description="Пол")
    def gender_display(self, obj):
        return obj.get_gender_display()

    # gender_display.short_description = "Пол"

    @admin.display(description="Цвет")
    def get_color_name(self, obj):
        return obj.color if obj.color else "—"

    @admin.display(description="Вариации")
    def get_colors_count(self, obj):
        # Проверяем, есть ли у текущего товара родитель
        if obj.base_product_id:
            # Это дочерний товар (вариация)
            count = obj.child_colors_count
            # Ссылка должна вести на ID родителя, чтобы показать всю группу
            target_base_id = obj.base_product_id
        else:
            # Это базовый товар
            count = obj.parent_colors_count
            # Ссылка ведет на его собственный ID
            target_base_id = obj.id

        # Если товар базовый и у него нет вариаций
        if count == 0:
            return "—"

        # Генерируем ссылку
        url = (
            reverse("admin:xwear_product_changelist")
            + "?"
            + urlencode({"base_product__id__exact": target_base_id})
        )

        return format_html('<a href="{}">{}</a>', url, count)

    @admin.display(description="Сезон", ordering="specification__season")
    def get_season(self, obj):
        if hasattr(obj, "specification"):
            return obj.specification.get_season_display()
        return "—"

    @admin.display(description="Группа", ordering="root_category_name")
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

    # @admin.display(description="Категория", ordering="category")
    # def get_short_category(self, obj):
    #     """
    #     Отображает только последнюю часть категории (после разделителя)
    #     """
    #     if obj.category:
    #         full_path = str(obj.category)
    #         return full_path.rsplit(" / ", maxsplit=1)[-1]
    #     return "-"

    @admin.display(description="Главное фото")
    def image_main(self, obj):
        main_img = obj.get_main_image_obj
        if main_img:
            return get_admin_thumb(main_img.image, "xwear.ProductImage.image")
        return "-"
        # return None

    @admin.display(description="Размеры", ordering="active_sizes")
    def active_sizes_count(self, obj):
        # 1.вар - через цикл (не оптимально для большого кол-ва данных)
        # Получаем все размеры один раз (они уже в кеше благодаря prefetch_related)
        # all_sizes = obj.sizes.all()
        # all_count = len(all_sizes)
        # Считаем активные без создания лишних списков в памяти
        # active_count = sum(1 for s in all_sizes if s.is_active)

        # Считаем в памяти через список - менее оптимально
        # active_count = len([s for s in obj.sizes.all() if s.is_active])

        # return f"{active_count} / {all_count}"

        # 2.вар - подсчет на уровне SQL через annotate в get_queryset (работает быстро и поддерживает сортировку в столбце)
        active = obj.active_count
        total = obj.total_count

        # По умолчанию цвет обычный
        text_color = "inherit"

        if active == 0:
            text_color = "#dc3545"  # Красный
        elif active == total:
            text_color = "#28a745"  # Зеленый
        elif active < total / 2:
            text_color = "#800000"  # Бордовый

        return format_html(
            '<span style="color: {};">{} / {}</span>',
            text_color,
            active,
            total,
        )

    @admin.display(description="Диапазон цен", ordering="min_price")
    def get_price_range(self, obj):
        # 1 вар. - Через список - не оптимально
        # prices = [s.final_price for s in obj.sizes.all() if s.is_active]
        # if prices:
        #     return f"{min(prices)} - {max(prices)}"
        # return "Цена не задана"

        # 2.вар - подсчет на уровне SQL через annotate в get_queryset (работает быстро и поддерживает сортировку в столбце)
        # Если база нашла цены (min_price не None)
        if obj.min_price is not None:
            # Если мин и макс совпадают, выводим одно число, иначе диапазон
            if obj.min_price == obj.max_price:
                return f"{obj.min_price}"
            return f"{obj.min_price} – {obj.max_price}"

        return "Цена не задана"

    # ограничиваем выборку для base_product
    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term
        )

        # Проверяем, что запрос пришел именно от нашего поля
        if request.GET.get("field_name") == "base_product":
            # 1. Сначала оставляем только "корневые" товары
            queryset = queryset.filter(base_product__isnull=True)

            # 2. Пытаемся достать данные из GET-запроса
            brand_id = request.GET.get("forward_brand")
            category_id = request.GET.get("forward_category")
            model_name = request.GET.get("forward_model")

            # 3. Если данные есть — фильтруем жестко по модели
            if brand_id and category_id and model_name:
                queryset = queryset.filter(
                    brand_id=brand_id,
                    category_id=category_id,
                    model_name__iexact=model_name,  # Регистронезависимо
                )

        return queryset, use_distinct

    # Оптимизация запросов
    def get_queryset(self, request):
        # Создаем подзапрос: ищем категорию с уровнем 0 и таким же tree_id, как у товара
        root_category_subquery = Category.objects.filter(
            tree_id=OuterRef("category__tree_id"), level=0
        ).values("name")[:1]

        return (
            super()
            .get_queryset(request)
            .select_related(
                "category__parent", "brand", "color", "base_product", "specification"
            )
            .prefetch_related("images")
            .annotate(
                # Считаем общее количество связанных размеров
                total_count=Count("sizes"),
                # Считаем только активные размеры, используя фильтр Q
                active_count=Count("sizes", filter=Q(sizes__is_active=True)),
                # 1. Если это базовый товар (считаем его "детей")
                parent_colors_count=Count("variants__color", distinct=True),
                # 2. Если это дочерний товар (идем к родителю и считаем его "детей")
                child_colors_count=Count("base_product__variants__color", distinct=True),
                # Расчет цен
                min_price=Min("sizes__final_price", filter=Q(sizes__is_active=True)),
                max_price=Max("sizes__final_price", filter=Q(sizes__is_active=True)),
                # Добавляем имя корневой категории в SQL запрос
                root_category_name=Subquery(root_category_subquery),
            )
        )

    def save_model(self, request, obj, form, change):
        # 1. Если чекбокс перегенерации нажат — очищаем поле прямо перед сохранением
        if form.cleaned_data.get("regen_article"):
            obj.article = None
        if form.cleaned_data.get("regen_slug"):
            obj.slug = None

        # 2. Сохраняем сам товар
        super().save_model(request, obj, form, change)

        # 3. Проверяем, ввел ли менеджер значение в поле массовой скидки
        discount_value = form.cleaned_data.get("set_discount_all_sizes")

        if discount_value is not None:
            # Обновляем все активные размеры этого товара одним запросом к базе
            obj.sizes.filter(is_active=True).update(discount_percent=discount_value)

            messages.info(
                request, f"Скидка {discount_value}% применена ко всем размерам."
            )

    def save_related(self, request, form, formsets, change):
        # 1. Сначала даем Django сохранить все инлайны и позиции от Sortable2
        super().save_related(request, form, formsets, change)

        # 2. Ищем, в какой форме был изменен или установлен флаг is_main
        manual_id = None
        for formset in formsets:
            if formset.model == ProductImage:
                for f in formset.forms:
                    # Если галочка is_main изменилась или она True в новой форме
                    if "is_main" in f.changed_data and f.cleaned_data.get("is_main"):
                        if f.instance.pk:
                            manual_id = f.instance.pk
                break

        # 3. Передаем этот ID в функцию синхронизации
        from .utils import sync_product_images

        sync_product_images(form.instance, manual_selected_id=manual_id)

    # Динамический подход для полей только для чтения (если данных ещё нет, можно ввести вручную)
    # def get_readonly_fields(self, request, obj=None):
    #     if obj:  # Если товар уже создан
    #         return [
    #             "article",
    #             "slug",
    #         ]  # Запрещаем менять слаг и артикул ПОСЛЕ создания
    #     return ["article"]  # При создании слаг можно править

    class Media:
        js = (
            "admin/js/product_gender_auto.js",
            "admin/js/product_price_preview.js",
            "admin/js/product_autocomplete.js",
        )


# ------ БРЕНДЫ --------


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "view_products_link_list"]
    readonly_fields = ["view_products_link_detail"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]

    fieldsets = (
        (
            None,
            {
                "fields": (("name", "slug"), "view_products_link_detail"),
            },
        ),
    )

    # @admin.display(description="Кол-во товаров", ordering="products_count")
    # def get_products_count(self, obj):
    #     # Берем значение из аннотации
    #     return obj.products_count

    # Ссылка для общего СПИСКА брендов (компактная)
    @admin.display(description="Товары")
    def view_products_link_list(self, obj):
        if obj.pk:
            url = (
                reverse("admin:xwear_product_changelist") + f"?brand__id__exact={obj.pk}"
            )
            return format_html('<a href="{}">Перейти ({})</a>', url, obj.products_count)
        return "-"

    # 3. Кнопка для СТРАНИЦЫ редактирования бренда
    @admin.display(description="Управление ассортиментом")
    def view_products_link_detail(self, obj):
        if obj.pk:
            url = (
                reverse("admin:xwear_product_changelist") + f"?brand__id__exact={obj.pk}"
            )
            return format_html(
                '<a href="{}" class="button" style="background-color: #79aec8; color: white; padding: 10px 15px; text-decoration: none; border-radius: 4px;">'
                'Посмотреть все товары бренда "{}" ({})'
                "</a>",
                url,
                obj.name,
                obj.products_count,
            )
        return "Сначала сохраните бренд"

    def get_queryset(self, request):
        # Используем аннотацию
        return super().get_queryset(request).annotate(products_count=Count("products"))


# ------ ИЗБРАННОЕ --------


@admin.register(Favorite)
class FavoriteAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ("user", "product", "created_at")
    list_filter = ("user", "product__brand", "created_at")
    search_fields = ("user__email", "product__name")
    readonly_fields = (
        "user",
        "product",
        "created_at",
    )


# ------ БАННЕР-СЛАЙДЕР --------


@admin.register(SliderBanner)
class SliderBannerAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ("get_preview", "title", "order", "link", "is_active")
    list_editable = ("link", "is_active")
    readonly_fields = ("get_preview_large",)
    fields = ("title", "image", "get_preview_large", "link", "is_active")

    @admin.display(description="Превью")
    def get_preview(self, obj):
        return get_admin_thumb(obj.image, alias="admin_preview")

    @admin.display(description="Текущее изображение")
    def get_preview_large(self, obj):
        return get_admin_thumb(obj.image, alias="slider_large", show_info=True)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == "image":
            # Прокидываем лимиты ImageValidator в админку (в data-атрибуты поля)
            add_validator_attrs_to_widget(db_field, formfield)
        return formfield

    class Media:
        js = ("admin/js/image_preview.js",)
