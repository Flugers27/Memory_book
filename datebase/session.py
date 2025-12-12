"""
Управление сессиями базы данных.
"""
from .connection import SessionLocal
from sqlalchemy.orm import Session

def get_db():
    """
    Зависимость для получения сессии базы данных.
    Используется в FastAPI Depends().
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()