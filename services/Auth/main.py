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

# Импортируем из КОРНЕВОГО config.py
try:
    from config import engine, create_tables, CORS_ORIGINS
    print("✅ Успешно импортировано из корневого config.py")
except ImportError as e:
    print(f"❌ Ошибка импорта корневого config: {e}")
    raise

# Импортируем из ЛОКАЛЬНОГО config.py в папке Auth
try:
    from services.Auth.config import config as auth_config
    print("✅ Успешно импортировано из auth config")
except ImportError as e:
    print(f"❌ Ошибка импорта auth config: {e}")
    # Создаем дефолтную конфигурацию
    class AuthConfig:
        JWT_SECRET_KEY = "default-secret-key-change-in-production"
        JWT_ALGORITHM = "HS256"
        ACCESS_TOKEN_EXPIRE_MINUTES = 30
        REFRESH_TOKEN_EXPIRE_DAYS = 7
    
    auth_config = AuthConfig()
    print("⚠️  Используется дефолтная конфигурация Auth")

# Импортируем роутеры
try:
    from services.Auth.routers import auth, users, health
    print("✅ Успешно импортированы роутеры")
except ImportError as e:
    print(f"❌ Ошибка импорта роутеров: {e}")
    raise

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
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(health.router, prefix="/health", tags=["health"])

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)