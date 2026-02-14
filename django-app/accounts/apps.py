from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"
    verbose_name = "Аккаунты"

    def ready(self):
        # pylint: disable=unused-import, import-outside-toplevel
        import accounts.signals  # активация сигналов
