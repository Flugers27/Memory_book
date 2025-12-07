from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

app = FastAPI(
    title="Memory Book Service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "service": "Memory Book API",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "auth": "/api/v1/auth",
            "users": "/api/v1/users"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Memory Book"}

# Импортируем и регистрируем роуты
try:
    from src.services.auth.router import router as auth_router
    from src.services.user.router import router as user_router
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["authentication"])
    app.include_router(user_router, prefix="/api/v1/users", tags=["users"])
    print("✅ Роуты успешно загружены")
except ImportError as e:
    print(f"⚠️  Не удалось загрузить роуты: {e}")
    print("Запускаем базовую версию API...")

if __name__ == "__main__":
    print("🚀 Запуск Memory Book Service на http://localhost:8000")
    print("📚 Документация: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)