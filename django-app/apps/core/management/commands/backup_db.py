import os
import time
import subprocess
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class Command(BaseCommand):
    help = "Создает бинарный бэкап базы данных PostgreSQL (.backup) с текущей датой и удаляет архивы старше 7 дней"

    def handle(self, *args, **options):
        # 1. Получаем настройки базы данных по умолчанию
        db = settings.DATABASES["default"]
        db_engine = db.get("ENGINE", "")

        # Проверяем, что это точно PostgreSQL
        if "postgresql" not in db_engine:
            raise CommandError("Этот скрипт работает только с базами данных PostgreSQL.")

        db_name = db["NAME"]
        db_user = db["USER"]
        db_password = db["PASSWORD"]
        db_host = db["HOST"] or "127.0.0.1"
        db_port = db["PORT"] or "5432"

        # 2. Формируем имя файла с датой и временем
        # Формат: dbname_backup_2026_04_06_15_30.backup
        timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M")
        filename = f"{db_name}_backup_{timestamp}.backup"

        # Создаем папку backups в корне проекта, если её нет
        backup_dir = os.path.join(settings.BASE_DIR, "backups")
        os.makedirs(backup_dir, exist_ok=True)
        filepath = os.path.join(backup_dir, filename)

        # 3. Подготавливаем команду pg_dump
        cmd = [
            "pg_dump",
            "-U",
            db_user,
            "-h",
            db_host,
            "-p",
            str(db_port),
            "-F",
            "c",  # Формат Custom (бинарный архив)
            "-d",
            db_name,  # Явное указание имени БД
            "-f",
            filepath,  # Куда сохранить файл
        ]

        # 4. Передаем пароль через переменные окружения,
        # чтобы pg_dump не завис в ожидании ввода с клавиатуры
        env = os.environ.copy()
        if db_password:
            env["PGPASSWORD"] = db_password

        self.stdout.write(f'Создание бэкапа базы данных "{db_name}"...')

        # 5. Запускаем процесс
        try:
            # check=True выбросит исключение, если команда завершится с ошибкой
            subprocess.run(cmd, env=env, check=True, capture_output=True, text=True)
            self.stdout.write(self.style.SUCCESS(f"Бэкап создан: {filepath}"))

            # Опционально: можно добавить вывод размера файла
            file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
            self.stdout.write(f"Размер файла: {file_size_mb:.2f} MB")

        except subprocess.CalledProcessError as e:
            # Если что-то пошло не так, выводим ошибку из консоли PostgreSQL
            self.stderr.write(self.style.ERROR("Ошибка при создании бэкапа:"))
            self.stderr.write(self.style.ERROR(e.stderr))

        # 6. Очистка старых бэкапов
        days_to_keep = 7
        now = time.time()

        # 86400 - это количество секунд в одних сутках (24 * 60 * 60)
        cutoff_time = now - (days_to_keep * 86400)

        deleted_backups = 0
        # deleted_logs = 0

        self.stdout.write("Запуск удаления старых бэкапов...")

        # Перебираем все файлы в папке backups
        for filename in os.listdir(backup_dir):
            filepath = os.path.join(backup_dir, filename)

            # Удаляем только файлы .backup старше 7 дней
            if os.path.isfile(filepath) and filename.endswith(".backup"):
                # Проверяем время последней модификации файла
                file_mtime = os.path.getmtime(filepath)
                # Если файл старше 7 дней
                if file_mtime < cutoff_time:
                    os.remove(filepath)
                    deleted_backups += 1

        if deleted_backups > 0:
            self.stdout.write(
                self.style.WARNING(f"Удалено старых бэкапов - {deleted_backups}")
            )
        else:
            self.stdout.write("Нет файлов для удаления.")

        self.stdout.write(
            self.style.SUCCESS("Процесс резервного копирования и очистки завершен.")
        )


# Как использовать
# --------------------------
# 1. Ручной запуск в терминале:
# python manage.py backup_db

# 2. Автоматизация (Production):
# Когда проект будет на сервере, можно настроить Cron (планировщик задач в Linux), чтобы команда запускалась, например, раз в сутки в 3 часа ночи.
# 2.1 Чтобы добавить задачу в Cron на сервере Linux, введи команду:
# crontab -e
# 2.2 Затем добавь в конец файла следующую строку:
# 0 3 * * * /путь/к/проекту/venv/bin/python /путь/к/проекту/manage.py backup_db > /путь/к/проекту/backups/cron.log 2>&1
# или так:
# 0 3 * * * /путь/к/проекту/venv/bin/python /путь/к/проекту/manage.py backup_db >> /путь/к/проекту/backups/cron.log 2>&1

# Разбор команды Cron:
# 0 3 * * * : Это расписание. Запускать в 03:00 (3 часа ночи, 0 минут), каждый день, каждый месяц, каждый день недели.
# указываем абсолютный путь к интерпретатору Python внутри твоего виртуального окружения (venv).
# Указываем абсолютный путь к manage.py.
# > cron.log 2>&1: Все успехи и ошибки скрипта будут перезаписываться в файл лога (отчёт только о последнем бэкапе)
# >> cron.log 2>&1: Новые записи дописываются в конец файла. Удобно, чтобы посмотреть, не было ли сбоев неделю назад.
