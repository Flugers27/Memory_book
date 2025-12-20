"""
КОНФИГУРАЦИЯ СЕРВИСА ПАМЯТИ
"""
import os
import sys
from datetime import timedelta
from dotenv import load_dotenv

# Добавляем путь для импорта корневого конфига
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from config import config as base_config

load_dotenv()

class MemoryConfig:
    """Конфигурация сервиса памяти"""
    
    # Наследуем базовые настройки
    SECRET_KEY = base_config.SECRET_KEY
    ALGORITHM = base_config.ALGORITHM
    CORS_ORIGINS = base_config.CORS_ORIGINS
    
    # Специфичные для Memory настройки
    SERVICE_PORT = int(os.getenv("MEMORY_PORT", 8002))
    SERVICE_NAME = "memory-service"
    
    # Пагинация
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    # Файлы
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "./uploads")
    MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # URL других сервисов
    AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
    
    # Время жизни кэша
    CACHE_TTL = 300  # 5 минут

    # Логирование
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = "logs/memory_service.log"

# Создаем экземпляр конфигурации
config = MemoryConfig()