"""
CRUD операции для сервиса памяти
"""
from sqlalchemy.orm import Session
from sqlalchemy.dialects import postgresql
from sqlalchemy import and_, or_, desc, asc
from fastapi import APIRouter, Depends, HTTPException, status, Query

from typing import Optional, List, Dict, Any
import uuid
from . import schemas
from .models import AgentBD, PageBD
#from config import, PageBD, MemoryTitles

# ========== CRUD FOR MEMORY AGENT ==========
def get_memory_agent(db: Session, agent_id: uuid.UUID) -> Optional[AgentBD]:
    """Получает агента памяти по ID"""
    res =  db.query(AgentBD).filter(AgentBD.id_agent == agent_id).first()
    
    return res

def get_memory_agent_list_by_user(
    db: Session, 
    user_id: str,  # user_id как строка
    skip: int = 0,
    limit: int = 50
) -> schemas.AgentListResponse:
    """Получает список агентов памяти пользователя в нужном формате"""
    # Получаем агентов из БД
    agents = db.query(AgentBD)\
        .filter(AgentBD.user_id == user_id)\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    # Преобразуем в формат для ответа
    agent_list = []
    for agent in agents:
        agent_list.append(schemas.AgentInList(
            id_agent=agent.id_agent,  # Оставляем как UUID, Pydantic сам сериализует в строку
            full_name=agent.full_name,
            birth_date=agent.birth_date,
            death_date=agent.death_date
        ))
    
    # Возвращаем в нужном формате
    return schemas.AgentListResponse(
        user_id=user_id,
        agent_list=agent_list
    )

def create_memory_agent(
    db: Session, 
    agent_data: schemas.AgentCreate,  # Теперь без user_id
    user_id: uuid.UUID
) -> AgentBD:
    """Создает нового агента памяти"""
    # Преобразуем UUID в строку для хранения в БД
    user_id_str = str(user_id)
    db_agent = AgentBD(**agent_data.dict(), user_id=user_id_str)
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent  # Возвращаем объект SQLAlchemy

def update_memory_agent(
    db: Session,
    agent_id: uuid.UUID,
    agent_update: schemas.AgentUpdate,
    user_id: uuid.UUID
) -> Optional[AgentBD]:
    """Обновляет агента памяти"""
    db_agent = get_memory_agent(db, agent_id)
    if not db_agent or db_agent.user_id != user_id:
        return None
    
    update_data = agent_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:  # Обновляем только если значение не None
            setattr(db_agent, field, value)
    
    db.commit()
    db.refresh(db_agent)
    return db_agent  # Возвращаем объект SQLAlchemy

def delete_memory_agent(
    db: Session,
    agent_id: uuid.UUID,
    user_id: uuid.UUID
) -> bool:
    """Удаляет агента памяти"""
    db_agent = get_memory_agent(db, agent_id)
    if not db_agent or db_agent.user_id != user_id:
        return False
    
    db.delete(db_agent)
    db.commit()
    return True

# ========== CRUD FOR MEMORY PAGE ==========
def get_memory_page(db: Session, page_id: uuid.UUID) -> Optional[PageBD]:
    """Получает страницу памяти по ID"""
    return db.query(PageBD).filter(PageBD.id_page == page_id).first()

def get_memory_pages_by_user(
    db: Session,
    user_id: uuid.UUID,
    skip: int = 0,
    limit: int = 50,
    is_draft: Optional[bool] = None,
    is_public: Optional[bool] = None
) -> List[PageBD]:
    """Получает список страниц памяти пользователя"""
    query = db.query(PageBD).filter(PageBD.user_id == user_id)
    
    # Фильтрация по статусу
    if is_draft is not None:
        query = query.filter(PageBD.is_draft == is_draft)
    if is_public is not None:
        query = query.filter(PageBD.is_public == is_public)
    
    return query\
        .order_by(desc(PageBD.created_at))\
        .offset(skip)\
        .limit(limit)\
        .all()

def get_public_memory_pages(
    db: Session,
    skip: int = 0,
    limit: int = 50
) -> List[PageBD]:
    """Получает список публичных страниц памяти"""
    return db.query(PageBD)\
        .filter(
            PageBD.is_public == True,
            PageBD.is_draft == False
        )\
        .order_by(desc(PageBD.created_at))\
        .offset(skip)\
        .limit(limit)\
        .all()

def create_memory_page(
    db: Session,
    page_data: schemas.MemoryPageCreate,
    user_id: uuid.UUID
) -> PageBD:
    """Создает новую страницу памяти"""
    db_page = PageBD(**page_data.dict(), user_id=user_id)
    db.add(db_page)
    db.commit()
    db.refresh(db_page)
    return db_page

def update_memory_page(
    db: Session,
    page_id: uuid.UUID,
    page_update: schemas.MemoryPageUpdate,
    user_id: uuid.UUID
) -> Optional[PageBD]:
    """Обновляет страницу памяти"""
    db_page = get_memory_page(db, page_id)
    if not db_page or db_page.user_id != user_id:
        return None
    
    update_data = page_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_page, field, value)
    
    db.commit()
    db.refresh(db_page)
    return db_page

def delete_memory_page(
    db: Session,
    page_id: uuid.UUID,
    user_id: uuid.UUID
) -> bool:
    """Удаляет страницу памяти"""
    db_page = get_memory_page(db, page_id)
    if not db_page or db_page.user_id != user_id:
        return False
    
    db.delete(db_page)
    db.commit()
    return True

