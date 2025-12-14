"""
API Gateway - главная точка входа для всех запросов
"""
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
import httpx
import logging
from typing import Dict, Optional
import time

# Импорты из внутренних модулей
from .config import settings
from .dependencies import verify_token, rate_limit
from .middleware import LoggingMiddleware
from .proxy import ServiceProxy


# Настройка логирования
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Создаем FastAPI приложение
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Добавляем кастомное middleware
app.add_middleware(LoggingMiddleware)

from .openapi import custom_openapi
app.openapi = lambda: custom_openapi(app)

# Инициализируем прокси для сервисов
service_proxy = ServiceProxy()

@app.get("/")
async def root():
    """Корневой эндпоинт Gateway"""
    print(settings.SERVICE_ROUTES)
    return {
        "message": "Memory Book API Gateway",
        "version": settings.VERSION,
        "services": list(settings.SERVICE_ROUTES.keys()),
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Проверка здоровья Gateway"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "gateway"
    }

@app.get("/health/all")
async def health_check_all():
    """Проверка здоровья всех сервисов"""
    health_status = {
        "gateway": {"status": "healthy", "timestamp": time.time()},
        "services": {}
    }
    
    # Проверяем каждый сервис
    for service_name, service_url in settings.SERVICE_ROUTES.items():
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{service_url}/health")
                health_status["services"][service_name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "status_code": response.status_code,
                    "url": service_url
                }
        except Exception as e:
            health_status["services"][service_name] = {
                "status": "unreachable",
                "error": str(e),
                "url": service_url
            }
    
    return health_status

@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def gateway_proxy(
    service: str,
    path: str,
    request: Request,
    current_user: Optional[Dict] = Depends(verify_token)
):
    """
    Основной прокси-эндпоинт Gateway
    
    Все запросы проходят через этот эндпоинт:
    /auth/login -> Auth Service
    /memory/pages -> Memory Service
    и т.д.
    """
    logger.info(f"Gateway request: {request.method} /{service}/{path}")
    
    # Проверяем существование сервиса
    if service not in settings.SERVICE_ROUTES:
        raise HTTPException(status_code=404, detail=f"Service '{service}' not found")
    
    # Проверяем аутентификацию (если требуется)
    full_path = f"/{service}/{path}"
    requires_auth = not any(full_path.startswith(public_path) for public_path in settings.PUBLIC_PATHS)
    
    if requires_auth and not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Проксируем запрос к соответствующему сервису
    try:
        response = await service_proxy.proxy_request(
            service=service,
            path=path,
            request=request,
            current_user=current_user
        )
        return response
    except httpx.TimeoutException:
        logger.error(f"Service {service} timeout for path {path}")
        raise HTTPException(status_code=504, detail=f"Service {service} timeout")
    except httpx.RequestError as e:
        logger.error(f"Service {service} error: {str(e)}")
        raise HTTPException(status_code=502, detail=f"Service {service} unavailable")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal gateway error")

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting API Gateway on {settings.HOST}:{settings.PORT}")
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )