"""
CRUD операции для работы с базой данных.
"""
import sys
import os
from sqlalchemy.orm import Session
from typing import Optional
import uuid

# Добавляем корень проекта в путь
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from config import User
from . import schemas
from .auth_logic import get_password_hash

def get_user_by_id(db: Session, user_id: uuid.UUID) -> Optional[User]:
    """Получает пользователя по ID"""
    return db.query(User).filter(User.id_user == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Получает пользователя по email"""
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Получает пользователя по username"""
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user_data: schemas.UserCreate) -> User:
    """Создает нового пользователя"""
    # Проверяем уникальность email
    if get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Проверяем уникальность username если указан
    if user_data.username and get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=400,
            detail="Username already taken"
        )
    
    # Создаем пользователя
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        password_hash=get_password_hash(user_data.password)
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user  # Всегда возвращаем объект User

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