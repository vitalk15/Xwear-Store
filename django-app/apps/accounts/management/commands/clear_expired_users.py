from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings

User = get_user_model()


class Command(BaseCommand):
    help = "Удаляет пользователей, которые не подтвердили email в установленный срок"

    def handle(self, *args, **options):
        # 1. Определяем порог времени
        # Текущее время минус таймаут из настроек
        threshold = timezone.now() - timedelta(
            seconds=settings.ACCOUNT_ACTIVATION_TIMEOUT
        )

        # 2. Ищем неактивных пользователей, созданных раньше этого порога
        expired_users = User.objects.filter(is_active=False, date_joined__lt=threshold)

        count = expired_users.count()

        if count > 0:
            # 3. Удаляем их
            # (Вместе с ними удалятся записи из связанных таблиц, если есть)
            expired_users.delete()
            self.stdout.write(
                self.style.SUCCESS(f"Успешно удалено {count} неактивных пользователей.")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "Неактивных пользователей с истекшим сроком не найдено."
                )
            )


# Как использовать
# --------------------------
# 1. Ручной запуск в терминале:
# python manage.py clear_expired_users

# 2. Автоматизация (Production):
# Когда проект будет на сервере, можно настроить Cron (планировщик задач в Linux), чтобы команда запускалась, например, раз в сутки в 3 часа ночи. Запись в crontab будет выглядеть примерно так:
# 0 3 * * * cd /path/to/project && /path/to/venv/bin/python manage.py clear_expired_users
