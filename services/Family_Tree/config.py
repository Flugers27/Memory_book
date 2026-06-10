"""
КОНФИГУРАЦИЯ СЕРВИСА FAMILY TREE
"""
import os
import sys
from dotenv import load_dotenv

# Добавляем путь для импорта корневого конфига
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from config import config as base_config

load_dotenv()

class FamilyTreeConfig:
    """Конфигурация сервиса семейного древа"""
    
    # Наследуем базовые настройки
    SECRET_KEY = base_config.SECRET_KEY
    ALGORITHM = base_config.ALGORITHM
    CORS_ORIGINS = base_config.CORS_ORIGINS
    
    # Специфичные для Family Tree настройки
    SERVICE_PORT = int(os.getenv("FAMILY_PORT", 8005))
    SERVICE_NAME = "family-tree-service"
    HOST = os.getenv("FAMILY_HOST", "0.0.0.0")
    DEBUG = os.getenv("FAMILY_DEBUG", "False").lower() == "true"
    
    # Пагинация
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    # Логирование
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = "logs/family_tree_service.log"

# Создаем экземпляр конфигурации
config = FamilyTreeConfig()