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
    
    # JWT настройки (должны совпадать с Auth сервисом)
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-key-change-in-production")
    JWT_ALGORITHM = "HS256"
    
    # Настройки безопасности
    CORS_ORIGINS = [
        "http://localhost:3000",  # React frontend
        "http://127.0.0.1:3000",  # React frontend (IP)
        "http://localhost:3001",  # React frontend (port 3001)
        "http://localhost:8080",  # Vue frontend
        "http://localhost:5173",
        "http://localhost:8000",  # Gateway itself
        "http://172.27.136.127:3000",  # Frontend on network IP (port 3000)
        "http://172.27.136.127:3001",  # Frontend on network IP (port 3001)
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
        "/memory/public_memory_page_list",
        "/memory/public_memory_page/",
        "/memory/public_memory_page",
        "/memory/agent/",
        "/memory/page_list/",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/health",
    ]
    
    # Сопоставление сервисов с путями
    SERVICE_ROUTES = {
        "auth": AUTH_SERVICE_URL,
        "memory": MEMORY_SERVICE_URL,
        "agent": MEMORY_SERVICE_URL,
        "page": MEMORY_SERVICE_URL,
    }
    
    # Логирование
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = "logs/gateway.log"

settings = Settings()