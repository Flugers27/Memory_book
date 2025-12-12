"""
ГЛАВНЫЙ ФАЙЛ СЕРВИСА АВТОРИЗАЦИИ
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
import os

# Добавляем корень проекта в путь Python
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Импортируем из корневого config.py
try:
    from config import engine, User, RefreshToken, create_tables, CORS_ORIGINS
    print("✅ Успешно импортировано из config.py")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print(f"   Путь Python: {sys.path}")
    raise

# Импортируем роутеры
from .routers import auth, users, health
from .config import config as auth_config

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Контекст жизненного цикла приложения.
    Создает таблицы при запуске, закрывает подключения при завершении.
    """
    # Создаем таблицы в базе данных
    create_tables()
    print("🚀 Сервис авторизации запущен")
    
    yield  # Приложение работает
    
    # Очищаем подключения при завершении
    engine.dispose()
    print("👋 Сервис авторизации остановлен")

# Создаем FastAPI приложение
app = FastAPI(
    title="Auth Service API",
    description="Сервис аутентификации и авторизации для Memory Book",
    version="1.0.0",
    lifespan=lifespan
)

# Настраиваем CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(health.router)

@app.get("/")
async def root():
    """Корневой эндпоинт с информацией о сервисе"""
    return {
        "service": "Auth Service",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "register": "POST /auth/register",
            "login": "POST /auth/login",
            "refresh": "POST /auth/refresh",
            "logout": "POST /auth/logout",
            "user_info": "GET /users/me",
            "health": "GET /health"
        }
    }