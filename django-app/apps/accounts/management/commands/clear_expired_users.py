import logging
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger("management_commands")

User = get_user_model()


class Command(BaseCommand):
    help = "Удаляет пользователей, которые не подтвердили email в установленный срок"

    def handle(self, *args, **options):
        # 1. Определяем порог времени
        # Текущее время минус таймаут из настроек
        threshold = timezone.now() - timedelta(
            seconds=settings.ACCOUNT_ACTIVATION_TIMEOUT
        )

        # 2. Ищем неактивных пользователей, созданных раньше этого порога.
        # Используем поле date_joined, которое Django заполняет автоматически при создании записи. Это гарантирует, что мы не удалим того, кто зарегистрировался всего 5 минут назад и просто еще не успел открыть почту.
        expired_users = User.objects.filter(is_active=False, date_joined__lt=threshold)

        count = expired_users.count()

        if count > 0:
            # 3. Формируем список email для логов (чтобы знать, кого удалили)
            emails = list(expired_users.values_list("email", flat=True))

            # 4. Удаляем неактивных пользователей
            # (Вместе с ними удалятся записи из связанных таблиц, если есть)
            expired_users.delete()

            message = f"Удалено {count} неактивных пользователей: {', '.join(emails)}"

            # Пишем в консоль
            self.stdout.write(self.style.SUCCESS(message))
            # Пишем в лог-файл
            logger.info(message)
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
