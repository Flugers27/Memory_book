"""
КОНФИГУРАЦИЯ СЕРВИСА MEDIA
"""
import os
import sys
from dotenv import load_dotenv

# Добавляем путь для импорта корневого конфига
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from config import config as base_config

load_dotenv()

class MediaConfig:
    """Конфигурация сервиса медиа"""
    
    # Наследуем базовые настройки
    SECRET_KEY = base_config.SECRET_KEY
    ALGORITHM = base_config.ALGORITHM
    CORS_ORIGINS = base_config.CORS_ORIGINS
    
    # Специфичные для Media настройки
    SERVICE_PORT = int(os.getenv("MEDIA_PORT", 8004))
    SERVICE_NAME = "media-service"
    HOST = os.getenv("MEDIA_HOST", "0.0.0.0")
    DEBUG = os.getenv("MEDIA_DEBUG", "False").lower() == "true"
    
    # Настройки загрузки файлов
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 50 * 1024 * 1024))  # 50 MB по умолчанию
    ALLOWED_EXTENSIONS = {
        'image': ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'],
        'video': ['mp4', 'mov', 'avi', 'mkv', 'webm'],
        'audio': ['mp3', 'wav', 'ogg', 'm4a'],
        'document': ['pdf', 'doc', 'docx', 'txt', 'md']
    }
    
    # Пути для хранения файлов
    BASE_DATA_MEDIA = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data_media")
    TEMP_BASE_FOLDER = os.path.join(BASE_DATA_MEDIA, "temp")
    PERMANENT_BASE_FOLDER = os.path.join(BASE_DATA_MEDIA, "permanent")
    
    @staticmethod
    def get_temp_folder_path(user_id: str, page_id: str = None) -> str:
        """Получает путь к папке для временных файлов пользователя"""
        if page_id:
            return os.path.join(MediaConfig.TEMP_BASE_FOLDER, user_id, page_id)
        return os.path.join(MediaConfig.TEMP_BASE_FOLDER, user_id)
    
    @staticmethod
    def get_permanent_folder_path(user_id: str, page_id: str = None) -> str:
        """Получает путь к папке для постоянных файлов пользователя"""
        if page_id:
            return os.path.join(MediaConfig.PERMANENT_BASE_FOLDER, user_id, page_id)
        return os.path.join(MediaConfig.PERMANENT_BASE_FOLDER, user_id)
    
    # Время жизни временных файлов (в часах)
    TEMP_FILE_LIFETIME = int(os.getenv("TEMP_FILE_LIFETIME", 24))
    
    # Пагинация
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100

# Создаем экземпляр конфигурации
config = MediaConfig()