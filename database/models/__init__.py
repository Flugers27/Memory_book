"""
Пакет для работы с базой данных.
"""
from .engine import engine, get_engine
from .session import SessionLocal, get_db, get_session
from .base import Base, BaseModel

__all__ = [
    # Подключение
    'engine', 'get_engine',
    
    # Сессии
    'SessionLocal', 'get_db', 'get_session',
    
    # Базовые классы
    'Base', 'BaseModel',
]

def create_tables():
    """Создает все таблицы в базе данных"""
    from .base import Base
    
    # Импортируем все модели, чтобы они зарегистрировались
    try:
        from services.Auth.models import User, RefreshToken
        print("✅ Модели Auth сервиса импортированы")
    except ImportError as e:
        print(f"⚠️  Не удалось импортировать модели Auth: {e}")
    
    try:
        from services.Memory.models import AgentBD, PageBD, MemoryTitles
        print("✅ Модели Memory сервиса импортированы")
    except ImportError as e:
        print(f"⚠️  Не удалось импортировать модели Memory: {e}")
    
    # Создаем таблицы
    Base.metadata.create_all(bind=engine)
    print("✅ Все таблицы базы данных созданы")