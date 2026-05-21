#!/usr/bin/env python3
"""
Тестирование новой структуры папок сервиса Media
"""
import sys
import os
import shutil

# Добавляем путь для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.Media.config import config
from services.Media.utils import ensure_base_directories, ensure_user_directories, generate_filename
import uuid

print("Тестирование новой структуры папок сервиса Media...")
print("=" * 60)

# Тест 1: Проверка базовых директорий
print("1. Проверка базовых директорий:")
print(f"   TEMP_BASE_FOLDER: {config.TEMP_BASE_FOLDER}")
print(f"   PERMANENT_BASE_FOLDER: {config.PERMANENT_BASE_FOLDER}")

# Создаем базовые директории
ensure_base_directories()
if os.path.exists(config.TEMP_BASE_FOLDER):
    print("   [OK] TEMP_BASE_FOLDER создана")
else:
    print("   [ERROR] TEMP_BASE_FOLDER не создана")

if os.path.exists(config.PERMANENT_BASE_FOLDER):
    print("   [OK] PERMANENT_BASE_FOLDER создана")
else:
    print("   [ERROR] PERMANENT_BASE_FOLDER не создана")

# Тест 2: Проверка путей для пользователя
print("\n2. Проверка путей для пользователя:")
user_id = "test_user_123"
page_id = "test_page_456"

temp_path_user = config.get_temp_folder_path(user_id)
temp_path_user_page = config.get_temp_folder_path(user_id, page_id)
permanent_path_user = config.get_permanent_folder_path(user_id)
permanent_path_user_page = config.get_permanent_folder_path(user_id, page_id)

print(f"   temp_path_user: {temp_path_user}")
print(f"   temp_path_user_page: {temp_path_user_page}")
print(f"   permanent_path_user: {permanent_path_user}")
print(f"   permanent_path_user_page: {permanent_path_user_page}")

# Создаем директории пользователя
ensure_user_directories(user_id)
ensure_user_directories(user_id, page_id)

if os.path.exists(temp_path_user):
    print("   [OK] temp_path_user создана")
else:
    print("   [ERROR] temp_path_user не создана")

if os.path.exists(temp_path_user_page):
    print("   [OK] temp_path_user_page создана")
else:
    print("   [ERROR] temp_path_user_page не создана")

if os.path.exists(permanent_path_user):
    print("   [OK] permanent_path_user создана")
else:
    print("   [ERROR] permanent_path_user не создана")

if os.path.exists(permanent_path_user_page):
    print("   [OK] permanent_path_user_page создана")
else:
    print("   [ERROR] permanent_path_user_page не создана")

# Тест 3: Проверка генерации имен файлов
print("\n3. Проверка генерации имен файлов:")
media_id = str(uuid.uuid4())
original_filename = "test_image.jpg"
generated_name = generate_filename(original_filename, media_id)

print(f"   media_id: {media_id}")
print(f"   original_filename: {original_filename}")
print(f"   generated_name: {generated_name}")

# Проверяем формат: {id_media}_{дата_загрузки}.{расширение}
if generated_name.startswith(media_id + "_") and generated_name.endswith(".jpg"):
    print("   [OK] Формат имени файла правильный")
else:
    print("   [ERROR] Формат имени файла неправильный")

# Тест 4: Проверка URL генерации
print("\n4. Проверка генерации URL:")
from services.Media.utils import get_file_url

# Временный файл без page_id
url_temp = get_file_url(generated_name, user_id, None, True)
print(f"   URL временного файла (без page_id): {url_temp}")
expected_temp = f"/media/temp/{user_id}/{generated_name}"
if url_temp == expected_temp:
    print("   [OK] URL временного файла правильный")
else:
    print(f"   [ERROR] Ожидалось: {expected_temp}")

# Временный файл с page_id
url_temp_page = get_file_url(generated_name, user_id, page_id, True)
print(f"   URL временного файла (с page_id): {url_temp_page}")
expected_temp_page = f"/media/temp/{user_id}/{page_id}/{generated_name}"
if url_temp_page == expected_temp_page:
    print("   [OK] URL временного файла с page_id правильный")
else:
    print(f"   [ERROR] Ожидалось: {expected_temp_page}")

# Постоянный файл с page_id
url_perm_page = get_file_url(generated_name, user_id, page_id, False)
print(f"   URL постоянного файла (с page_id): {url_perm_page}")
expected_perm_page = f"/media/permanent/{user_id}/{page_id}/{generated_name}"
if url_perm_page == expected_perm_page:
    print("   [OK] URL постоянного файла с page_id правильный")
else:
    print(f"   [ERROR] Ожидалось: {expected_perm_page}")

# Тест 5: Очистка тестовых данных
print("\n5. Очистка тестовых данных:")
try:
    if os.path.exists(temp_path_user_page):
        shutil.rmtree(temp_path_user_page)
        print("   [OK] Удалена temp_path_user_page")
    if os.path.exists(temp_path_user):
        shutil.rmtree(temp_path_user)
        print("   [OK] Удалена temp_path_user")
    if os.path.exists(permanent_path_user_page):
        shutil.rmtree(permanent_path_user_page)
        print("   [OK] Удалена permanent_path_user_page")
    if os.path.exists(permanent_path_user):
        shutil.rmtree(permanent_path_user)
        print("   [OK] Удалена permanent_path_user")
except Exception as e:
    print(f"   [ERROR] Ошибка при очистке: {e}")

print("\n" + "=" * 60)
print("Тестирование завершено!")