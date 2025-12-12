"""
Логика аутентификации: JWT, хеширование паролей, проверка токенов.
"""
from datetime import datetime, timedelta
from typing import Optional
import uuid
import sys
import os
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

# Добавляем корень проекта в путь
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Импортируем из корневого config.py
from config import User, RefreshToken, SECRET_KEY, ALGORITHM, BCRYPT_ROUNDS
from .config import config

# Контекст для хеширования паролей
pwd_context = CryptContext(schemes=["argon2"],deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет совпадение пароля с хешем"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Создает хеш пароля"""
    return pwd_context.hash(password)

def create_access_token(user_id: uuid.UUID, email: str) -> str:
    """Создает JWT access токен"""
    to_encode = {
        "sub": str(user_id),
        "email": email,
        "type": "access"
    }
    expire = datetime.utcnow() + config.ACCESS_TOKEN_EXPIRE
    to_encode.update({"exp": expire})
    
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(user_id: uuid.UUID, email: str) -> str:
    """Создает JWT refresh токен"""
    to_encode = {
        "sub": str(user_id),
        "email": email,
        "type": "refresh"
    }
    expire = datetime.utcnow() + config.REFRESH_TOKEN_EXPIRE
    to_encode.update({"exp": expire})
    
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str, token_type: str = "access") -> dict:
    """
    Проверяет JWT токен и возвращает payload
    Вызывает исключение если токен невалидный
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        if payload.get("type") != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token type, expected {token_type}"
            )
        
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Проверяет email и пароль, возвращает пользователя если успешно"""
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    if not user.is_active:
        return None
    
    return user

def save_refresh_token(db: Session, user_id: uuid.UUID, refresh_token: str, 
                      device_info: str = None, ip_address: str = None) -> RefreshToken:
    """Сохраняет refresh токен в базу данных"""
    # Удаляем старые токены для этого устройства
    if device_info:
        db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id,
            RefreshToken.device_info == device_info
        ).delete()
    
    # Создаем новый токен
    expires_at = datetime.utcnow() + config.REFRESH_TOKEN_EXPIRE
    db_token = RefreshToken(
        user_id=user_id,
        token_hash=get_password_hash(refresh_token),
        device_info=device_info,
        ip_address=ip_address,
        expires_at=expires_at
    )
    
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token

def verify_refresh_token(db: Session, refresh_token: str, user_id: uuid.UUID) -> bool:
    """Проверяет, существует ли refresh токен в базе"""
    db_token = db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        RefreshToken.expires_at > datetime.utcnow()
    ).first()
    
    if not db_token:
        return False
    
    return verify_password(refresh_token, db_token.token_hash)