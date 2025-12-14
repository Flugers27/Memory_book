"""
Роутер для работы со страницами памяти (memory_page)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from ..config import get_db
from .. import schemas_new as schemas
from ..crud import (
    select_memory_page_list_by_user, select_public_memory_page_list, select_public_memory_page, select_memory_page_by_user)  #get_memory_page
from ..dependencies import get_current_user_id

router = APIRouter(tags=["memory_page"])

# ========== ПУБЛИЧНЫЕ ЭНДПОИНТЫ (доступны всем) ==========

@router.get("/public_memory_page_list", response_model=schemas.PublicMemoryPageListResponse)
async def get_public_memory_pages_with_agents_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    res = select_public_memory_page_list(db, skip=skip, limit=limit)

    res = schemas.PublicMemoryPageListResponse.from_public_memory_pages(res)
    print(res)
    return res

@router.get("/public_memory_page/{agent_id}", response_model=schemas.PublicMemoryPageResponse)
async def get_public_memory_page_with_agent(
    agent_id: str,
    db: Session = Depends(get_db)
):
    """
    Получение публичной страницы памяти по ID
    Только не черновик (is_draft=False) и публичная (is_public=True)
    """

    agent, page = select_public_memory_page(db, agent_id)

    if not page:
        raise HTTPException(
            status_code=404,
            detail="Публичная страница памяти не найдена или недоступна"
        )

    res = schemas.PublicMemoryPageResponse.from_agent_and_page(agent, page)
    return res

# ========== АВТОРИЗОВАННЫЕ ЭНДПОИНТЫ ==========

@router.get("/memory_page_list", response_model=schemas.MemoryPageListResponse)
async def get_user_memory_pages(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    is_draft: Optional[bool] = Query(None, description="Фильтр по черновикам"),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Получение списка страниц памяти текущего пользователя
    По умолчанию возвращаются только не черновики (is_draft=False)
    """
    
    res = select_memory_page_list_by_user(
        db=db,
        user_id=user_id,
        skip=skip,
        limit=limit
    )
    print(res)
    res = schemas.MemoryPageListResponse.from_memory_pages(user_id, res)
    
    return res

@router.get("/memory_page/{page_id}", response_model=schemas.MemoryPageResponse)
async def get_user_memory_page(
    agent_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Получение страницы памяти по ID (для владельца)
    Владелец может получить даже черновик
    """
    res = select_memory_page_by_user(db, user_id, agent_id)

    if not res:
        raise HTTPException(
            status_code=404,
            detail="Публичная страница памяти не найдена или недоступна"
        )

    first_agent, first_page = res[0]
    agent = first_agent  

    # Собираем все страницы агента
    pages = []
    for agent_record, page_record in res:
        if page_record:  # Проверяем, что страница существует (может быть NULL при LEFT JOIN)
            pages.append(page_record)

    res = schemas.MemoryPageResponse.from_models(agent, pages)
    return res
