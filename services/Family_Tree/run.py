"""
Точка запуска сервиса Family Tree
"""
import uvicorn
import sys
import os

# Добавляем корень проекта в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from services.Family_Tree.config import config

if __name__ == "__main__":
    uvicorn.run(
        "services.Family_Tree.main:app",
        host=config.HOST,
        port=config.SERVICE_PORT,
        reload=config.DEBUG,
        log_level="info"
    )