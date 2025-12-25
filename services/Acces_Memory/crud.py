"""
CRUD операции для управления доступом к страницам (исправленная версия).
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, text
from typing import List, Optional, Tuple, Dict, Any
import uuid
from datetime import datetime

from database.models.access import PageAccessControl
from database.models.memory import AgentBD, PageBD
from database.models.auth import User
from . import schemas


def get_access_by_id(db: Session, access_id: uuid.UUID) -> Optional[PageAccessControl]:
    """Получить запись доступа по ID."""
    return db.query(PageAccessControl).filter(PageAccessControl.id_access == access_id).first()


def get_access_by_page_and_user(db: Session, page_id: uuid.UUID, user_id: uuid.UUID) -> Optional[PageAccessControl]:
    """Получить запись доступа для конкретной страницы и пользователя."""
    return db.query(PageAccessControl).filter(
        and_(
            PageAccessControl.page_id == page_id,
            PageAccessControl.user_id == user_id,
            PageAccessControl.is_active == True
        )
    ).first()


def list_access_by_user(db: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 50) -> Tuple[List[dict], int]:
    """Получить список записей доступа для пользователя (страницы, к которым ему дали доступ)."""
    # SQL запрос для получения данных с JOIN
    sql = text("""
        SELECT 
            pa.id_access,
            pa.user_id,
            pa.granted_by,
            g.full_name as grantor_full_name,
            g.username as grantor_username,
            a.id_agent,
            p.id_page,
            a.full_name as agent_full_name,
            a.is_human,
            p.is_public,
            p.is_draft,
            pa.can_view,
            pa.can_edit,
            pa.granted_at,
            pa.expires_at,
            pa.is_active
        FROM page_access_control as pa
        JOIN pages as p ON pa.page_id = p.id_page
        JOIN agents as a ON p.agent_id = a.id_agent
        JOIN users as g ON pa.granted_by = g.id_user
        WHERE pa.user_id = :user_id AND pa.is_active = TRUE
        ORDER BY pa.granted_at DESC
        LIMIT :limit OFFSET :skip
    """)
    
    # Получаем данные
    result = db.execute(sql, {
        'user_id': str(user_id),
        'skip': skip,
        'limit': limit
    }).fetchall()
    
    # Получаем общее количество
    count_sql = text("""
        SELECT COUNT(*) 
        FROM page_access_control as pa
        WHERE pa.user_id = :user_id AND pa.is_active = TRUE
    """)
    
    total = db.execute(count_sql, {'user_id': str(user_id)}).scalar() or 0
    
    # Преобразуем в список словарей
    items = [dict(row._mapping) for row in result]
    return items, total


def list_access_by_grantor(db: Session, grantor_id: uuid.UUID, skip: int = 0, limit: int = 50) -> Tuple[List[dict], int]:
    """Получить список записей доступа, которые предоставил определённый пользователь."""
    # SQL запрос для получения данных с JOIN
    sql = text("""
        SELECT 
            pa.id_access,
            pa.granted_by,
            pa.user_id,
            u.full_name as recipient_full_name,
            u.username as recipient_username,
            a.id_agent,
            p.id_page,
            a.full_name as agent_full_name,
            a.is_human,
            p.is_public,
            p.is_draft,
            pa.can_view,
            pa.can_edit,
            pa.granted_at,
            pa.expires_at,
            pa.is_active
        FROM page_access_control as pa
        JOIN pages as p ON pa.page_id = p.id_page
        JOIN agents as a ON p.agent_id = a.id_agent
        JOIN users as u ON pa.user_id = u.id_user
        WHERE pa.granted_by = :grantor_id AND pa.is_active = TRUE
        ORDER BY pa.granted_at DESC
        LIMIT :limit OFFSET :skip
    """)
    
    # Получаем данные
    result = db.execute(sql, {
        'grantor_id': str(grantor_id),
        'skip': skip,
        'limit': limit
    }).fetchall()
    
    # Получаем общее количество
    count_sql = text("""
        SELECT COUNT(*) 
        FROM page_access_control as pa
        WHERE pa.granted_by = :grantor_id AND pa.is_active = TRUE
    """)
    
    total = db.execute(count_sql, {'grantor_id': str(grantor_id)}).scalar() or 0
    
    # Преобразуем в список словарей
    items = [dict(row._mapping) for row in result]
    return items, total


def check_user_page_access(
    db: Session, 
    page_id: uuid.UUID, 
    user_id: uuid.UUID
) -> Dict[str, Any]:
    """
    Проверить, есть ли у пользователя доступ к странице.
    Используем raw SQL для избежания проблем с relationships.
    """
    try:
        # 1. Проверяем существование страницы
        page_sql = text("""
            SELECT id_page, user_id, is_public, is_draft
            FROM pages 
            WHERE id_page = :page_id
        """)
        
        page_result = db.execute(page_sql, {'page_id': str(page_id)}).fetchone()
        
        if not page_result:
            return {
                'has_access': False,
                'can_view': False,
                'can_edit': False,
                'reason': 'Page not found',
                'is_owner': False
            }
        
        page_data = dict(page_result._mapping)
        
        # 2. Проверяем, является ли пользователь владельцем страницы
        is_owner = str(page_data['user_id']) == str(user_id)
        
        if is_owner:
            return {
                'has_access': True,
                'can_view': True,
                'can_edit': True,
                'reason': 'Page owner',
                'is_owner': True,
                'page_id': page_id
            }
        
        # 3. Проверяем, является ли страница публичной
        if page_data['is_public'] and not page_data['is_draft']:
            return {
                'has_access': True,
                'can_view': True,
                'can_edit': False,
                'reason': 'Public page',
                'is_owner': False,
                'page_id': page_id
            }
        
        # 4. Проверяем доступ в access_control
        access_sql = text("""
            SELECT can_view, can_edit, expires_at
            FROM page_access_control 
            WHERE page_id = :page_id 
                AND user_id = :user_id 
                AND is_active = TRUE
        """)
        
        access_result = db.execute(access_sql, {
            'page_id': str(page_id),
            'user_id': str(user_id)
        }).fetchone()
        
        if access_result:
            access_data = dict(access_result._mapping)
            
            # Проверяем срок действия доступа
            if access_data['expires_at'] and access_data['expires_at'] < datetime.now():
                return {
                    'has_access': False,
                    'can_view': False,
                    'can_edit': False,
                    'reason': 'Access expired',
                    'is_owner': False,
                    'page_id': page_id
                }
            
            return {
                'has_access': True,
                'can_view': access_data['can_view'],
                'can_edit': access_data['can_edit'],
                'reason': 'Has access',
                'is_owner': False,
                'page_id': page_id,
                'access_expires': access_data['expires_at']
            }
        
        return {
            'has_access': False,
            'can_view': False,
            'can_edit': False,
            'reason': 'No access',
            'is_owner': False,
            'page_id': page_id
        }
        
    except Exception as e:
        print(f"Error in check_user_page_access: {e}")
        import traceback
        traceback.print_exc()
        return {
            'has_access': False,
            'can_view': False,
            'can_edit': False,
            'reason': f'Error: {str(e)}',
            'is_owner': False
        }


def get_page_with_access_check(
    db: Session, 
    page_id: uuid.UUID, 
    user_id: uuid.UUID
) -> Optional[Dict[str, Any]]:
    """
    Получить полную информацию о странице с проверкой доступа пользователя.
    Используем raw SQL для избежания проблем с relationships.
    """
    try:
        # 1. Проверяем доступ
        access_check = check_user_page_access(db, page_id, user_id)
        
        if not access_check['has_access']:
            return None
        
        # 2. Получаем информацию о странице
        page_sql = text("""
            SELECT p.*, a.*, u_grantor.full_name as grantor_name, u_grantor.username as grantor_username
            FROM pages p
            JOIN agents a ON p.agent_id = a.id_agent
            LEFT JOIN page_access_control pac ON p.id_page = pac.page_id AND pac.user_id = :user_id AND pac.is_active = TRUE
            LEFT JOIN users u_grantor ON pac.granted_by = u_grantor.id_user
            WHERE p.id_page = :page_id
        """)
        
        page_result = db.execute(page_sql, {
            'page_id': str(page_id),
            'user_id': str(user_id)
        }).fetchone()
        
        if not page_result:
            return None
        
        page_data = dict(page_result._mapping)
        
        # 3. Формируем результат
        result = {
            'has_access': True,
            'permissions': {
                'can_view': access_check['can_view'],
                'can_edit': access_check['can_edit']
            },
            'is_owner': access_check.get('is_owner', False),
            'reason': access_check.get('reason', ''),
            'page_data': page_data
        }
        
        return result
        
    except Exception as e:
        print(f"Error in get_page_with_access_check: {e}")
        import traceback
        traceback.print_exc()
        return None


def create_access(db: Session, access_data: schemas.PageAccessCreate, grantor_id: uuid.UUID) -> PageAccessControl:
    """Создать новую запись доступа."""
    db_access = PageAccessControl(
        **access_data.dict(),
        granted_by=grantor_id
    )
    db.add(db_access)
    db.commit()
    db.refresh(db_access)
    return db_access


def update_access(db: Session, access_id: uuid.UUID, update_data: schemas.PageAccessUpdate) -> Optional[PageAccessControl]:
    """Обновить запись доступа."""
    db_access = get_access_by_id(db, access_id)
    if not db_access:
        return None
    
    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(db_access, key, value)
    
    db.commit()
    db.refresh(db_access)
    return db_access


def deactivate_access(db: Session, access_id: uuid.UUID) -> bool:
    """Деактивировать запись доступа (мягкое удаление)."""
    db_access = get_access_by_id(db, access_id)
    if not db_access:
        return False
    
    db_access.is_active = False
    db.commit()
    return True


def delete_access(db: Session, access_id: uuid.UUID) -> bool:
    """Удалить запись доступа из БД."""
    db_access = get_access_by_id(db, access_id)
    if not db_access:
        return False
    
    db.delete(db_access)
    db.commit()
    return True