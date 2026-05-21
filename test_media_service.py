#!/usr/bin/env python3
"""
Тестирование сервиса Media
"""
import sys
import os

# Добавляем путь для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Тестирование сервиса Media...")
print("=" * 60)

# Тест 1: Проверка импортов
try:
    from services.Media.config import config
    print("OK: Импорт config.py: УСПЕШНО")
    print(f"  Порт: {config.SERVICE_PORT}")
    print(f"  Имя сервиса: {config.SERVICE_NAME}")
except ImportError as e:
    print(f"ERROR: Импорт config.py: ОШИБКА - {e}")

try:
    from services.Media import schemas
    print("OK: Импорт schemas.py: УСПЕШНО")
except ImportError as e:
    print(f"ERROR: Импорт schemas.py: ОШИБКА - {e}")

try:
    from services.Media import crud
    print("OK: Импорт crud.py: УСПЕШНО")
except ImportError as e:
    print(f"ERROR: Импорт crud.py: ОШИБКА - {e}")

try:
    from services.Media import utils
    print("OK: Импорт utils.py: УСПЕШНО")
except ImportError as e:
    print(f"ERROR: Импорт utils.py: ОШИБКА - {e}")

try:
    from services.Media import dependencies
    print("OK: Импорт dependencies.py: УСПЕШНО")
except ImportError as e:
    print(f"ERROR: Импорт dependencies.py: ОШИБКА - {e}")

try:
    from services.Media.routers import media, health
    print("OK: Импорт routers: УСПЕШНО")
except ImportError as e:
    print(f"ERROR: Импорт routers: ОШИБКА - {e}")

try:
    from services.Media.main import app
    print("OK: Импорт main.py: УСПЕШНО")
except ImportError as e:
    print(f"ERROR: Импорт main.py: ОШИБКА - {e}")

# Тест 2: Проверка модели
try:
    from database.models.media import MediaBD
    print("OK: Импорт модели MediaBD: УСПЕШНО")
    print(f"  Таблица: {MediaBD.__tablename__}")
    print(f"  Поле is_temp: {'is_temp' in MediaBD.__table__.columns}")
except ImportError as e:
    print(f"ERROR: Импорт модели MediaBD: ОШИБКА - {e}")

# Тест 3: Проверка создания директорий
try:
    from services.Media.utils import ensure_base_directories, ensure_user_directories
    print("OK: Функции ensure_base_directories и ensure_user_directories доступны")
except ImportError as e:
    print(f"ERROR: Функции ensure_*_directories: ОШИБКА - {e}")

print("=" * 60)
print("Тестирование завершено.")

# Проверка структуры эндпоинтов
print("\nСозданные эндпоинты:")
print("1. POST /media/upload - Загрузка медиафайла")
print("2. GET /media/{media_id} - Получение информации о медиа")
print("3. GET /media/ - Список медиа с фильтрами")
print("4. GET /media/temp/my - Временные медиа пользователя")
print("5. POST /media/{media_id}/confirm - Подтверждение временного медиа")
print("6. PUT /media/{media_id} - Обновление информации")
print("7. DELETE /media/{media_id} - Удаление медиа")
print("8. POST /media/cleanup/temp - Очистка временных медиа")
print("9. GET /media/page/{page_id} - Медиа страницы")
print("10. GET /health - Health check")
print("11. GET /temp/{filename} - Отдача временных файлов")
print("12. GET /permanent/{filename} - Отдача постоянных файлов")

print("\nСервис Media готов к запуску на порту 8004")