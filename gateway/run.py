#!/usr/bin/env python3
"""
Скрипт запуска API Gateway
"""
import uvicorn
import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gateway.config import settings

if __name__ == "__main__":
    print(f"🚀 Starting {settings.APP_NAME}...")
    print(f"📡 Host: {settings.HOST}")
    print(f"🔌 Port: {settings.PORT}")
    print(f"🔐 Services: {list(settings.SERVICE_ROUTES.keys())}")
    print("-" * 50)
    
    uvicorn.run(
        "gateway.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
        access_log=True
    )