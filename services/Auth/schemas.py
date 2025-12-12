"""
Pydantic схемы для валидации данных.
Используются для входящих запросов и исходящих ответов.
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
import uuid

class UserBase(BaseModel):
    """Базовая схема пользователя"""
    email: EmailStr
    username: Optional[str] = None
    full_name: Optional[str] = None

class UserCreate(UserBase):
    """Схема для создания пользователя (регистрация)"""
    password: str = Field(..., min_length=3, max_length=100)

class UserLogin(BaseModel):
    """Схема для входа пользователя"""
    email: EmailStr
    password: str

class UserResponse(UserBase):
    """Схема ответа с информацией о пользователе"""
    id_user: uuid.UUID
    is_active: bool
    is_verified: bool
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode  = True  # В Pydantic v2 заменил orm_mode=True

class Token(BaseModel):
    """Схема ответа с токенами"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshTokenRequest(BaseModel):
    """Схема запроса для обновления токена"""
    refresh_token: str

class PasswordUpdate(BaseModel):
    """Схема для обновления пароля"""
    current_password: str
    new_password: str = Field(..., min_length=4, max_length=100)