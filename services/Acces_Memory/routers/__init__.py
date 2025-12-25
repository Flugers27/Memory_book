"""
Роутеры сервиса управления доступом.
"""
from .access import router as access_router
from .health import router as health_router

__all__ = ["access_router", "health_router"]