"""
Роутер для работы со страницами памяти (memory_page)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

# Относительные импорты
from ..config import get_db
from .. import schemas
from ..crud import (
    get_memory_page, get_memory_pages_by_user, create_memory_page,
    update_memory_page, delete_memory_page, get_public_memory_pages
)
from ..dependencies import get_current_user_id

router = APIRouter(prefix="/pages", tags=["memory_pages"])

@router.get("/", response_model=List[schemas.MemoryPage])
async def get_pages(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    is_draft: Optional[bool] = None,
    is_public: Optional[bool] = None,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Получение списка страниц памяти текущего пользователя"""
    pages = get_memory_pages_by_user(
        db=db,
        user_id=user_id,
        skip=skip,
        limit=limit,
        is_draft=is_draft,
        is_public=is_public
    )
    return pages

@router.get("/public", response_model=List[schemas.MemoryPage])
async def get_public_pages(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Получение списка публичных страниц памяти (не требует авторизации)"""
    pages = get_public_memory_pages(db=db, skip=skip, limit=limit)
    return pages

@router.post("/", response_model=schemas.MemoryPage, status_code=status.HTTP_201_CREATED)
async def create_page(
    page_data: schemas.MemoryPageCreate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Создание новой страницы памяти"""
    # Проверяем что агент принадлежит пользователю (если указан)
    if page_data.memory_agent_id:
        from ..models import MemoryAgent
        agent = db.query(MemoryAgent).filter(
            MemoryAgent.id_agent == page_data.memory_agent_id,
            MemoryAgent.user_id == user_id
        ).first()
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Memory agent not found or access denied"
            )
    
    page = create_memory_page(
        db=db,
        page_data=page_data,
        user_id=user_id
    )
    
    return page

@router.get("/{page_id}", response_model=schemas.MemoryPage)
async def get_page(
    page_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Получение страницы памяти по ID"""
    page = get_memory_page(db, page_id)
    
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found"
        )
    
    # Проверяем права доступа
    if page.user_id != user_id and not (page.is_public and not page.is_draft):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return page

@router.put("/{page_id}", response_model=schemas.MemoryPage)
async def update_page(
    page_id: uuid.UUID,
    page_update: schemas.MemoryPageUpdate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Обновление страницы памяти"""
    page = update_memory_page(
        db=db,
        page_id=page_id,
        page_update=page_update,
        user_id=user_id
    )
    
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found or access denied"
        )
    
    return page

@router.delete("/{page_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_page(
    page_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Удаление страницы памяти"""
    success = delete_memory_page(
        db=db,
        page_id=page_id,
        user_id=user_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found or access denied"
        )