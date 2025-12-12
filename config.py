"""
КОРНЕВОЙ КОНФИГУРАЦИОННЫЙ ФАЙЛ
Содержит настройки БД, модели и подключения.
ВСЕ В ОДНОМ ФАЙЛЕ!
"""

import os
import uuid
from sqlalchemy import create_engine, Column, String, Boolean, DateTime, Text, ForeignKey, Date, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from dotenv import load_dotenv

load_dotenv()

# ========== НАСТРОЙКИ ==========
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://wb:admin@localhost/memory_book_UAT"
)

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))
BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", 12))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")

# ========== ПОДКЛЮЧЕНИЕ К БД ==========
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Зависимость для получения сессии базы данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ========== МОДЕЛЬ ПОЛЬЗОВАТЕЛЯ ==========
class User(Base):
    __tablename__ = "users"
    
    id_user = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, index=True)
    full_name = Column(String(100))
    avatar_url = Column(Text)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# ========== МОДЕЛЬ REFRESH TOKEN ==========
class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    __table_args__ = {'schema': 'sys'}
    
    id_user_token = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id_user"), nullable=False, index=True)
    token_hash = Column(String(512), nullable=False)
    device_info = Column(Text)
    ip_address = Column(String(50))
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# ========== ФУНКЦИЯ СОЗДАНИЯ ТАБЛИЦ ==========
def create_tables():
    """Создает все таблицы в БД"""
    Base.metadata.create_all(bind=engine)
    print("✅ Таблицы базы данных созданы")

# В конец файла config.py добавь:

# ========== МОДЕЛЬ MEMORY AGENT ==========
class MemoryAgent(Base):
    __tablename__ = "memory_agent"
    
    id_agent = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    full_name = Column(String(255), nullable=False)
    birth_date = Column(Date)
    death_date = Column(Date)
    avatar_url = Column(Text)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id_user"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Связи
    user = relationship("User")
    memory_pages = relationship("MemoryPage", back_populates="memory_agent")

# ========== МОДЕЛЬ MEMORY PAGE ==========
class MemoryPage(Base):
    __tablename__ = "memory_page"
    
    id_page = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    epitaph = Column(Text)
    place_of_birth = Column(String(500))
    place_of_death = Column(String(500))
    is_public = Column(Boolean, default=False, nullable=False)
    is_draft = Column(Boolean, default=False, nullable=False)
    memory_agent_id = Column(UUID(as_uuid=True), ForeignKey("memory_agent.id_agent"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id_user"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Связи
    user = relationship("User")
    memory_agent = relationship("MemoryAgent", back_populates="memory_pages")
    memory_titles = relationship("MemoryTitles", back_populates="memory_page")

# ========== МОДЕЛЬ MEMORY TITLES ==========
class MemoryTitles(Base):
    __tablename__ = "memory_titles"
    
    id_titles = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    head = Column(String(100), nullable=False)
    body = Column(Text)
    page_id = Column(UUID(as_uuid=True), ForeignKey("memory_page.id_page"), nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    sort_order = Column(Integer, default=0)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("memory_titles.id_titles"))
    
    # Связи
    memory_page = relationship("MemoryPage", back_populates="memory_titles")
    parent = relationship("MemoryTitles", remote_side=[id_titles], backref="children")

# ========== ОБНОВЛЕННАЯ ФУНКЦИЯ СОЗДАНИЯ ТАБЛИЦ ==========
def create_tables():
    """Создает все таблицы в БД"""
    Base.metadata.create_all(bind=engine)
    print("✅ Все таблицы базы данных созданы")