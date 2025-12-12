"""
Комплексный роутер для создания/просмотра/обновления полной цепочки:
агент -> страница -> заголовки
Название файла: memory_pages.py (но функциональность полная)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from ..dependencies import get_current_user_id
from config import get_db, MemoryAgent, MemoryPage, MemoryTitles
from .. import schemas
from ..crud import (
    create_memory_agent, create_memory_page, create_memory_title,
    get_memory_page, get_memory_agent, get_memory_titles_by_page,
    update_memory_agent, update_memory_page, update_memory_title
)

router = APIRouter(prefix="/memory-pages", tags=["complete_memory_operations"])

# ========== COMPLETE CREATE ==========
class CompleteCreateRequest(schemas.MemoryBase):
    """Запрос на создание полной цепочки"""
    agent: schemas.MemoryAgentCreate
    page: schemas.MemoryPageCreate
    titles: List[schemas.MemoryTitlesCreate] = []

class CompleteCreateResponse(schemas.MemoryBase):
    """Ответ с созданной цепочкой"""
    agent: schemas.MemoryAgent
    page: schemas.MemoryPage
    titles: List[schemas.MemoryTitles] = []

@router.post("/create", response_model=CompleteCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_complete_memory(
    request: CompleteCreateRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Создание полной цепочки: агент -> страница -> заголовки
    """
    # 1. Создаем агента
    agent = create_memory_agent(db, request.agent, user_id)
    
    # 2. Обновляем page_data с правильным agent_id
    page_data_dict = request.page.dict()
    page_data_dict["memory_agent_id"] = agent.id_agent
    
    from .. import schemas as memory_schemas
    page_data = memory_schemas.MemoryPageCreate(**page_data_dict)
    
    # 3. Создаем страницу
    page = create_memory_page(db, page_data, user_id)
    
    if not page:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create page"
        )
    
    # 4. Создаем заголовки (если есть)
    created_titles = []
    for title_data in request.titles:
        # Обновляем page_id в каждом заголовке
        title_dict = title_data.dict()
        title_dict["page_id"] = page.id_page
        title_data_updated = memory_schemas.MemoryTitlesCreate(**title_dict)
        
        title = create_memory_title(db, title_data_updated, user_id)
        if title:
            created_titles.append(title)
    
    return CompleteCreateResponse(
        agent=agent,
        page=page,
        titles=created_titles
    )

# ========== COMPLETE READ ==========
class CompleteMemoryResponse(schemas.MemoryBase):
    """Полная информация о памяти"""
    agent: schemas.MemoryAgent
    page: schemas.MemoryPage
    titles: List[schemas.MemoryTitles] = []

@router.get("/page/{page_id}", response_model=CompleteMemoryResponse)
async def get_complete_memory(
    page_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Получение полной информации о странице: агент + страница + заголовки
    """
    # 1. Получаем страницу
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
    
    # 2. Получаем агента
    agent = get_memory_agent(db, page.memory_agent_id)
    if not agent or agent.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found or access denied"
        )
    
    # 3. Получаем заголовки
    titles = db.query(MemoryTitles)\
        .filter(MemoryTitles.page_id == page_id)\
        .order_by(MemoryTitles.sort_order)\
        .all()
    
    return CompleteMemoryResponse(
        agent=agent,
        page=page,
        titles=titles
    )

# ========== COMPLETE UPDATE ==========
class CompleteUpdateRequest(schemas.MemoryBase):
    """Запрос на обновление полной цепочки"""
    agent_update: schemas.MemoryAgentUpdate = None
    page_update: schemas.MemoryPageUpdate = None
    titles_updates: List[dict] = []  # List of {"id": uuid, "update": MemoryTitlesUpdate}

@router.put("/page/{page_id}")
async def update_complete_memory(
    page_id: uuid.UUID,
    request: CompleteUpdateRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Обновление полной цепочки: агент + страница + заголовки
    """
    # 1. Получаем страницу
    page = get_memory_page(db, page_id)
    if not page or page.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found or access denied"
        )
    
    result = {
        "agent_updated": False,
        "page_updated": False,
        "titles_updated": []
    }
    
    # 2. Обновляем агента (если нужно)
    if request.agent_update:
        agent = update_memory_agent(db, page.memory_agent_id, request.agent_update, user_id)
        if agent:
            result["agent_updated"] = True
    
    # 3. Обновляем страницу (если нужно)
    if request.page_update:
        updated_page = update_memory_page(db, page_id, request.page_update, user_id)
        if updated_page:
            result["page_updated"] = True
    
    # 4. Обновляем заголовки (если нужно)
    for title_update in request.titles_updates:
        title_id = title_update.get("id")
        update_data = title_update.get("update")
        
        if title_id and update_data:
            from .. import schemas as memory_schemas
            title_update_obj = memory_schemas.MemoryTitlesUpdate(**update_data)
            
            updated_title = update_memory_title(db, title_id, title_update_obj, user_id)
            if updated_title:
                result["titles_updated"].append(str(title_id))
    
    return result

# ========== QUICK CREATE (опционально) ==========
class QuickCreateRequest(schemas.MemoryBase):
    """Быстрое создание с минимальными данными"""
    agent_name: str
    page_epitaph: str = ""

@router.post("/quick-create", response_model=CompleteCreateResponse, status_code=status.HTTP_201_CREATED)
async def quick_create_memory(
    request: QuickCreateRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Быстрое создание памяти с минимальными данными
    """
    # 1. Создаем агента
    agent_data = schemas.MemoryAgentCreate(
        full_name=request.agent_name,
        birth_date=None,
        death_date=None,
        avatar_url=None
    )
    
    agent = create_memory_agent(db, agent_data, user_id)
    
    # 2. Создаем страницу
    page_data = schemas.MemoryPageCreate(
        epitaph=request.page_epitaph,
        place_of_birth=None,
        place_of_death=None,
        is_public=False,
        is_draft=False,
        memory_agent_id=agent.id_agent
    )
    
    page = create_memory_page(db, page_data, user_id)
    
    if not page:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create page"
        )
    
    return CompleteCreateResponse(
        agent=agent,
        page=page,
        titles=[]
    )