"""
Роутеры сервиса памяти
"""
#from .pages import router as pages_router
from .agents import router as agents_router
from .health import router as health_router
from .memory_pages import router as memory_pages_router 

__all__ = [ "agents_router","memory_pages_router", "health_router"] #"pages_router",