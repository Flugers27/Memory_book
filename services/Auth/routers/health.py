"""
Маршруты для проверки здоровья сервиса.
"""
from fastapi import APIRouter
from datetime import datetime

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check():
    """
    Проверка доступности сервиса.
    """
    return {
        "status": "healthy",
        "service": "Auth",
        "timestamp": datetime.utcnow().isoformat()
    }