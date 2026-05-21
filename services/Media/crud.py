"""
CRUD операции для работы с медиафайлами
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime, timedelta
import os

from database.models.media import MediaBD
from . import schemas
from .config import config


def create_media(db: Session, media_data: schemas.MediaCreate) -> MediaBD:
    """Создает запись о медиа в базе данных"""
    db_media = MediaBD(
        id_media=str(uuid.uuid4()),
        user_id=media_data.user_id,
        page_id=media_data.page_id,
        file_extension=media_data.file_extension,
        file_size=media_data.file_size,
        media_type=media_data.media_type,
        mime_type=media_data.mime_type,
        width=media_data.width,
        height=media_data.height,
        duration=media_data.duration,
        is_public=media_data.is_public,
        sort_order=media_data.sort_order,
        is_temp=media_data.is_temp,
        has_thumbnail=False,
        has_medium=False
    )
    db.add(db_media)
    db.commit()
    db.refresh(db_media)
    return db_media


def get_media_by_id(db: Session, media_id: str) -> Optional[MediaBD]:
    """Получает медиа по ID"""
    return db.query(MediaBD).filter(MediaBD.id_media == media_id).first()


def get_media_by_user(db: Session, user_id: str, skip: int = 0, limit: int = 100) -> List[MediaBD]:
    """Получает все медиа пользователя"""
    return db.query(MediaBD).filter(MediaBD.user_id == user_id).offset(skip).limit(limit).all()


def get_temp_media_by_user(db: Session, user_id: str) -> List[MediaBD]:
    """Получает временные медиа пользователя"""
    return db.query(MediaBD).filter(
        and_(
            MediaBD.user_id == user_id,
            MediaBD.is_temp == True
        )
    ).all()


def get_media_by_page(db: Session, page_id: str, include_temp: bool = False) -> List[MediaBD]:
    """Получает все медиа страницы"""
    query = db.query(MediaBD).filter(MediaBD.page_id == page_id)
    if not include_temp:
        query = query.filter(MediaBD.is_temp == False)
    return query.order_by(MediaBD.sort_order.asc()).all()


def update_media(db: Session, media_id: str, media_update: schemas.MediaUpdate) -> Optional[MediaBD]:
    """Обновляет информацию о медиа"""
    db_media = get_media_by_id(db, media_id)
    if not db_media:
        return None
    
    update_data = media_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_media, field, value)
    
    db.commit()
    db.refresh(db_media)
    return db_media


def confirm_temp_media(db: Session, media_id: str, page_id: str) -> Optional[MediaBD]:
    """Подтверждает временное медиа, привязывая его к странице"""
    db_media = get_media_by_id(db, media_id)
    if not db_media:
        return None
    
    db_media.page_id = page_id
    db_media.is_temp = False
    db.commit()
    db.refresh(db_media)
    return db_media


def delete_media(db: Session, media_id: str) -> bool:
    """Удаляет медиа из базы данных"""
    db_media = get_media_by_id(db, media_id)
    if not db_media:
        return False
    
    db.delete(db_media)
    db.commit()
    return True


def delete_old_temp_media(db: Session, hours_old: int = 24) -> int:
    """Удаляет старые временные медиа"""
    cutoff_time = datetime.utcnow() - timedelta(hours=hours_old)
    
    # Находим старые временные медиа
    old_media = db.query(MediaBD).filter(
        and_(
            MediaBD.is_temp == True,
            MediaBD.created_at < cutoff_time
        )
    ).all()
    
    # Удаляем их
    count = 0
    for media in old_media:
        db.delete(media)
        count += 1
    
    if count > 0:
        db.commit()
    
    return count


def get_user_temp_media_count(db: Session, user_id: str) -> int:
    """Получает количество временных медиа пользователя"""
    return db.query(MediaBD).filter(
        and_(
            MediaBD.user_id == user_id,
            MediaBD.is_temp == True
        )
    ).count()


def search_media(
    db: Session, 
    user_id: Optional[str] = None,
    page_id: Optional[str] = None,
    media_type: Optional[str] = None,
    is_temp: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100
) -> List[MediaBD]:
    """Поиск медиа с фильтрами"""
    query = db.query(MediaBD)
    
    if user_id:
        query = query.filter(MediaBD.user_id == user_id)
    
    if page_id:
        query = query.filter(MediaBD.page_id == page_id)
    
    if media_type:
        query = query.filter(MediaBD.media_type == media_type)
    
    if is_temp is not None:
        query = query.filter(MediaBD.is_temp == is_temp)
    
    return query.offset(skip).limit(limit).all()