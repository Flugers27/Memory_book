"""
FastAPI зависимости (Depends).
"""
import sys
import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import jwt
import uuid

# Добавляем корень проекта в путь
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from config import get_db, User
from .auth_logic import verify_token
from .crud import get_user_by_id

# Схема OAuth2 для получения токена из заголовков
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

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
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        return user
    except (jwt.JWTError, ValueError):
        raise credentials_exception

def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Зависимость для получения активного пользователя"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user