"""
Middleware для API Gateway
"""
import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware для логирования всех запросов
    """
    
    async def dispatch(self, request: Request, call_next):
        # Засекаем время начала обработки
        start_time = time.time()
        
        # Получаем информацию о запросе
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path
        
        # Пропускаем запрос через цепочку middleware
        response = await call_next(request)
        
        # Вычисляем время обработки
        process_time = time.time() - start_time
        
        # Логируем запрос
        logger.info(
            f"{client_ip} - \"{method} {path}\" "
            f"{response.status_code} - {process_time:.3f}s"
        )
        
        # Добавляем заголовок с временем обработки
        response.headers["X-Process-Time"] = str(process_time)
        
        return response

class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware для сбора метрик
    """
    def __init__(self, app):
        super().__init__(app)
        self.request_count = 0
        self.error_count = 0
    
    async def dispatch(self, request: Request, call_next):
        self.request_count += 1
        
        try:
            response = await call_next(request)
            
            # Считаем ошибки
            if response.status_code >= 400:
                self.error_count += 1
            
            # Добавляем метрики в заголовки
            response.headers["X-Request-Count"] = str(self.request_count)
            response.headers["X-Error-Count"] = str(self.error_count)
            
            return response
        except Exception as e:
            self.error_count += 1
            raise e