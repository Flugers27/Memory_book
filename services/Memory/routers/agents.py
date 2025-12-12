"""
Роутер для работы с агентами памяти (memory_agent)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
import uuid

# Простые относительные импорты - они будут работать, так как файл в папке routers
from ..config import get_db
from .. import schemas
from ..crud import (
    get_memory_agent, get_memory_agents_by_user, create_memory_agent,
    update_memory_agent, delete_memory_agent
)
# Используем локальную зависимость из Memory/dependencies.py
from ..dependencies import get_current_user_id

router = APIRouter(prefix="/agents", tags=["memory_agents"])

@router.get("/", response_model=List[schemas.MemoryAgent])
async def get_agents(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Получение списка агентов памяти текущего пользователя"""
    agents = get_memory_agents_by_user(
        db=db,
        user_id=user_id,
        skip=skip,
        limit=limit
    )
    return agents

@router.post("/", response_model=schemas.MemoryAgent, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_data: schemas.MemoryAgentCreate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Создание нового агента памяти"""
    agent = create_memory_agent(
        db=db,
        agent_data=agent_data,
        user_id=user_id
    )
    return agent

@router.get("/{agent_id}", response_model=schemas.MemoryAgent)
async def get_agent(
    agent_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Получение агента памяти по ID"""
    agent = get_memory_agent(db, agent_id)
    
    if not agent or agent.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found or access denied"
        )
    
    return agent

@router.put("/{agent_id}", response_model=schemas.MemoryAgent)
async def update_agent(
    agent_id: uuid.UUID,
    agent_update: schemas.MemoryAgentUpdate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Обновление агента памяти"""
    agent = update_memory_agent(
        db=db,
        agent_id=agent_id,
        agent_update=agent_update,
        user_id=user_id
    )
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found or access denied"
        )
    
    return agent

@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Удаление агента памяти"""
    success = delete_memory_agent(
        db=db,
        agent_id=agent_id,
        user_id=user_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found or access denied"
        )