"""
Роутер для health check и обслуживания статических файлов
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
from pathlib import Path

from ..config import config

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {
        "status": "healthy",
        "service": config.SERVICE_NAME,
        "port": config.SERVICE_PORT
    }


@router.get("/temp/{user_id}/{filename}")
async def serve_temp_file(user_id: str, filename: str):
    """Отдача временных файлов (без page_id)"""
    file_path = os.path.join(config.get_temp_folder_path(user_id), filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл не найден")
    
    return FileResponse(file_path)


@router.get("/temp/{user_id}/{page_id}/{filename}")
async def serve_temp_file_with_page(user_id: str, page_id: str, filename: str):
    """Отдача временных файлов (с page_id)"""
    file_path = os.path.join(config.get_temp_folder_path(user_id, page_id), filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл не найден")
    
    return FileResponse(file_path)


@router.get("/permanent/{user_id}/{filename}")
async def serve_permanent_file(user_id: str, filename: str):
    """Отдача постоянных файлов (без page_id)"""
    file_path = os.path.join(config.get_permanent_folder_path(user_id), filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл не найден")
    
    return FileResponse(file_path)


@router.get("/permanent/{user_id}/{page_id}/{filename}")
async def serve_permanent_file_with_page(user_id: str, page_id: str, filename: str):
    """Отдача постоянных файлов (с page_id)"""
    file_path = os.path.join(config.get_permanent_folder_path(user_id, page_id), filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл не найден")
    
    return FileResponse(file_path)