"""
Утилиты для работы с медиафайлами
"""
import os
import uuid
import shutil
from pathlib import Path
from typing import Optional, Tuple
import mimetypes
from datetime import datetime, timedelta

from .config import config

# Импорты с обработкой ошибок (библиотеки могут быть не установлены)
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False


def ensure_base_directories():
    """Создает базовые директории для хранения файлов"""
    os.makedirs(config.TEMP_BASE_FOLDER, exist_ok=True)
    os.makedirs(config.PERMANENT_BASE_FOLDER, exist_ok=True)
    print(f"Created base directories: {config.TEMP_BASE_FOLDER}, {config.PERMANENT_BASE_FOLDER}")


def ensure_user_directories(user_id: str, page_id: str = None):
    """Создает необходимые директории для пользователя"""
    # Сначала создаем базовые директории
    ensure_base_directories()
    
    temp_path = config.get_temp_folder_path(user_id, page_id)
    permanent_path = config.get_permanent_folder_path(user_id, page_id)
    
    os.makedirs(temp_path, exist_ok=True)
    os.makedirs(permanent_path, exist_ok=True)


def get_file_extension(filename: str) -> str:
    """Получает расширение файла из имени"""
    return Path(filename).suffix.lower().lstrip('.')


def generate_filename(original_filename: str, media_id: str) -> str:
    """Генерирует уникальное имя файла: id_media + дата загрузки"""
    ext = get_file_extension(original_filename)
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{media_id}_{date_str}.{ext}"


def get_media_type(mime_type: str, file_extension: str) -> str:
    """Определяет тип медиа по MIME-типу и расширению"""
    if mime_type.startswith('image/'):
        return 'image'
    elif mime_type.startswith('video/'):
        return 'video'
    elif mime_type.startswith('audio/'):
        return 'audio'
    elif mime_type in ['application/pdf', 'application/msword', 
                       'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
        return 'document'
    else:
        # Пытаемся определить по расширению
        if file_extension in config.ALLOWED_EXTENSIONS['image']:
            return 'image'
        elif file_extension in config.ALLOWED_EXTENSIONS['video']:
            return 'video'
        elif file_extension in config.ALLOWED_EXTENSIONS['audio']:
            return 'audio'
        elif file_extension in config.ALLOWED_EXTENSIONS['document']:
            return 'document'
        else:
            return 'other'


def validate_file_size(file_size: int) -> bool:
    """Проверяет размер файла"""
    return file_size <= config.MAX_FILE_SIZE


def validate_file_extension(file_extension: str, media_type: str) -> bool:
    """Проверяет расширение файла"""
    if media_type in config.ALLOWED_EXTENSIONS:
        return file_extension.lower() in config.ALLOWED_EXTENSIONS[media_type]
    return False


def save_uploaded_file(file_content: bytes, filename: str, user_id: str, page_id: str = None, is_temp: bool = True) -> str:
    """Сохраняет загруженный файл в папку пользователя"""
    ensure_user_directories(user_id, page_id)
    
    if is_temp:
        save_folder = config.get_temp_folder_path(user_id, page_id)
    else:
        save_folder = config.get_permanent_folder_path(user_id, page_id)
    
    save_path = os.path.join(save_folder, filename)
    
    with open(save_path, 'wb') as f:
        f.write(file_content)
    
    return save_path


def get_file_info(file_path: str) -> Tuple[Optional[int], Optional[int], Optional[int]]:
    """Получает информацию о файле (ширина, высота, длительность)"""
    try:
        if HAS_MAGIC:
            mime_type = magic.from_file(file_path, mime=True)
        else:
            # Если библиотека magic не установлена, определяем по расширению
            ext = get_file_extension(file_path)
            if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp']:
                mime_type = 'image/jpeg'
            else:
                mime_type = 'application/octet-stream'
        
        if mime_type.startswith('image/') and HAS_PIL:
            with Image.open(file_path) as img:
                width, height = img.size
                return width, height, None
        
        # Для видео и аудио нужно использовать дополнительные библиотеки
        # Пока возвращаем None
        return None, None, None
        
    except Exception:
        return None, None, None


def move_to_permanent(temp_filename: str, permanent_filename: str, user_id: str, page_id: str = None) -> bool:
    """Перемещает файл из временной папки в постоянную"""
    try:
        temp_path = os.path.join(config.get_temp_folder_path(user_id, page_id), temp_filename)
        permanent_path = os.path.join(config.get_permanent_folder_path(user_id, page_id), permanent_filename)
        
        # Создаем целевую папку, если не существует
        os.makedirs(os.path.dirname(permanent_path), exist_ok=True)
        
        if os.path.exists(temp_path):
            shutil.move(temp_path, permanent_path)
            return True
        return False
    except Exception:
        return False


def delete_file(filename: str, user_id: str, page_id: str = None, is_temp: bool = True) -> bool:
    """Удаляет файл"""
    try:
        if is_temp:
            file_path = os.path.join(config.get_temp_folder_path(user_id, page_id), filename)
        else:
            file_path = os.path.join(config.get_permanent_folder_path(user_id, page_id), filename)
        
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception:
        return False


def get_file_url(filename: str, user_id: str, page_id: str = None, is_temp: bool = True) -> str:
    """Генерирует URL для доступа к файлу"""
    # В реальном приложении здесь должен быть полный URL
    # Для упрощения возвращаем относительный путь
    if is_temp:
        if page_id:
            return f"/media/temp/{user_id}/{page_id}/{filename}"
        else:
            return f"/media/temp/{user_id}/{filename}"
    else:
        if page_id:
            return f"/media/permanent/{user_id}/{page_id}/{filename}"
        else:
            return f"/media/permanent/{user_id}/{filename}"


def cleanup_old_temp_files(hours_old: int = 24) -> int:
    """Удаляет старые временные файлы"""
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_old)
        deleted_count = 0
        
        # Рекурсивно обходим все папки в temp
        for root, dirs, files in os.walk(config.TEMP_BASE_FOLDER):
            for filename in files:
                file_path = os.path.join(root, filename)
                try:
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    if file_mtime < cutoff_time:
                        os.remove(file_path)
                        deleted_count += 1
                except Exception:
                    continue
        
        return deleted_count
    except Exception:
        return 0


def get_file_path(filename: str, user_id: str, page_id: str = None, is_temp: bool = True) -> str:
    """Получает полный путь к файлу"""
    if is_temp:
        return os.path.join(config.get_temp_folder_path(user_id, page_id), filename)
    else:
        return os.path.join(config.get_permanent_folder_path(user_id, page_id), filename)