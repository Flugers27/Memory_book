"""
Зависимости (Depends) для сервиса Media
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
from .crud import get_media_by_id

# Схема OAuth2 для получения токена из заголовков
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/login",
    scheme_name="JWT"
)

def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:
    """
    Получает ID пользователя из токена.
    В реальном приложении здесь должна быть валидация JWT токена.
    Для упрощения предполагаем, что токен содержит user_id.
    """
    # Временная реализация - извлекаем user_id из заголовка
    # В реальном приложении нужно декодировать JWT токен
    try:
        # Здесь должна быть логика валидации токена
        # Пока возвращаем тестовый ID
        return "test-user-id"
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный или просроченный токен"
        )


def get_media_or_404(
    media_id: str,
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
    user_id: str = Depends(get_current_user_id)
):
    """Проверяет, имеет ли пользователь доступ к медиа"""
    if media.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к этому медиа"
        )
    return media