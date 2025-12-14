"""
Зависимости и утилиты для API Gateway
"""
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from slowapi import Limiter
from slowapi.util import get_remote_address
import jwt
import httpx
from typing import Optional, Dict
from functools import wraps
import time

from .config import settings

security = HTTPBearer()

limiter = Limiter(key_func=get_remote_address)

# Настройки rate limiting по сервисам
RATE_LIMITS = {
    'auth': {
        'login': '10/minute',
        'register': '5/minute',
        'default': '60/minute'
    },
    'memory': {
        'default': '100/minute'
    }
}

def get_rate_limit(request: Request):
    """Динамическое определение rate limit в зависимости от пути"""
    path_parts = request.url.path.split('/')
    if len(path_parts) < 2:
        return "60/minute"
    
    service = path_parts[1]
    endpoint = path_parts[2] if len(path_parts) > 2 else 'default'
    
    service_limits = RATE_LIMITS.get(service, {})
    return service_limits.get(endpoint, service_limits.get('default', '60/minute'))

async def verify_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict]:
    """
    Проверка JWT токена.
    Возвращает данные пользователя или None если токен не валиден/отсутствует.
    """
    if not credentials:
        return None
    
    token = credentials.credentials
    
    try:
        # Вариант 1: Локальная проверка токена (быстрее)
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # Проверяем тип токена
        if payload.get("type") != "access":
            return None
            
        return {
            "user_id": payload.get("sub"),
            "email": payload.get("email"),
            "token": token
        }
        
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        # Вариант 2: Проверка через Auth сервис (медленнее, но надежнее)
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    f"{settings.AUTH_SERVICE_URL}/verify",
                    json={"token": token},
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("valid"):
                        return {
                            "user_id": data.get("user_id"),
                            "email": data.get("email"),
                            "token": token
                        }
        except Exception:
            pass
        
        return None

def rate_limit(max_requests: int = 60, window: int = 60):
    """
    Декоратор для ограничения количества запросов
    """
    from collections import defaultdict
    import time
    
    request_log = defaultdict(list)
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get('request')
            if not request:
                return await func(*args, **kwargs)
                
            client_ip = request.client.host
            current_time = time.time()
            
            # Очищаем старые записи
            request_log[client_ip] = [
                req_time for req_time in request_log[client_ip]
                if current_time - req_time < window
            ]
            
            # Проверяем лимит
            if len(request_log[client_ip]) >= max_requests:
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests"
                )
            
            # Добавляем текущий запрос
            request_log[client_ip].append(current_time)
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator