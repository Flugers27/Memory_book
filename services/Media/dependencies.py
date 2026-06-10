"""
Зависимости (Depends) для сервиса Media
"""
import sys
import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import uuid
from typing import Optional

# Добавляем корень проекта в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

# Импортируем из общей базы данных
from database.session import get_db

# Импортируем из текущего сервиса
from .crud import get_media_by_id

# Используем HTTPBearer для Bearer токенов (Swagger показывает поле для токена)
http_bearer = HTTPBearer(auto_error=False)

def get_current_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer)
) -> uuid.UUID:
    """
    Получает ID пользователя из JWT токена.
    Декодирует токен и извлекает user_id из поля 'sub'.
    Токен передаётся в заголовке: Authorization: Bearer <token>
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    try:
        # Импортируем jwt библиотеку
        import jwt as pyjwt
        from ..config import config
        
        # Декодируем токен
        payload = pyjwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        user_id_str = payload.get("sub")
        
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный токен: отсутствует ID пользователя"
            )
        
        return uuid.UUID(user_id_str)
    except pyjwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен истек"
        )
    except pyjwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный токен"
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный формат ID пользователя в токене"
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный или просроченный токен"
        )


def get_media_or_404(
    media_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Получает медиа по ID или возвращает 404"""
    media = get_media_by_id(db, media_id)
    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Медиа с ID {media_id} не найдено"
        )
    return media


def validate_user_access(
    media,
    user_id: uuid.UUID = Depends(get_current_user_id)
):
    """Проверяет, имеет ли пользователь доступ к медиа"""
    if media.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к этому медиа"
        )
    return media