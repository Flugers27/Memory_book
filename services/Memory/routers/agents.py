"""
Роутер для работы с агентами памяти (memory_agent)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
import uuid

# Простые относительные импорты - они будут работать, так как файл в папке routers
from ..config import get_db
#from .. import schemas
from .. import schemas_new as schemas
from ..crud import (
    select_memory_agent_by_user, select_memory_agent_list_by_user, create_memory_agent,
    update_memory_agent, delete_memory_agent
)
# Используем локальную зависимость из Memory/dependencies.py
from ..dependencies import get_current_user_id

router = APIRouter(tags=["agent"])

    #Получение списка агентов памяти текущего пользователя
@router.get("/agent_list", response_model=schemas.AgentListResponse)
async def get_agents(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Получение списка агентов памяти текущего пользователя"""
    agents = select_memory_agent_list_by_user(db=db, user_id=user_id, skip=skip, limit=limit)
    res = schemas.AgentListResponse.from_agents(user_id=user_id, agents=agents)

    return res

@router.get("/agent/{agent_id}", response_model=schemas.AgentResponse)
async def get_agent(
    agent_id: str,  # UUID тип
    user_id: str = Depends(get_current_user_id),  # UUID тип
    db: Session = Depends(get_db)
):
    """Получение агента памяти по ID"""
    agent = select_memory_agent_by_user(db, user_id, agent_id)
    
    if not agent or str(agent.user_id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found or access denied")
    
    return agent.to_dict()

    #Создание нового агента памяти
@router.post("/agent/add", response_model=schemas.AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_data: schemas.AgentCreate,  # Без user_id
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Создание нового агента памяти"""
    agent = create_memory_agent(
        db=db,
        agent_data=agent_data,
        user_id=user_id
    )
    return agent.to_dict()  # Возвращаем объект SQLAlchemy

@router.put("/agent/update/{agent_id}", response_model=schemas.AgentResponse)
async def update_agent(
    agent_id: str,
    agent_update: schemas.AgentUpdate,
    user_id: str = Depends(get_current_user_id),
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
    
    return agent.to_dict()

@router.delete("/agent/del/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: str,
    user_id: str = Depends(get_current_user_id),
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