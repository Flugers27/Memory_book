"""
CRUD операции для сервиса памяти
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from typing import Optional, List
import uuid
from . import schemas
from config import MemoryAgent, MemoryPage, MemoryTitles

# ========== CRUD FOR MEMORY AGENT ==========
def get_memory_agent(db: Session, agent_id: uuid.UUID) -> Optional[MemoryAgent]:
    """Получает агента памяти по ID"""
    return db.query(MemoryAgent).filter(MemoryAgent.id_agent == agent_id).first()

def get_memory_agents_by_user(
    db: Session, 
    user_id: uuid.UUID,
    skip: int = 0,
    limit: int = 50
) -> List[MemoryAgent]:
    """Получает список агентов памяти пользователя"""
    return db.query(MemoryAgent)\
        .filter(MemoryAgent.user_id == user_id)\
        .order_by(desc(MemoryAgent.created_at))\
        .offset(skip)\
        .limit(limit)\
        .all()

def create_memory_agent(
    db: Session, 
    agent_data: schemas.MemoryAgentCreate,
    user_id: uuid.UUID
) -> MemoryAgent:
    """Создает нового агента памяти"""
    db_agent = MemoryAgent(**agent_data.dict(), user_id=user_id)
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent

def update_memory_agent(
    db: Session,
    agent_id: uuid.UUID,
    agent_update: schemas.MemoryAgentUpdate,
    user_id: uuid.UUID
) -> Optional[MemoryAgent]:
    """Обновляет агента памяти"""
    db_agent = get_memory_agent(db, agent_id)
    if not db_agent or db_agent.user_id != user_id:
        return None
    
    update_data = agent_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_agent, field, value)
    
    db.commit()
    db.refresh(db_agent)
    return db_agent

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
def get_memory_page(db: Session, page_id: uuid.UUID) -> Optional[MemoryPage]:
    """Получает страницу памяти по ID"""
    return db.query(MemoryPage).filter(MemoryPage.id_page == page_id).first()

def get_memory_pages_by_user(
    db: Session,
    user_id: uuid.UUID,
    skip: int = 0,
    limit: int = 50,
    is_draft: Optional[bool] = None,
    is_public: Optional[bool] = None
) -> List[MemoryPage]:
    """Получает список страниц памяти пользователя"""
    query = db.query(MemoryPage).filter(MemoryPage.user_id == user_id)
    
    # Фильтрация по статусу
    if is_draft is not None:
        query = query.filter(MemoryPage.is_draft == is_draft)
    if is_public is not None:
        query = query.filter(MemoryPage.is_public == is_public)
    
    return query\
        .order_by(desc(MemoryPage.created_at))\
        .offset(skip)\
        .limit(limit)\
        .all()

def get_public_memory_pages(
    db: Session,
    skip: int = 0,
    limit: int = 50
) -> List[MemoryPage]:
    """Получает список публичных страниц памяти"""
    return db.query(MemoryPage)\
        .filter(
            MemoryPage.is_public == True,
            MemoryPage.is_draft == False
        )\
        .order_by(desc(MemoryPage.created_at))\
        .offset(skip)\
        .limit(limit)\
        .all()

def create_memory_page(
    db: Session,
    page_data: schemas.MemoryPageCreate,
    user_id: uuid.UUID
) -> MemoryPage:
    """Создает новую страницу памяти"""
    db_page = MemoryPage(**page_data.dict(), user_id=user_id)
    db.add(db_page)
    db.commit()
    db.refresh(db_page)
    return db_page

def update_memory_page(
    db: Session,
    page_id: uuid.UUID,
    page_update: schemas.MemoryPageUpdate,
    user_id: uuid.UUID
) -> Optional[MemoryPage]:
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

