"""
Логика проксирования запросов к микросервисам
"""
import httpx
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from typing import Dict, Optional
import logging
import json

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .config import settings

logger = logging.getLogger(__name__)

class ServiceProxy:
    """Класс для проксирования запросов к микросервисам"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=settings.SERVICE_TIMEOUT)
    
    async def proxy_request(self, service: str, path: str, request: Request, current_user: Optional[Dict] = None) -> Response:
        service_url = settings.SERVICE_ROUTES.get(service)
        if not service_url:
            raise ValueError(f"Service '{service}' not configured")
        
        target_url = f"{service_url.rstrip('/')}/{path.lstrip('/')}"
        if service_url.startswith("http"):
            target_url = f"{service_url.rstrip('/')}/{service}/{path.lstrip('/')}"
        
        headers = self._prepare_headers(request, current_user)

        # Проверяем multipart
        if 'multipart/form-data' in request.headers.get('content-type', ''):
            return await self._proxy_multipart(request, target_url, headers, current_user)
        
        # Для обычных JSON-запросов
        body = await request.body()
        async with httpx.AsyncClient(timeout=settings.SERVICE_TIMEOUT) as client:
            resp = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                params=dict(request.query_params),
                content=body
            )
            # Возвращаем JSON, если возможно
            try:
                return JSONResponse(status_code=resp.status_code, content=resp.json())
            except Exception:
                return Response(content=resp.content, status_code=resp.status_code, headers=dict(resp.headers))
    
    def _prepare_headers(self, request: Request, current_user: Optional[Dict]) -> Dict:
        """
        Подготавливает заголовки для проксирования
        """
        headers = {}
        
        # Копируем полезные заголовки из оригинального запроса
        for header_name in [
            'content-type', 'accept', 'accept-encoding',
            'user-agent', 'cache-control', 'pragma'
        ]:
            if header_name in request.headers:
                headers[header_name] = request.headers[header_name]
        
        # Удаляем заголовки, которые не нужно передавать
        headers.pop('host', None)
        headers.pop('content-length', None)
        
        # Добавляем информацию о пользователе (если есть)
        if current_user:
            headers['X-User-ID'] = current_user.get('user_id', '')
            headers['X-User-Email'] = current_user.get('email', '')
            
            # Передаем оригинальный токен для внутренних проверок
            if 'token' in current_user:
                headers['X-Auth-Token'] = current_user['token']
        
        # Добавляем заголовки для отслеживания запросов
        headers['X-Forwarded-For'] = request.client.host if request.client else 'unknown'
        headers['X-Gateway-Request'] = 'true'
        
        return headers
    
    async def _prepare_body(self, request: Request) -> bytes:
        """
        Подготавливает тело запроса для проксирования
        """
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return b''
        
        return await request.body()
    
    async def close(self):
        """Закрывает HTTP клиент"""
        await self.client.aclose()


    async def _proxy_multipart(self, request: Request, target_url: str, 
                              headers: Dict, current_user: Optional[Dict]) -> Response:
        """Проксирование multipart/form-data запросов"""
        # Получаем данные формы
        form_data = await request.form()
        
        # Создаем новую форму
        files = []
        data = {}
        
        for key, value in form_data.items():
            if hasattr(value, 'read'):  # Это файл
                # Читаем файл в память (для небольших файлов)
                # Для больших файлов используйте потоковую передачу
                file_content = await value.read()
                files.append((key, (value.filename, file_content, value.content_type)))
            else:
                data[key] = value
        
        # Отправляем запрос
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                target_url,
                files=files,
                data=data,
                headers=headers
            )
            
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )