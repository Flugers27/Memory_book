"""
Pydantic схемы для валидации данных.
"""
from pydantic import BaseModel, EmailStr, Field, validator, ConfigDict
from typing import Optional
from datetime import datetime
import uuid

class UserBase(BaseModel):
    """Базовая схема пользователя"""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    class Config:
        orm_mode = True

class UserCreate(UserBase):
    """Схема для создания пользователя"""
    email: EmailStr
    password: str = Field(..., min_length=3, max_length=100)
    
    @validator('password')
    def validate_password(cls, v):
        # if len(v) < 8:
        #     raise ValueError('Password must be at least 8 characters long')
        # if not any(c.isupper() for c in v):
        #     raise ValueError('Password must contain at least one uppercase letter')
        # if not any(c.islower() for c in v):
        #     raise ValueError('Password must contain at least one lowercase letter')
        # if not any(c.isdigit() for c in v):
        #     raise ValueError('Password must contain at least one digit')
        return v

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
    
    # Конфигурация для Pydantic v2
    model_config = ConfigDict(from_attributes=True)

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
    new_password: str = Field(..., min_length=3, max_length=100)
    
    @validator('new_password')
    def validate_new_password(cls, v):
        # if len(v) < 8:
        #     raise ValueError('Password must be at least 8 characters long')
        # if not any(c.isupper() for c in v):
        #     raise ValueError('Password must contain at least one uppercase letter')
        # if not any(c.islower() for c in v):
        #     raise ValueError('Password must contain at least one lowercase letter')
        # if not any(c.isdigit() for c in v):
        #     raise ValueError('Password must contain at least one digit')
        return v

class TokenValidationResponse(BaseModel):
    """Схема ответа для валидации токена"""
    valid: bool
    user_id: Optional[str] = None
    email: Optional[str] = None
    expires_at: Optional[int] = None
    error: Optional[str] = None