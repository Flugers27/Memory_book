"""
КОНФИГУРАЦИЯ СЕРВИСА ПАМЯТИ
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

class MemoryConfig:
    # Можно добавить специфичные настройки для этого сервиса
    PAGE_DEFAULT_LIMIT = int(os.getenv("PAGE_DEFAULT_LIMIT", 50))
    AGENT_DEFAULT_LIMIT = int(os.getenv("AGENT_DEFAULT_LIMIT", 50))
    TITLE_DEFAULT_LIMIT = int(os.getenv("TITLE_DEFAULT_LIMIT", 100))
    
    # Настройки пагинации
    MAX_PAGE_SIZE = 100
    
    # Настройки фильтрации
    ALLOWED_SORT_FIELDS = ["created_at", "updated_at", "sort_order"]

# Настройки базы данных
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://wb:admin@localhost/memory_book_UAT")

# Создаем движок базы данных
engine = create_engine(DATABASE_URL)

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()

# Dependency для получения сессии базы данных
def get_db():
    """
    Зависимость для получения сессии базы данных.
    Используется в Depends() в эндпоинтах.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Создаем экземпляр конфигурации
config = MemoryConfig()