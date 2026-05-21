"""
Главный файл сервиса Media
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import sys

# Добавляем путь для импорта корневого конфига
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from config import config as base_config
from .config import config
from .routers import media, health
from .utils import ensure_base_directories


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Контекстный менеджер для управления жизненным циклом приложения.
    Выполняется при запуске и остановке сервиса.
    """
    # При запуске: создаем необходимые директории
    print(f"Starting {config.SERVICE_NAME} on port {config.SERVICE_PORT}...")
    ensure_base_directories()
    print(f"Base directories created: {config.TEMP_BASE_FOLDER}, {config.PERMANENT_BASE_FOLDER}")
    
    yield
    
    # При остановке: выполняем очистку
    print(f"Stopping {config.SERVICE_NAME}...")


# Создаем экземпляр FastAPI приложения
app = FastAPI(
    title="Media Service API",
    description="Сервис для загрузки и управления медиафайлами",
    version="1.0.0",
    lifespan=lifespan
)

# Настраиваем CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(media.router)
app.include_router(health.router)


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "service": config.SERVICE_NAME,
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "upload": "/media/upload",
            "my_temp_media": "/media/temp/my",
            "health": "/health"
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.SERVICE_PORT,
        reload=config.DEBUG,
        log_level="info"
    )