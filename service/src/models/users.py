from sqlalchemy import Column, String, Boolean, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

from src.models.base import Base

class User(Base):
    """Модель пользователя (соответствует вашей таблице users)"""
    __tablename__ = "users"
    __table_args__ = {"schema": "public"}
    
    id_user = Column(
        "id_user",
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )
    email = Column(String(255), nullable=False, unique=True, index=True)
    username = Column(String(100), unique=True, index=True)
    full_name = Column(String(100))  # У вас 100 символов, не 255
    avatar_url = Column(String)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), server_default=text("now()"))