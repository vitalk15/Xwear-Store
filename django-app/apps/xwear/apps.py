from django.apps import AppConfig


class XwearConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "xwear"
    verbose_name = "Магазин"

    def ready(self):
        # Пре-генерация миниатюр при сохранении изображения
        from easy_thumbnails.signals import saved_file
        from easy_thumbnails.signal_handlers import generate_aliases_global

        saved_file.connect(generate_aliases_global)
