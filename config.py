"""
Файл конфигурации проекта.
Использует переменные окружения или значения по умолчанию.
"""

import os

# Тип базы данных: 'sqlite' или 'postgres'
DB_TYPE = os.getenv("DB_TYPE", "sqlite")

# SQLite настройки
DATABASE_PATH = os.getenv("DATABASE_PATH", "app.db")

# PostgreSQL настройки (используются если DB_TYPE='postgres')
PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = os.getenv("PG_PORT", "5432")
PG_DATABASE = os.getenv("PG_DATABASE", "app_db")
PG_USER = os.getenv("PG_USER", "postgres")
PG_PASSWORD = os.getenv("PG_PASSWORD", "postgres")

# Администратор по умолчанию
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")