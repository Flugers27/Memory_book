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

# ========== CRUD FOR AGENT ==========
def select_memory_agent_list_by_user(db: Session, user_id: str, skip: int = 0, limit: int = 50) -> schemas.AgentListResponse:
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


# ========== CRUD FOR PAGE ==========
def _demote_other_main_pages(
    db: Session,
    agent_id: uuid.UUID,
    user_id: uuid.UUID,
    current_page_id: str
) -> None:
    """
    Вспомогательная функция:
    Делает все ДРУГИЕ опубликованные страницы агента черновиками.
    
    Устанавливает is_draft=True для всех страниц агента с is_draft=False,
    кроме текущей (указанной по ID).
    """
    # Находим все опубликованные страницы агента, кроме текущей
    other_published_pages = db.query(PageBD).filter(
        PageBD.memory_agent_id == str(agent_id),
        PageBD.id_page != current_page_id,
        PageBD.user_id == str(user_id),
        PageBD.is_draft == False  # Только опубликованные страницы
    ).all()
    
    # Делаем их черновиками
    for page in other_published_pages:
        page.is_draft = True
        page.is_public= False
        print(f"Страница {page.id_page} стала черновиком")
    
    if other_published_pages:
        db.commit()
        print(f"Обновлено {len(other_published_pages)} страниц в черновики")

def select_page_list(db: Session, agent_id: str, skip: int = 0, limit: int = 50) -> schemas.PageListResponse:
    """
    Получает список страниц
    Возвращает список (page)
    """
    
    try:
        result = db.query(PageBD) \
            .filter(PageBD.memory_agent_id == agent_id)\
            .order_by(desc(PageBD.updated_at))\
            .offset(skip)\
            .limit(limit)\
            .all()

        return result
    except Exception as e:
        print(f"ERROR in select_public_memory_page_list: {e}")
        return []
    
def select_page_by_user(db: Session, user_id: str, page_id: str) -> Optional[PageBD]:
    """Получает агента памяти по ID"""
    res =  db.query(PageBD).filter(and_(PageBD.id_page == page_id, PageBD.user_id == user_id)).first()

    return res

def create_page(
    db: Session, 
    page_data: schemas.PageCreate,  # Теперь без user_id
    user_id: uuid.UUID
) -> PageBD:
    """Создает нового агента памяти"""
    # Преобразуем UUID в строку для хранения в БД
    user_id_str = str(user_id)
    page= PageBD(**page_data.dict(), user_id=user_id_str)
    db.add(page)
    db.commit()
    db.refresh(page)

    if not page_data.is_draft:  # Если создали опубликованную
        _demote_other_main_pages(db, page.memory_agent_id, user_id, page.id_page)

    return page  # Возвращаем объект SQLAlchemy

def update_page_db(
    db: Session,
    page_id: str,
    page_update: schemas.PageUpdate,
    user_id: str
) -> PageBD:
    """Обновляет агента памяти"""
    page = select_page_by_user(db, user_id, page_id)

    if not page or str(page.user_id) != user_id:
        return None

    update_data = page_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:  # Обновляем только если значение не None
            setattr(page, field, value)
    
    db.commit()
    db.refresh(page)

    if not page_update.is_draft:  # Если создали опубликованную
        _demote_other_main_pages(db, page.memory_agent_id, user_id, page.id_page)

    return page  # Возвращаем объект SQLAlchemy

def delete_page(db: Session,page_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    """Удаляет агента памяти"""
    page = select_page_by_user(db, user_id, page_id)
    
    if not page or str(page.user_id) != user_id:
        return False
    
    db.delete(page)
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