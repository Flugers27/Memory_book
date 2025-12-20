"""
Пакет работы с базой данных.
"""
from .engine import engine, get_engine
from .session import SessionLocal, get_db, session_scope
from .base import Base, BaseModel

__all__ = [
    "engine",
    "get_engine",
    "SessionLocal",
    "get_db",
    "session_scope",
    "Base",
    "BaseModel",
]

def create_tables_dev():
    """
    Создание таблиц ТОЛЬКО для dev среды.
    В проде использовать Alembic.
    """
    import os

    if os.getenv("DEBUG", "false").lower() != "true":
        raise RuntimeError("create_tables_dev разрешён только в DEBUG режиме")

    Base.metadata.create_all(bind=engine)
    print("✅ Таблицы созданы (DEV)")
