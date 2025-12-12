"""
ГЛАВНЫЙ ФАЙЛ СЕРВИСА ПАМЯТИ
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .routers import agents, pages, titles, memory_pages, health  # Изменено здесь

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
    description="Сервис для управления страницами памяти, агентами и заголовками",
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
app.include_router(pages.router)
app.include_router(titles.router)
app.include_router(memory_pages.router)  # Изменено здесь
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
            "agents": {
                "list": "GET /agents",
                "create": "POST /agents",
                "get": "GET /agents/{agent_id}",
                "update": "PUT /agents/{agent_id}",
                "delete": "DELETE /agents/{agent_id}"
            },
            "pages": {
                "list": "GET /pages",
                "public": "GET /pages/public",
                "create": "POST /pages",
                "get": "GET /pages/{page_id}",
                "update": "PUT /pages/{page_id}",
                "delete": "DELETE /pages/{page_id}"
            },
            "titles": {
                "list": "GET /titles/page/{page_id}",
                "create_single": "POST /titles",
                "create_batch": "POST /titles/batch",
                "get": "GET /titles/{title_id}",
                "update": "PUT /titles/{title_id}",
                "delete": "DELETE /titles/{title_id}"
            },
            "memory_pages": {  # Изменено здесь
                "create_all": "POST /memory-pages/create",
                "quick_create": "POST /memory-pages/quick-create",
                "get_all": "GET /memory-pages/page/{page_id}",
                "update_all": "PUT /memory-pages/page/{page_id}"
            },
            "health": "GET /health"
        }
    }