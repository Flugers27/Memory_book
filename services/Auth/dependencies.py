"""
FastAPI зависимости (Depends).
"""
import sys
import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import uuid

# Добавляем корень проекта в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

# Импортируем из общей базы данных
from database.session import get_db

# Импортируем из текущего сервиса
from .auth_logic import verify_token
from .crud import get_user_by_id
from .models import User

# Схема OAuth2 для получения токена из заголовков
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/login",
    scheme_name="JWT"
)

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Зависимость для получения текущего пользователя из JWT токена.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Проверяем токен
        payload = verify_token(token, "access")
        user_id = uuid.UUID(payload.get("sub"))
        
        # Получаем пользователя из базы
        user = get_user_by_id(db, user_id)
        if user is None:
            raise credentials_exception
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is not active"
            )
        
        return user
    except (ValueError, AttributeError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token format: {str(e)}"
        )

def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Зависимость для получения активного пользователя"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is not active"
        )
    return current_user

def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Зависимость для получения администратора"""
    # Здесь можно добавить проверку на роль администратора
    # Например, если у пользователя есть поле role или is_admin
    return current_user