"""
Health-check для сервиса Family Tree
"""
from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Проверка состояния сервиса"""
    return {
        "status": "healthy",
        "service": "family-tree",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }