"""
Управление сессиями БД.
"""
from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker, Session
from .engine import engine

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    class_=Session,
)

def get_db():
    """
    Dependency для FastAPI.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

@contextmanager
def session_scope():
    """
    Контекстный менеджер для использования вне FastAPI.
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
