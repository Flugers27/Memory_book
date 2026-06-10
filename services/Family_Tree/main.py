"""
ГЛАВНЫЙ ФАЙЛ СЕРВИСА FAMILY TREE
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

from .config import config
from .routers import family_router, health_router

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
    """Контекст жизненного цикла приложения"""
    logger.info(f"{config.SERVICE_NAME} запущен на порту {config.SERVICE_PORT}")
    yield
    logger.info(f"{config.SERVICE_NAME} остановлен")


# Создаем FastAPI приложение
app = FastAPI(
    title="Family Tree Service API",
    description="Сервис для создания и управления генеалогическими древами",
    version="1.0.0",
    lifespan=lifespan
)

# Настраиваем CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(family_router)
app.include_router(health_router)


@app.get("/")
async def root():
    """Корневой эндпоинт с информацией о сервисе"""
    return {
        "service": config.SERVICE_NAME,
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "trees": {
                "create": "POST /family/tree",
                "my_list": "GET /family/tree/my",
                "get": "GET /family/tree/{tree_id}",
                "update": "PUT /family/tree/{tree_id}",
                "delete": "DELETE /family/tree/{tree_id}"
            },
            "public_trees": {
                "list": "GET /family/tree/public",
                "get": "GET /family/tree/public/{tree_id}"
            },
            "agents": {
                "add": "POST /family/tree/{tree_id}/agent",
                "remove": "DELETE /family/tree/{tree_id}/agent/{agent_id}"
            },
            "relationships": {
                "list": "GET /family/tree/{tree_id}/relationship",
                "create": "POST /family/tree/{tree_id}/relationship",
                "update": "PUT /family/tree/{tree_id}/relationship/{rel_id}",
                "delete": "DELETE /family/tree/{tree_id}/relationship/{rel_id}"
            },
            "health": "GET /health"
        }
    }


if __name__ == "__main__":
    logger.info(f"Запуск {config.SERVICE_NAME} на {config.HOST}:{config.SERVICE_PORT}")
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.SERVICE_PORT,
        reload=config.DEBUG,
        log_level="info"
    )