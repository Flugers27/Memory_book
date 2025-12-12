"""
Подключение к базе данных PostgreSQL.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# URL базы данных
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://wb:admin@localhost/memory_book_UAT"
)

# Создаем движок SQLAlchemy
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Базовый класс для моделей
Base = declarative_base()

# Фабрика сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)