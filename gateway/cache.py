"""
Кэширование для API Gateway
"""
from datetime import datetime, timedelta
from typing import Optional, Any
import hashlib
import pickle
import redis.asyncio as redis
from functools import wraps
import json

class CacheManager:
    def __init__(self, redis_url: Optional[str] = None):
        self.redis = None
        if redis_url:
            try:
                self.redis = redis.from_url(redis_url)
            except Exception:
                pass
    
    async def get(self, key: str) -> Optional[Any]:
        if not self.redis:
            return None
        
        try:
            data = await self.redis.get(key)
            if data:
                return pickle.loads(data)
        except Exception:
            pass
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 300):
        if not self.redis:
            return
        
        try:
            await self.redis.setex(
                key,
                ttl,
                pickle.dumps(value)
            )
        except Exception:
            pass

cache = CacheManager(os.getenv("REDIS_URL"))

def cache_response(ttl: int = 60):
    """Декоратор для кэширования ответов"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get('request')
            if not request:
                return await func(*args, **kwargs)
            
            # Создаем ключ кэша
            cache_key = hashlib.md5(
                f"{request.url.path}:{request.query_params}".encode()
            ).hexdigest()
            
            # Пытаемся получить из кэша
            cached = await cache.get(cache_key)
            if cached:
                return Response(**cached)
            
            # Выполняем запрос
            response = await func(*args, **kwargs)
            
            # Кэшируем ответ (только для GET и успешных запросов)
            if request.method == "GET" and response.status_code < 400:
                cache_data = {
                    "content": response.body,
                    "status_code": response.status_code,
                    "headers": dict(response.headers)
                }
                await cache.set(cache_key, cache_data, ttl)
            
            return response
        return wrapper
    return decorator