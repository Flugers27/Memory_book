"""
ГЛАВНЫЙ ФАЙЛ СЕРВИСА ПАМЯТИ
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .routers import agents, memory_pages, health  # Изменено здесь  pages

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Контекст жизненного цикла приложения.
    """
    from config import create_tables
    # Создаем таблицы в базе данных (если еще не созданы)
    create_tables()
    print("🚀 Сервис памяти запущен")
    
    yield  # Приложение работает
    
    print("👋 Сервис памяти остановлен")

# Создаем FastAPI приложение
app = FastAPI(
    title="Memory Service API",
    description="Сервис для управления страницами памяти",
    version="1.0.0",
    lifespan=lifespan
)

# Настраиваем CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Временно разрешаем все для тестирования
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(agents.router)
app.include_router(memory_pages.router)
#app.include_router(pages.router)
app.include_router(health.router)

@app.get("/")
async def root():
    """Корневой эндпоинт с информацией о сервисе"""
    return {
        "service": "Memory Service",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "memory_page": {
                "p_list": "Get /public_memory_page_list",
                "p_get": "Get /public_memory_page/{page_id}",
                "list": "Get /memory_page_list",
                "get": "Get /memory_page/{page_id}",
            },
            "agent": {
                "list": "GET /agent_list",
                "get": "GET /agent/{agent_id}",
                "create": "POST /agent",
                "update": "PUT /agent/{agent_id}",
                "delete": "DELETE /agent/{agent_id}"
            },
            "page": {
                "list": "GET /page_list",
                "create": "POST /page",
                "get": "GET /page/{page_id}",
                "update": "PUT /page/{page_id}",
                "delete": "DELETE /page/{page_id}"
            },
            "health": "GET /health"
        }
    }