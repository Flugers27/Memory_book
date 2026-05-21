#!/usr/bin/env python3
"""
Скрипт для запуска сервиса Media
"""
import uvicorn
import os
import sys

# Добавляем путь для импорта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from services.Media.config import config

if __name__ == "__main__":
    print(f"Starting Media Service on port {config.SERVICE_PORT}...")
    print(f"Host: {config.HOST}")
    print(f"Debug: {config.DEBUG}")
    print(f"Upload folder: {config.UPLOAD_FOLDER}")
    
    uvicorn.run(
        "services.Media.main:app",
        host=config.HOST,
        port=config.SERVICE_PORT,
        reload=config.DEBUG,
        log_level="info"
    )