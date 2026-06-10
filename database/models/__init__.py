"""
Пакет для работы с базой данных.
"""
from ..engine import engine, get_engine
from ..session import SessionLocal, get_db


__all__ = [
    # Подключение
    'engine', 'get_engine',
    
    # Сессии
    'SessionLocal', 'get_db',
    
    # Базовые классы
    'Base', 'BaseModel',
]

def create_tables():
    """Создает все таблицы в базе данных"""
    from .base import Base
    
    # Импортируем все модели, чтобы они зарегистрировались
    try:
        from database.models.auth import User, UserRole, RefreshToken, EmailVerificationToken
        print("✅ Модели Auth сервиса импортированы")
    except ImportError as e:
        print(f"⚠️  Не удалось импортировать модели Auth: {e}")
    
    try:
        from database.models.memory import AgentBD, PageBD
        print("✅ Модели Memory сервиса импортированы")
    except ImportError as e:
        print(f"⚠️  Не удалось импортировать модели Memory: {e}")
    
    try:
        from database.models.media import MediaBD
        print("✅ Модели Media сервиса импортированы")
    except ImportError as e:
        print(f"⚠️  Не удалось импортировать модели Media: {e}")
    
    try:
        from database.models.access import PageAccessControl
        print("✅ Модели Access сервиса импортированы")
    except ImportError as e:
        print(f"⚠️  Не удалось импортировать модели Access: {e}")
    
    try:
        from database.models.family import FamilyTree, FamilyTreeAgent, RelationshipAgent
        print("✅ Модели Family сервиса импортированы")
    except ImportError as e:
        print(f"⚠️  Не удалось импортировать модели Family: {e}")
    
    # Создаем таблицы
    Base.metadata.create_all(bind=engine)
    print("✅ Все таблицы базы данных созданы")