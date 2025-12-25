"""
Конфигурация сервиса управления доступом.
"""
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from config import config as base_config

load_dotenv()

class AccessConfig:
    """Конфигурация сервиса доступа"""
    
    # Наследуем базовые настройки
    SECRET_KEY = base_config.SECRET_KEY
    ALGORITHM = base_config.ALGORITHM
    CORS_ORIGINS = base_config.CORS_ORIGINS
    
    # Специфичные настройки
    SERVICE_PORT = int(os.getenv("ACCESS_PORT", 8003))
    SERVICE_NAME = "access-service"
    
    # Пагинация
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    # Логирование
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = "logs/access_service.log"

# Создаем экземпляр конфигурации
config = AccessConfig()