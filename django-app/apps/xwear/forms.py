from django import forms
from django.core.exceptions import ValidationError
from adminsortable2.admin import CustomInlineFormSet
from .models import Product, ProductVariant, Color


class ProductAdminForm(forms.ModelForm):
    # Указываем специальное поле для выбора категории
    # level_indicator — это символы, которые будут показывать вложенность
    # category = TreeNodeChoiceField(queryset=Category.objects.all(), level_indicator="---")
    # Фильтруем категории так, чтобы можно было выбрать только "листья" (leaf nodes)
    # category = TreeNodeChoiceField(
    #     queryset=Category.objects.filter(children__isnull=True), level_indicator="--"
    # )

    regen_slug = forms.BooleanField(
        required=False,
        label="Сбросить слаг",
        help_text="Если был изменён ВИД, БРЕНД, МОДЕЛЬ или КАТЕГОРИЯ - отметьте, чтобы обновить слаг",
    )

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

    class Meta:
        model = Product
        fields = "__all__"


class ProductVariantAdminForm(forms.ModelForm):
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
        help_text="Отметьте, чтобы создать новый артикул для варианта товара",
    )
    regen_slug = forms.BooleanField(
        required=False,
        label="Сбросить слаг",
        help_text="Отметьте, чтобы обновить ссылку на вариант товара",
    )

    class Meta:
        model = ProductVariant
        fields = "__all__"


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


class ProductSizeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.instance — это конкретная запись ProductSize (строка инлайна)
        if self.instance and self.instance.pk:
            # Если запись уже есть в базе, блокируем изменение размера
            self.fields["size"].disabled = True
        else:
            # Если это новая строка, поле будет доступно для выбора
            self.fields["size"].disabled = False

    def clean(self):
        cleaned_data = super().clean()
        is_active = cleaned_data.get("is_active")
        price = cleaned_data.get("price")
        size = cleaned_data.get("size")

        # Проверяем, не помечена ли строка на удаление (чтобы не спамить ошибками)
        if cleaned_data.get("DELETE"):
            return cleaned_data

        # Логика валидации
        if is_active:
            if price is None or price <= 0:
                # Выводим ошибку конкретно над полем цены
                # self.add_error(
                #     "price", f"Нельзя активировать размер {size} без указания цены!"
                # )

                # Или общую ошибку для всей строки
                raise ValidationError(
                    f"Нельзя активировать размер {size} без указания цены!"
                )

        return cleaned_data


class ProductSizeFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()

        # Если есть ошибки в самих формах размеров (например, буквы в цене), не продолжаем
        if any(self.errors):
            return

        # Проверяем, активен ли вариант (берем значение из формы, а не из базы!)
        # self.instance — это наш ProductVariant
        if self.instance.is_active:
            has_active_sizes = False
            for form in self.forms:
                # Проверяем, что форма заполнена, не пуста и не помечена на удаление
                if form.cleaned_data and not form.cleaned_data.get("DELETE", False):
                    if form.cleaned_data.get("is_active"):
                        has_active_sizes = True
                        break

            if not has_active_sizes:
                raise ValidationError(
                    "Нельзя активировать вариант без активных размеров."
                )


class ProductImageFormSet(CustomInlineFormSet):
    """Проверяет, что загружено хотя бы одно изображение"""

    def clean(self):
        super().clean()
        if any(self.errors):
            return

        # Если вариант активирован, проверяем картинки
        if self.instance.is_active:
            has_images = False
            for form in self.forms:
                # Проверяем, что форма не пустая и не помечена на удаление
                if form.cleaned_data and not form.cleaned_data.get("DELETE", False):
                    # Проверяем наличие самого файла изображения
                    if form.cleaned_data.get("image"):
                        has_images = True
                        break

            if not has_images:
                raise ValidationError(
                    "Для активации варианта нужно хотя бы одно изображение."
                )
