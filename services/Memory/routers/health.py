"""
Роутер для проверки здоровья сервиса памяти
"""
from fastapi import APIRouter
from datetime import datetime

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check():
    """Проверка здоровья сервиса памяти"""
    return {
        "status": "healthy",
        "service": "Memory",
        "timestamp": datetime.utcnow().isoformat()
    }