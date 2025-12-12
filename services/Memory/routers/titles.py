"""
Роутер для работы с заголовками памяти (memory_titles)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
import uuid

# Относительные импорты
from ..config import get_db
from .. import schemas
from ..crud import (
    get_memory_title, get_memory_titles_by_page, create_memory_title,
    update_memory_title, delete_memory_title
)
from ..dependencies import get_current_user_id

router = APIRouter(prefix="/titles", tags=["memory_titles"])

@router.get("/page/{page_id}", response_model=List[schemas.MemoryTitles])
async def get_titles_by_page(
    page_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Получение заголовков для страницы памяти"""
    # Проверяем права доступа к странице
    from ..models import MemoryPage
    page = db.query(MemoryPage).filter(MemoryPage.id_page == page_id).first()
    
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found"
        )
    
    if page.user_id != user_id and not (page.is_public and not page.is_draft):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    titles = get_memory_titles_by_page(
        db=db,
        page_id=page_id,
        skip=skip,
        limit=limit
    )
    return titles

@router.post("/", response_model=schemas.MemoryTitles, status_code=status.HTTP_201_CREATED)
async def create_title(
    title_data: schemas.MemoryTitlesCreate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Создание нового заголовка памяти"""
    title = create_memory_title(
        db=db,
        title_data=title_data,
        user_id=user_id
    )
    
    if not title:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found or access denied"
        )
    
    return title

@router.get("/{title_id}", response_model=schemas.MemoryTitles)
async def get_title(
    title_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Получение заголовка памяти по ID"""
    title = get_memory_title(db, title_id)
    
    if not title:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Title not found"
        )
    
    # Проверяем права доступа к странице
    from ..models import MemoryPage
    page = db.query(MemoryPage).filter(MemoryPage.id_page == title.page_id).first()
    
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found"
        )
    
    if page.user_id != user_id and not (page.is_public and not page.is_draft):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return title

@router.put("/{title_id}", response_model=schemas.MemoryTitles)
async def update_title(
    title_id: uuid.UUID,
    title_update: schemas.MemoryTitlesUpdate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Обновление заголовка памяти"""
    title = update_memory_title(
        db=db,
        title_id=title_id,
        title_update=title_update,
        user_id=user_id
    )
    
    if not title:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Title not found or access denied"
        )
    
    return title

@router.delete("/{title_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_title(
    title_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Удаление заголовка памяти"""
    success = delete_memory_title(
        db=db,
        title_id=title_id,
        user_id=user_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Title not found or access denied"
        )