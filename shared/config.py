"""
Конфигурация API Gateway
"""
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

class Settings:
    # Основные настройки Gateway
    APP_NAME = "Memory Book API Gateway"
    VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Порт Gateway
    HOST = os.getenv("GATEWAY_HOST", "0.0.0.0")
    PORT = int(os.getenv("GATEWAY_PORT", "8000"))
    
    # URL микросервисов
    AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
    MEMORY_SERVICE_URL = os.getenv("MEMORY_SERVICE_URL", "http://localhost:8002")
    ACCESS_SERVICE_URL = os.getenv("ACCESS_SERVICE_URL", "http://localhost:8003")
    
    # JWT настройки (должны совпадать с Auth сервисом)
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-key-change-in-production")
    JWT_ALGORITHM = "HS256"
    
    # Настройки безопасности
    CORS_ORIGINS = [
        "http://localhost:3000",  # React frontend
        "http://localhost:8080",  # Vue frontend
        "http://localhost:8000",  # Gateway itself
    ]
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE = 60
    
    # Timeout для запросов к сервисам (секунды)
    SERVICE_TIMEOUT = 10.0
    
    # Пути, которые не требуют аутентификации
    PUBLIC_PATHS = [
        "/auth/login",
        "/auth/register",
        "/auth/refresh",
        "/auth/docs",
        "/auth/redoc",
        "/auth/openapi.json",
        "/memory/public/",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/health",
    ]
    
    # Сопоставление сервисов с путями
    SERVICE_ROUTES = {
        "auth": AUTH_SERVICE_URL,
        "memory": MEMORY_SERVICE_URL,
        "access": ACCESS_SERVICE_URL,
    }
    
    # Логирование
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = "logs/gateway.log"

settings = Settings()