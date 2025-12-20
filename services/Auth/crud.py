"""
CRUD операции для работы с базой данных.
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
import uuid
from fastapi import HTTPException, status

from .models import User
from . import schemas
from .utils import get_password_hash

def get_user_by_id(db: Session, user_id: uuid.UUID) -> Optional[User]:
    """Получает пользователя по ID"""
    return db.query(User).filter(User.id_user == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Получает пользователя по email"""
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Получает пользователя по username"""
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user_data: schemas.UserCreate) -> Optional[User]:
    """Создает нового пользователя"""
    try:
        # Проверяем email
        if get_user_by_email(db, user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Проверяем username если указан
        if user_data.username and get_user_by_username(db, user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            password_hash=get_password_hash(user_data.password)
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
        
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig)
        
        if "users_email_key" in error_msg or "email" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        elif "users_username_key" in error_msg or "username" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {error_msg}"
            )

def update_user_last_login(db: Session, user_id: uuid.UUID) -> None:
    """Обновляет время последнего входа пользователя"""
    from datetime import datetime
    user = get_user_by_id(db, user_id)
    if user:
        user.last_login_at = datetime.utcnow()
        db.commit()

def update_user_password(db: Session, user_id: uuid.UUID, new_password: str) -> bool:
    """Обновляет пароль пользователя"""
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    
    user.password_hash = get_password_hash(new_password)
    db.commit()
    return True

def delete_user(db: Session, user_id: uuid.UUID) -> bool:
    """Удаляет пользователя (soft delete)"""
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    
    user.is_active = False
    db.commit()
    return True

def activate_user(db: Session, user_id: uuid.UUID) -> bool:
    """Активирует пользователя"""
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    
    user.is_active = True
    db.commit()
    return True

def verify_user_email(db: Session, user_id: uuid.UUID) -> bool:
    """Помечает email пользователя как подтвержденный"""
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    
    user.is_verified = True
    db.commit()
    return True

def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    """Получает всех пользователей (для админов)"""
    return db.query(User).offset(skip).limit(limit).all()