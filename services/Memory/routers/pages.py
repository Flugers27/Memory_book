"""
Роутер для работы со страницами памяти (memory_page)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from database.session import get_db
from .. import schemas_new as schemas
from ..crud import (
    select_page_list, select_page_by_user, create_page, update_page_db, delete_page)  #get_memory_page
from ..dependencies import get_current_user_id

router = APIRouter(tags=["pages"])

@router.get("/page_list/{agent_id}", response_model=schemas.PageListResponse)
async def get_pages(
    agent_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)):
    """Получение списка страниц памяти текущего пользователя"""

    res = select_page_list(db=db, agent_id=agent_id, skip=skip, limit=limit)

    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found"
        )
    res = schemas.PageListResponse.from_pages(user_id = user_id, agent_id=agent_id, pages=res)

    if not res or res == []:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pages not found"
        )

    return res

@router.get("/page/{page_id}", response_model=schemas.PageResponse)
async def get_page(page_id: str, user_id: uuid.UUID = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """Получение страницы памяти по ID"""
    page = select_page_by_user(db, user_id, page_id)
    
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found"
        )
    
    print(page)
    # Проверяем права доступа
    if str(page.user_id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return page.to_dict()

@router.post("/page/add", response_model=schemas.PageResponse, status_code=status.HTTP_201_CREATED)
async def add_agent(
    page_data: schemas.PageCreate,  # Без user_id
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Создание новой страницы"""
    page = create_page(
        db=db,
        page_data=page_data,
        user_id=user_id
    )

    return page.to_dict()  # Возвращаем объект SQLAlchemy

@router.put("/page/update/{page_id}", response_model=schemas.PageResponse)
async def update_page(
    page_id: uuid.UUID,
    page_update: schemas.PageUpdate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Обновление страницы памяти"""

    if page_update.is_public == True and page_update.is_draft == True :
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Публичные страницы не могут быть черновиком")

    page = update_page_db(
        db=db,
        page_id=page_id,
        page_update=page_update,
        user_id=user_id
    )
    
    if str(page.user_id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied")
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found or access denied"
        )
    print(page)
    print(type(page))
    return page.to_dict()

@router.delete("/page/del/{page_id}", status_code=status.HTTP_204_NO_CONTENT)
async def del_page(
    page_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Удаление страницы памяти"""
    success = delete_page(
        db=db,
        page_id=page_id,
        user_id=user_id
    )
    print(success)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found or access denied"
        )