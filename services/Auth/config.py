"""
КОНФИГУРАЦИЯ СЕРВИСА АВТОРИЗАЦИИ
Специфичные настройки для этого сервиса
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class AuthConfig:
    # JWT настройки
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM = "HS256"
    
    # Сроки действия токенов
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))
    
    # Настройки безопасности
    BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", 12))
    
    @property
    def ACCESS_TOKEN_EXPIRE(self) -> timedelta:
        return timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    @property
    def REFRESH_TOKEN_EXPIRE(self) -> timedelta:
        return timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)

# Создаем экземпляр конфигурации
config = AuthConfig()