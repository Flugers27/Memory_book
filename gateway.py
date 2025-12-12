"""
API Gateway - проксирует запросы к нужным сервисам
"""
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Инициализация клиента HTTP
    app.state.http_client = httpx.AsyncClient()
    yield
    # Закрытие клиента
    await app.state.http_client.aclose()

app = FastAPI(
    lifespan=lifespan,
    title="API Gateway",
    description="Проксирует запросы к сервисам",
    version="1.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем все для тестирования
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Сервисы
SERVICES = {
    "auth": "http://localhost:8000",
    "memory": "http://localhost:8001"
}

# Маршруты, которые обрабатываются самим gateway
INTERNAL_ROUTES = ["/docs", "/redoc", "/openapi.json", "/favicon.ico"]

@app.get("/")
async def root():
    """Корневой endpoint для проверки работы gateway"""
    return {
        "message": "API Gateway is running",
        "services": list(SERVICES.keys()),
        "endpoints": [
            "POST /auth/login",
            "POST /auth/register", 
            "GET /agents/",
            "GET /pages/",
            "GET /titles/"
        ]
    }

@app.get("/health")
async def health():
    """Health check для gateway"""
    services_status = {}
    
    client: httpx.AsyncClient = app.state.http_client
    
    for service_name, service_url in SERVICES.items():
        try:
            response = await client.get(f"{service_url}/", timeout=2.0)
            services_status[service_name] = {
                "status": "healthy" if response.status_code < 500 else "unhealthy",
                "status_code": response.status_code,
                "url": service_url
            }
        except Exception as e:
            services_status[service_name] = {
                "status": "unavailable",
                "error": str(e),
                "url": service_url
            }
    
    return {
        "gateway": "healthy",
        "services": services_status
    }

@app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy(request: Request, path_name: str):
    """Проксирует запросы к нужному сервису"""
    
    # Обработка OPTIONS запросов для CORS
    if request.method == "OPTIONS":
        return Response(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            }
        )
    
    # Проверяем, является ли путь внутренним маршрутом gateway
    full_path = f"/{path_name}"
    if full_path in INTERNAL_ROUTES or full_path.startswith("/docs") or full_path.startswith("/redoc"):
        # Для favicon.ico возвращаем 404
        if full_path == "/favicon.ico":
            return Response(status_code=404)
        # Для остальных внутренних маршрутов позволяем FastAPI обработать их
        return JSONResponse(
            status_code=404,
            content={"error": "Internal gateway route should not be proxied"}
        )
    
    # Определяем к какому сервису относится запрос
    # Все что начинается с auth/ или users/ идет в auth сервис
    if path_name.startswith("auth/") or path_name.startswith("users/"):
        target_service = "auth"
    # Все что начинается с pages/, agents/, titles/ идет в memory сервис
    elif (path_name.startswith("pages/") or 
          path_name.startswith("agents/") or 
          path_name.startswith("titles/")):
        target_service = "memory"
    else:
        # Для всех остальных маршрутов возвращаем ошибку
        return JSONResponse(
            status_code=404,
            content={
                "error": f"Route not found or not mapped: /{path_name}",
                "available_routes": {
                    "auth": ["/auth/login", "/auth/register", "/auth/refresh", "/auth/verify", "/users/"],
                    "memory": ["/pages/", "/agents/", "/titles/"]
                }
            }
        )
    
    target_url = f"{SERVICES[target_service]}/{path_name}"
    print(f"DEBUG: Proxying {request.method} /{path_name} -> {target_url}")
    
    # Проксируем запрос
    client: httpx.AsyncClient = request.app.state.http_client
    
    # Подготавливаем запрос
    headers = dict(request.headers)
    headers.pop("host", None)  # Удаляем host заголовок
    
    try:
        # Собираем тело запроса
        body = await request.body()
        
        response = await client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            content=body if body else None,
            params=request.query_params,
            follow_redirects=True,
            timeout=30.0
        )
        
        # Исключаем некоторые заголовки из ответа
        excluded_headers = ["content-encoding", "transfer-encoding", "connection"]
        response_headers = {
            k: v for k, v in response.headers.items()
            if k.lower() not in excluded_headers
        }
        
        # Добавляем CORS заголовки
        response_headers["Access-Control-Allow-Origin"] = "*"
        response_headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, PATCH, OPTIONS"
        response_headers["Access-Control-Allow-Headers"] = "*"
        
        # Создаем ответ FastAPI с теми же данными
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=response_headers
        )
        
    except httpx.ConnectError:
        return JSONResponse(
            status_code=503,
            content={"error": f"Service {target_service} is unavailable", "service": target_service, "url": target_url}
        )
    except httpx.TimeoutException:
        return JSONResponse(
            status_code=504,
            content={"error": f"Service {target_service} timeout", "service": target_service, "url": target_url}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Gateway error: {str(e)}", "service": target_service, "url": target_url}
        )