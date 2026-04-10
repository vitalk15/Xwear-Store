import os
import time
import subprocess
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class Command(BaseCommand):
    help = "Создает бэкап (по-умолчанию бинарный) всей базы или выбранных таблиц PostgreSQL. Удаляет архивы старше 7 дней."

    def add_arguments(self, parser):
        # Добавляем кастомный флаг --sql
        # action='store_true' означает, что если флаг указан, переменная будет True.
        # Если не указан — False.
        parser.add_argument(
            "--sql",
            action="store_true",
            help="Сохранить бэкап в текстовом формате (.sql) вместо бинарного",
        )
        # Добавляем кастомный флаг для таблиц. nargs='+' позволяет передать список через пробел
        parser.add_argument(
            "--tables",
            nargs="+",
            help="Список конкретных таблиц для бэкапа (например: core_category core_brand)",
        )
        parser.add_argument(
            "--data-only",
            action="store_true",
            help="Сохранить только данные (через INSERT), без структуры таблиц. Принудительно включает текстовый формат.",
        )

    def handle(self, *args, **options):
        # --- 1. Настройки базы и парсинг аргументов ---
        # Получаем настройки базы данных по умолчанию
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

        # Проверяем, передан ли флаг --sql
        is_sql_format = options["sql"]
        # Получаем список таблиц
        tables_to_backup = options["tables"]
        # Проверяем, передан ли флаг --data_only
        is_data_only = options["data_only"]

        # ВАЖНО: pg_dump поддерживает --inserts только при текстовом выводе
        if is_data_only:
            is_sql_format = True

        # Динамически задаем расширение файла и формат для pg_dump
        extension = ".sql" if is_sql_format else ".backup"
        pg_format = "p" if is_sql_format else "c"  # 'p' - plain, 'c' - custom

        # Дата и время создания
        timestamp = datetime.now().strftime("%d_%m_%Y_%H_%M")
        # timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M")

        # Формируем имя файла
        prefix = "partial" if tables_to_backup else "full"
        if is_data_only:
            prefix += "_data_only"

        filename = f"{db_name}_{prefix}_{timestamp}{extension}"

        # Создаем папку backups в корне проекта, если её нет
        backup_dir = os.path.join(settings.BASE_DIR, "backups")
        os.makedirs(backup_dir, exist_ok=True)
        filepath = os.path.join(backup_dir, filename)

        # --- 2. Создание бэкапа ---
        # Подготавливаем команду pg_dump
        cmd = [
            "pg_dump",
            "-U",
            db_user,
            "-h",
            db_host,
            "-p",
            str(db_port),
            "-F",
            pg_format,
            "-d",
            db_name,
            "-f",
            filepath,
        ]

        # Если запрошены только данные
        if is_data_only:
            cmd.extend(
                [
                    "--data-only",  # Не выгружать схему (-a)
                    "--column-inserts",  # Использовать INSERT с указанием колонок
                    "--disable-triggers",  # Отключить триггеры/внешние ключи при восстановлении
                ]
            )

        # Если таблицы указаны, добавляем каждый флаг -t в команду
        if tables_to_backup:
            for table in tables_to_backup:
                cmd.extend(["-t", table])

        # Передаем пароль через переменные окружения,
        # чтобы pg_dump не завис в ожидании ввода с клавиатуры
        env = os.environ.copy()
        if db_password:
            env["PGPASSWORD"] = db_password

        # Запускаем процесс
        try:
            target_desc = f'базы данных "{db_name}"'
            if tables_to_backup:
                target_desc = f"таблиц: {', '.join(tables_to_backup)}"

            mode_desc = "(Только данные)" if is_data_only else "(Схема + Данные)"
            self.stdout.write(f"Создание бэкапа {target_desc} {mode_desc}...")
            # check=True выбросит исключение, если команда завершится с ошибкой
            subprocess.run(cmd, env=env, check=True, capture_output=True, text=True)
            self.stdout.write(self.style.SUCCESS(f"Бэкап создан: {filepath}"))

            # Вывод размера файла
            file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
            self.stdout.write(f"Размер файла: {file_size_mb:.2f} MB")

        except subprocess.CalledProcessError as e:
            # Если что-то пошло не так, выводим ошибку из консоли PostgreSQL
            self.stderr.write(self.style.ERROR("Ошибка при создании бэкапа:"))
            self.stderr.write(self.style.ERROR(e.stderr))
            return  # Прерываем выполнение, чтобы не удалять старые бэкапы при ошибке нового

        # --- 3. Очистка старых бэкапов (7 дней) ---
        days_to_keep = 7

        # 86400 - это количество секунд в одних сутках (24 * 60 * 60)
        cutoff_time = time.time() - (days_to_keep * 86400)

        deleted_backups = 0
        # deleted_logs = 0

        self.stdout.write("Запуск удаления старых бэкапов...")

        # Перебираем все файлы в папке backups
        for filename in os.listdir(backup_dir):
            filepath = os.path.join(backup_dir, filename)

            # Проверяем оба возможных расширения перед удалением
            is_backup_file = filename.endswith(".backup") or filename.endswith(".sql")

            # Удаляем только файлы и только с двумя возможными расширениями
            if os.path.isfile(filepath) and is_backup_file:
                # Проверяем время последней модификации файла
                file_mtime = os.path.getmtime(filepath)
                # Если файл старше 7 дней
                if file_mtime < cutoff_time:
                    os.remove(filepath)
                    deleted_backups += 1

        if deleted_backups:
            self.stdout.write(
                self.style.WARNING(f"Удалено старых бэкапов - {deleted_backups}")
            )
        else:
            self.stdout.write("Нет файлов для удаления.")

        self.stdout.write(
            self.style.SUCCESS("Процесс резервного копирования и очистки завершен.")
        )


# Как использовать для бэкапа всей БД
# -----------------------------------
# 1. Ручной запуск в терминале:
# python manage.py backup_db
# или
# python manage.py backup_db --sql

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


# Как использовать для бэкапа таблиц
# ----------------------------------
# 1. Бинарный бэкап:
# python manage.py backup_db --tables xwear_category xwear_brand xwear_size xwear_color xwear_material
# 2. Текстовый бэкап:
# python manage.py backup_db --sql --tables xwear_category xwear_brand xwear_size xwear_color xwear_material
# 3. Встроенная команда Django, которая сохраняет данные в формате JSON, не привязываясь к SQL-структуре (если структура моделей изменена):
# python manage.py dumpdata xwear.Category --indent 4 > categories.json
# (--indent 4 добавляет в JSON-файл переносы строк и отступы в 4 пробела)

# Восстановление
# --------------
# 1. Для .sql файла:
# psql -U имя_пользователя -d имя_базы < table_backup.sql
# 2. Для .backup файла:
# pg_restore -U имя_пользователя -d имя_базы -t название_таблицы table_backup.backup
# 3. Встроенная команда Django, которая загружает данные в формате JSON обратно:
# python manage.py loaddata categories.json
