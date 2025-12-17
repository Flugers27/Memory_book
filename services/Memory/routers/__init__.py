"""
Роутеры сервиса памяти
"""
#from .pages import router as pages_router
from .agents import router as agents_router
from .pages import router as page_router
from .memory_pages import router as memory_pages_router 
from .health import router as health_router

__all__ = [ "agents_router","memory_pages_router", "health_router", "page_router"] #"pages_router",