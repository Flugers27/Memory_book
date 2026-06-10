"""
Главный файл сервиса управления доступом.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .config import config
import logging

from .routers import access_router, health_router

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Контекст жизненного цикла приложения.
    """
    print("🚀 Сервис управления доступом запущен")
    
    yield  # Приложение работает
    
    print("👋 Сервис управления доступом остановлен")

# Создаем FastAPI приложение
app = FastAPI(
    title="Access Management Service API",
    description="Сервис для управления доступом к страницам памяти",
    version="1.0.0",
    lifespan=lifespan
)

# Настраиваем CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(access_router)
app.include_router(health_router)

@app.get("/")
async def root():
    """Корневой эндпоинт с информацией о сервисе"""
    return {
        "service": "Access Management Service",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "access": {
                "my": "GET /access/my",
                "granted": "GET /access/granted",
                "grant": "POST /access/grant",
                "revoke": "DELETE /access/{access_id}",
            }
        }
    }


if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting Access Management Service on 0.0.0.0:{config.SERVICE_PORT}")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=config.SERVICE_PORT,
        reload=config.DEBUG,
        log_level="info"
    )