"""
Роутер для управления доступом к страницам.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import uuid
from sqlalchemy import text
from datetime import datetime

from database.session import get_db
from ..dependencies import get_current_user_id
from .. import schemas
from ..crud import (
    get_access_by_id,
    get_access_by_page_and_user,
    list_access_by_user,
    list_access_by_grantor,
    create_access,
    update_access,
    deactivate_access,
    delete_access,
    check_user_page_access,
    get_page_with_access_check
)

router = APIRouter(prefix="/access", tags=["Access Management"])


@router.get("/my", response_model=schemas.PageAccessListResponse)
def get_my_access(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """Получить список страниц, к которым у текущего пользователя есть доступ."""
    # Преобразуем user_id в UUID
    user_uuid = uuid.UUID(user_id)
    
    # Получаем данные из базы
    raw_items, total = list_access_by_user(db, user_uuid, skip=skip, limit=limit)
    
    # Преобразуем в схемы
    items = []
    for raw_item in raw_items:
        item = schemas.build_page_access_item_from_raw(raw_item)
        items.append(item)
    
    # Рассчитываем номер страницы
    page = skip // limit + 1 if limit > 0 else 1
    
    return schemas.PageAccessListResponse(
        items=items,
        total=total,
        page=page,
        size=limit
    )


@router.get("/granted", response_model=schemas.GrantedAccessListResponse)
def get_granted_by_me(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    grantor_id: str = Depends(get_current_user_id)
):
    """Получить список страниц, к которым текущий пользователь предоставил доступ."""
    # Преобразуем grantor_id в UUID если нужно
    try:
        grantor_uuid = uuid.UUID(grantor_id)
    except (ValueError, TypeError):
        grantor_uuid = uuid.UUID(str(grantor_id))
    
    # Получаем данные из базы
    raw_items, total = list_access_by_grantor(db, grantor_uuid, skip=skip, limit=limit)
    
    # Преобразуем в схемы
    items = []
    for raw_item in raw_items:
        item = schemas.build_granted_access_item_from_raw(raw_item)
        items.append(item)
    
    # Рассчитываем номер страницы
    page = skip // limit + 1 if limit > 0 else 1
    
    return schemas.GrantedAccessListResponse(
        items=items,
        total=total,
        page=page,
        size=limit
    )


@router.get("/page/{page_id}/check", response_model=schemas.PageAccessCheckResponse)
def check_page_access(
    page_id: uuid.UUID,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Проверить доступ текущего пользователя к странице.
    
    Возвращает информацию о том, есть ли доступ, и какие права у пользователя.
    """
    
    # Проверяем доступ
    access_check = check_user_page_access(db, page_id, user_id)
    
    if not access_check['has_access']:
        return schemas.PageAccessCheckResponse(
            has_access=False,
            can_view=False,
            can_edit=False,
            message=f"Нет доступа к странице: {access_check.get('reason', 'unknown')}"
        )
    
    # Собираем данные для ответа
    response = schemas.PageAccessCheckResponse(
        has_access=True,
        can_view=access_check['can_view'],
        can_edit=access_check['can_edit'],
        message="Доступ предоставлен"
    )
    
    return response


