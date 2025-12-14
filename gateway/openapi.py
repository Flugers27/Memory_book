"""
Кастомная OpenAPI схема для Gateway
"""
from fastapi.openapi.utils import get_openapi

def custom_openapi(app):
    """
    Генерирует кастомную OpenAPI схему для Gateway
    """
    if app.openapi_schema:
        return app.openapi_schema
    
    # Получаем базовую схему
    openapi_schema = get_openapi(
        title="Memory Book API Gateway",
        version="1.0.0",
        description="Единая точка входа для всех микросервисов Memory Book",
        routes=app.routes,
    )
    
    # Добавляем информацию о сервисах
    openapi_schema["x-servers"] = [
        {"url": "http://localhost:8000", "description": "Development server"}
    ]
    
    # Добавляем информацию о микросервисах
    openapi_schema["x-services"] = {
        "auth": {
            "url": "http://localhost:8001",
            "description": "Сервис аутентификации и авторизации",
            "endpoints": [
                "POST /auth/register",
                "POST /auth/login", 
                "POST /auth/refresh",
                "POST /auth/logout",
                "GET /users/me",
                "PUT /users/me/password"
            ]
        },
        "memory": {
            "url": "http://localhost:8002", 
            "description": "Сервис работы с воспоминаниями",
            "endpoints": [
                "GET /memory/pages",
                "POST /memory/pages",
                "GET /memory/pages/{id}",
                "PUT /memory/pages/{id}",
                "DELETE /memory/pages/{id}"
            ]
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema