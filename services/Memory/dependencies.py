"""
Зависимости для сервиса памяти
"""
import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import uuid
from typing import Optional

# Настройки JWT из .env
SECRET_KEY = os.getenv("SECRET_KEY", "your-very-secret-key-change-this-in-production-12345")
ALGORITHM = "HS256"

# Используем HTTPBearer для Bearer токенов
security = HTTPBearer(auto_error=False)

def get_current_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> uuid.UUID:
    """
    Получает ID пользователя из JWT токена.
    Валидирует токен локально, без обращения к Auth сервису.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    try:
        # Декодируем токен с использованием SECRET_KEY из .env
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str = payload.get("sub")  # JWT стандарт: 'sub' содержит user_id
        
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: no user id",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Преобразуем строку в UUID
        return uuid.UUID(user_id_str)
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid user id format: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )