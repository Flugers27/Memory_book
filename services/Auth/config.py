"""
КОНФИГУРАЦИЯ СЕРВИСА АВТОРИЗАЦИИ
"""
import os
import sys
from datetime import timedelta
from dotenv import load_dotenv

# Добавляем путь для импорта корневого конфига
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from config import config as base_config

load_dotenv()

class AuthConfig:
    """Конфигурация сервиса авторизации"""
    
    # Наследуем базовые настройки
    SECRET_KEY = base_config.SECRET_KEY
    ALGORITHM = base_config.ALGORITHM
    CORS_ORIGINS = base_config.CORS_ORIGINS
    
    # Специфичные для Auth настройки
    SERVICE_PORT = int(os.getenv("AUTH_PORT", 8001))
    SERVICE_NAME = "auth-service"
    
    # Сроки действия токенов
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))
    BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", 12))
    
    # Безопасность
    PASSWORD_MIN_LENGTH = 8
    ALLOW_LOGIN_ATTEMPTS = 5

    # Логирование
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = "logs/auth_service.log"
    
    @property
    def ACCESS_TOKEN_EXPIRE(self) -> timedelta:
        return timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    @property
    def REFRESH_TOKEN_EXPIRE(self) -> timedelta:
        return timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)

# Создаем экземпляр конфигурации
config = AuthConfig()