@router.get("/page/{page_id}/full", response_model=schemas.PageAccessDetails)
def get_page_with_full_info(
    page_id: uuid.UUID,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Получить полную информацию о странице, агенте и доступе.
    
    Только если у пользователя есть доступ к странице.
    """
    
    # Проверяем доступ
    access_check = check_user_page_access(db, page_id, user_id)
    
    if not access_check['has_access']:
        raise HTTPException(
            status_code=403,
            detail=f"Нет доступа к странице: {access_check.get('reason', 'unknown')}"
        )
    
    if not access_check['can_view']:
        raise HTTPException(
            status_code=403,
            detail="У вас нет прав на просмотр этой страницы"
        )
    
    # Получаем информацию о странице
    page_sql = text("""
        SELECT * FROM pages WHERE id_page = :page_id
    """)
    page_result = db.execute(page_sql, {'page_id': str(page_id)}).fetchone()
    
    if not page_result:
        raise HTTPException(
            status_code=404,
            detail="Страница не найдена"
        )
    
    page_dict = dict(page_result._mapping)
    
    # Получаем информацию об агенте
    agent_id = page_dict['agent_id']
    agent_sql = text("""
        SELECT * FROM agents WHERE id_agent = :agent_id
    """)
    agent_result = db.execute(agent_sql, {'agent_id': str(agent_id)}).fetchone()
    
    if not agent_result:
        raise HTTPException(
            status_code=404,
            detail="Агент не найден"
        )
    
    agent_dict = dict(agent_result._mapping)
    
    # Получаем информацию о доступе (если есть)
    access_info = None
    if not access_check.get('is_owner', False):
        # Ищем запись о доступе
        access_sql = text("""
            SELECT pac.*, u.full_name as grantor_name, u.username as grantor_username
            FROM page_access_control pac
            LEFT JOIN users u ON pac.granted_by = u.id_user
            WHERE pac.page_id = :page_id 
                AND pac.user_id = :user_id 
                AND pac.is_active = TRUE
        """)
        access_result = db.execute(access_sql, {
            'page_id': str(page_id),
            'user_id': str(user_id)
        }).fetchone()
        
        if access_result:
            access_dict = dict(access_result._mapping)
            
            # Создаем краткую информацию об агенте для access_info
            short_agent_info = schemas.AgentShortInfo(
                id_agent=uuid.UUID(str(agent_dict['id_agent'])),
                full_name=agent_dict['full_name'],
                is_human=bool(agent_dict.get('is_human', True)),
                page=schemas.PageShortInfo(
                    id_page=uuid.UUID(str(page_dict['id_page'])),
                    is_public=bool(page_dict['is_public']),
                    is_draft=bool(page_dict['is_draft'])
                )
            )
            
            # Создаем информацию о предоставившем доступ
            grantor_info = None
            if access_dict.get('grantor_name') or access_dict.get('grantor_username'):
                grantor_info = schemas.UserShortInfo(
                    id_user=uuid.UUID(str(access_dict['granted_by'])) if access_dict['granted_by'] else None,
                    full_name=access_dict.get('grantor_name'),
                    username=access_dict.get('grantor_username')
                )
            
            access_info = schemas.PageAccessListItem(
                id_access=uuid.UUID(str(access_dict['id_access'])),
                user_id=uuid.UUID(str(access_dict['user_id'])),
                granted_by=uuid.UUID(str(access_dict['granted_by'])) if access_dict['granted_by'] else None,
                grantor_info=grantor_info,
                agent=short_agent_info,
                can_view=bool(access_dict['can_view']),
                can_edit=bool(access_dict['can_edit']),
                granted_at=access_dict['granted_at'],
                expires_at=access_dict['expires_at'],
                is_active=bool(access_dict['is_active'])
            )
    
    # Создаем PageFullInfo
    page_info = schemas.PageFullInfo(
        id_page=uuid.UUID(str(page_dict['id_page'])),
        epitaph=page_dict.get('epitaph'),
        biography=page_dict.get('biography'),
        is_public=bool(page_dict['is_public']),
        is_draft=bool(page_dict['is_draft']),
        agent_id=uuid.UUID(str(page_dict['agent_id'])),
        user_id=uuid.UUID(str(page_dict['user_id'])),
        created_at=page_dict.get('created_at'),
        updated_at=page_dict.get('updated_at')
    )
    
    # Создаем AgentFullInfo
    agent_info = schemas.AgentFullInfo(
        id_agent=uuid.UUID(str(agent_dict['id_agent'])),
        full_name=agent_dict['full_name'],
        gender=agent_dict['gender'],
        birth_date=agent_dict.get('birth_date'),
        death_date=agent_dict.get('death_date'),
        place_of_birth=agent_dict.get('place_of_birth'),
        place_of_death=agent_dict.get('place_of_death'),
        avatar_url=agent_dict.get('avatar_url'),
        is_human=bool(agent_dict.get('is_human', True)),
        user_id=uuid.UUID(str(agent_dict['user_id']))
    )
    
    # Если пользователь владелец, создаем фиктивную информацию о доступе
    if access_check.get('is_owner', False) and not access_info:
        # Создаем фиктивный access_info для владельца
        short_agent_info = schemas.AgentShortInfo(
            id_agent=uuid.UUID(str(agent_dict['id_agent'])),
            full_name=agent_dict['full_name'],
            is_human=bool(agent_dict.get('is_human', True)),
            page=schemas.PageShortInfo(
                id_page=uuid.UUID(str(page_dict['id_page'])),
                is_public=bool(page_dict['is_public']),
                is_draft=bool(page_dict['is_draft'])
            )
        )
        
        # Создаем информацию о текущем пользователе как о предоставившем
        # Получаем информацию о текущем пользователе
        user_sql = text("""
            SELECT full_name, username FROM users WHERE id_user = :user_id
        """)
        user_result = db.execute(user_sql, {'user_id': str(user_id)}).fetchone()
        
        user_info = None
        if user_result:
            user_dict = dict(user_result._mapping)
            user_info = schemas.UserShortInfo(
                id_user=uuid.UUID(str(user_id)),
                full_name=user_dict.get('full_name'),
                username=user_dict.get('username')
            )
        
        access_info = schemas.PageAccessListItem(
            id_access=uuid.uuid4(),  # Генерируем временный ID
            user_id=uuid.UUID(str(user_id)),
            granted_by=uuid.UUID(str(user_id)),
            grantor_info=user_info,
            agent=short_agent_info,
            can_view=True,
            can_edit=True,
            granted_at=page_dict.get('created_at') or datetime.now(),
            expires_at=None,
            is_active=True
        )
    
    return schemas.PageAccessDetails(
        access_info=access_info,
        page=page_info,
        agent=agent_info,
        grantor_info=None,  # Можно заполнить если нужно
        current_user_permissions={
            'can_view': access_check['can_view'],
            'can_edit': access_check['can_edit']
        }
    )

# Остальные методы остаются без изменений
@router.post("/grant", response_model=schemas.PageAccessResponse)
def grant_access(
    request: schemas.GrantAccessRequest,
    db: Session = Depends(get_db),
    grantor_id: str = Depends(get_current_user_id)
):
    """Предоставить доступ к странице другому пользователю."""
    
    # Проверяем, не существует ли уже активный доступ
    existing = get_access_by_page_and_user(db, request.page_id, request.user_id)
    if existing and existing.is_active:
        raise HTTPException(
            status_code=400, 
            detail="Доступ уже предоставлен этому пользователю"
        )
    
    # Создаем данные для доступа
    access_data = schemas.PageAccessCreate(
        page_id=request.page_id,
        user_id=request.user_id,
        can_view=request.can_view,
        can_edit=request.can_edit,
        expires_at=request.expires_at,
        granted_by=grantor_id
    )
    
    # Создаем запись в базе
    db_access = create_access(db, access_data, grantor_id)
    
    # Возвращаем ответ
    return schemas.PageAccessResponse.from_orm(db_access)


@router.put("/{access_id}", response_model=schemas.PageAccessResponse)
def update_access_record(
    access_id: uuid.UUID,
    update_data: schemas.PageAccessUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user_id)
):
    """Обновить параметры доступа (только предоставивший доступ)."""
    # Проверяем, что текущий пользователь является grantor
    db_access = get_access_by_id(db, access_id)
    if not db_access:
        raise HTTPException(status_code=404, detail="Запись доступа не найдена")
    
    if db_access.granted_by != current_user:
        raise HTTPException(status_code=403, detail="Недостаточно прав для изменения")
    
    updated = update_access(db, access_id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Не удалось обновить запись")
    
    return schemas.PageAccessResponse.from_orm(updated)


@router.delete("/{access_id}")
def revoke_access(
    access_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user_id)
):
    """Отозвать доступ (деактивировать запись)."""
    db_access = get_access_by_id(db, access_id)
    if not db_access:
        raise HTTPException(status_code=404, detail="Запись доступа не найдена")
    
    if db_access.granted_by != current_user:
        raise HTTPException(status_code=403, detail="Недостаточно прав для отзыва")
    
    success = deactivate_access(db, access_id)
    if not success:
        raise HTTPException(status_code=500, detail="Не удалось отозвать доступ")
    
    return {"message": "Доступ отозван"}


@router.delete("/hard/{access_id}")
def delete_access_record(
    access_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_id)
):
    """Полностью удалить запись доступа (только для администраторов)."""
    # TODO: Проверить права администратора
    success = delete_access(db, access_id)
    if not success:
        raise HTTPException(status_code=404, detail="Запись доступа не найдена")
    
    return {"message": "Запись удалена"}