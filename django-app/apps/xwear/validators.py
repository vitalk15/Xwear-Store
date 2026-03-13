from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from django.utils.deconstruct import deconstructible


# Универсальный валидатор изображений
# Декоратор @deconstructible нужен, чтобы Django мог корректно сохранять этот валидатор в миграциях.
@deconstructible
class ImageValidator:
    def __init__(self, min_width=None, min_height=None, max_mb=None):
        self.min_width = min_width
        self.min_height = min_height
        self.max_mb = max_mb

    def __call__(self, image):
        # 1. Проверка веса файла
        if self.max_mb:
            filesize = image.size / (1024 * 1024)  # Переводим в Мб
            if filesize > self.max_mb:
                raise ValidationError(
                    f"Файл слишком тяжелый ({filesize:.2f} Мб). Максимум: {self.max_mb} Мб."
                )

        # 2. Проверка размеров (пиксели)
        width, height = get_image_dimensions(image)
        if self.min_width and width < self.min_width:
            raise ValidationError(
                f"Ширина изображения слишком мала ({width}px). Минимум: {self.min_width}px."
            )
        if self.min_height and height < self.min_height:
            raise ValidationError(
                f"Высота изображения слишком мала ({height}px). Минимум: {self.min_height}px."
            )
