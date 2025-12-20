"""
Модели для сервиса авторизации.
"""
from sqlalchemy import Column, String, Boolean, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from ..base import BaseModel

class User(BaseModel):
    __tablename__ = "users"
    
    # Переопределяем id чтобы использовать ваше имя поля
    id_user = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, index=True)
    full_name = Column(String(100))
    avatar_url = Column(Text)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login_at = Column(DateTime(timezone=True))
    
    # Убираем дублирующиеся created_at, updated_at - они уже в BaseModel

class RefreshToken(BaseModel):
    __tablename__ = "refresh_tokens"
    __table_args__ = {'schema': 'sys'}
    
    id_user_token = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    token_hash = Column(String(512), nullable=False)
    device_info = Column(Text)
    ip_address = Column(String(50))
    expires_at = Column(DateTime(timezone=True), nullable=False)