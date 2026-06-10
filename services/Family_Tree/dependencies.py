"""
DEPENDENCIES ДЛЯ СЕРВИСА FAMILY TREE
"""
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
import uuid
import logging

from database.session import get_db
from .config import config

logger = logging.getLogger(__name__)

# Используем HTTPBearer вместо OAuth2PasswordBearer,
# чтобы Swagger UI показывал поле для ввода токена, а не логин/пароль
http_bearer = HTTPBearer(auto_error=False)


def get_current_user_id(
    token_data: str = Depends(http_bearer),
) -> uuid.UUID:
    """
    Декодирует JWT-токен и возвращает user_id.
    Используется для защищённых маршрутов.
    Токен передаётся в заголовке: Authorization: Bearer <token>
    """
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = token_data.credentials
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token,
            config.SECRET_KEY,
            algorithms=[config.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return uuid.UUID(user_id)
    except (JWTError, ValueError) as e:
        logger.warning(f"JWT validation failed: {e}")
        raise credentials_exception


def get_optional_user_id(
    token_data: str = Depends(http_bearer),
) -> uuid.UUID | None:
    """
    Декодирует JWT-токен и возвращает user_id, если токен передан.
    Если токена нет — возвращает None (для публичных маршрутов).
    """
    if token_data is None:
        return None
    
    token = token_data.credentials
    
    try:
        payload = jwt.decode(
            token,
            config.SECRET_KEY,
            algorithms=[config.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return uuid.UUID(user_id)
    except (JWTError, ValueError):
        return None