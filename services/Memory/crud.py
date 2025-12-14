"""
CRUD операции для сервиса памяти
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.dialects import postgresql
from sqlalchemy import and_, or_, desc, asc
from fastapi import APIRouter, Depends, HTTPException, status, Query

from typing import Optional, List, Dict, Any
import uuid
from . import schemas
from .models import AgentBD, PageBD
#from config import, PageBD, MemoryTitles

# ========== CRUD FOR MEMORY AGENT ==========
def select_memory_agent_list_by_user(db: Session, user_id: str,skip: int = 0,limit: int = 50) -> schemas.AgentListResponse:
    """Получает список агентов памяти пользователя в нужном формате"""
    # Получаем агентов из БД
    agents = db.query(AgentBD)\
        .filter(AgentBD.user_id == user_id)\
        .offset(skip)\
        .limit(limit)\
        .all()

    return agents

def select_memory_agent_by_user(db: Session, user_id: str, agent_id: str) -> Optional[AgentBD]:
    """Получает агента памяти по ID"""
    res =  db.query(AgentBD).filter(and_(AgentBD.id_agent == agent_id, AgentBD.user_id == user_id)).first()
    print(res)

    return res

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
    agent_id: str,
    agent_update: schemas.AgentUpdate,
    user_id: str
) -> Optional[AgentBD]:
    """Обновляет агента памяти"""
    db_agent = select_memory_agent_by_user(db, user_id, agent_id)

    if not db_agent or str(db_agent.user_id) != user_id:
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
    db_agent = select_memory_agent_by_user(db, user_id, agent_id)
    if not db_agent or str(db_agent.user_id) != user_id:
        return False
    
    db.delete(db_agent)
    db.commit()
    return True

# ========== CRUD FOR MEMORY PAGE ==========
def select_public_memory_page_list(
    db: Session,
    skip: int = 0,
    limit: int = 50
) -> List[tuple]:
    """
    Получает список публичных страниц памяти с информацией об агентах
    Возвращает список кортежей (agent, page)
    """
    
    try:
        # Этот запрос возвращает кортежи (PageBD, AgentBD)
        result = db.query(AgentBD, PageBD) \
            .join(AgentBD, AgentBD.id_agent == PageBD.memory_agent_id)\
            .filter(PageBD.is_public == True)\
            .order_by(desc(PageBD.updated_at))\
            .offset(skip)\
            .limit(limit)\
            .all()

        return result
    except Exception as e:
        print(f"ERROR in select_public_memory_page_list: {e}")
        return []

def select_public_memory_page(
    db: Session,
    agent_id: str
) -> Optional[tuple]:
    """
    Получает публичную страницу памяти с информацией об агенте
    Возвращает кортеж (agent, page)
    """
    try:
        # Этот запрос возвращает кортежи (PageBD, AgentBD)
        result = db.query(AgentBD, PageBD) \
            .join(AgentBD, AgentBD.id_agent == PageBD.memory_agent_id)\
            .filter(and_(AgentBD.id_agent == agent_id, PageBD.is_public == True))\
            .first()

        return result
    except Exception as e:
        print(f"ERROR in select_public_memory_page: {e}")
        return None

def select_memory_page_list_by_user(
    db: Session,
    user_id: uuid.UUID,
    skip: int = 0,
    limit: int = 50,
    is_draft: Optional[bool] = None,
    is_public: Optional[bool] = None
) -> List[PageBD]:
    """Получает список страниц памяти пользователя"""
    try:
        # Этот запрос возвращает кортежи (PageBD, AgentBD)
        result = db.query(AgentBD, PageBD) \
            .outerjoin(PageBD, AgentBD.id_agent == PageBD.memory_agent_id)\
            .filter(AgentBD.user_id == user_id)\
            .order_by(AgentBD.id_agent)\
            .offset(skip)\
            .limit(limit)\
            .all()

        return result
    except Exception as e:
        print(f"ERROR in get_public_memory_pages_with_agents: {e}")
        return []

def select_memory_page_by_user(db: Session, user_id: str, agent_id: str) -> Optional[tuple]:
    """Получает список страниц памяти пользователя"""
    try:
        # Этот запрос возвращает кортежи (PageBD, AgentBD)
        result = db.query(AgentBD, PageBD) \
            .outerjoin(PageBD, AgentBD.id_agent == PageBD.memory_agent_id)\
            .filter(and_(AgentBD.user_id == user_id, AgentBD.id_agent == agent_id))\
            .order_by(AgentBD.id_agent)\
            .all()

        return result
    except Exception as e:
        print(f"ERROR in select_memory_page_by_user: {e}")
        return []