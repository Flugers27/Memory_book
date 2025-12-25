"""
Схемы Pydantic для управления доступом.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Any
from datetime import datetime, date
import uuid


class UserShortInfo(BaseModel):
    """Краткая информация о пользователе"""
    id_user: Optional[uuid.UUID]
    full_name: Optional[str]
    username: Optional[str]

    class Config:
        from_attributes = True


class PageShortInfo(BaseModel):
    """Краткая информация о странице"""
    id_page: uuid.UUID
    is_public: bool
    is_draft: bool

    class Config:
        from_attributes = True


class AgentShortInfo(BaseModel):
    """Краткая информация об агенте"""
    id_agent: uuid.UUID
    full_name: Optional[str]
    is_human: bool
    page: Optional[PageShortInfo] = None

    class Config:
        from_attributes = True


class PageAccessListItem(BaseModel):
    """Элемент списка доступа к странице (для получения доступа)"""
    id_access: uuid.UUID
    user_id: uuid.UUID
    granted_by: Optional[uuid.UUID]
    grantor_info: Optional[UserShortInfo] = None
    agent: Optional[AgentShortInfo] = None
    can_view: bool
    can_edit: bool
    granted_at: datetime
    expires_at: Optional[datetime]
    is_active: bool

    class Config:
        from_attributes = True


class GrantedAccessListItem(BaseModel):
    """Элемент списка предоставленных доступов (для предоставления доступа)"""
    id_access: uuid.UUID
    granted_by: uuid.UUID
    user_id: uuid.UUID
    recipient_info: Optional[UserShortInfo] = None
    agent: Optional[AgentShortInfo] = None
    can_view: bool
    can_edit: bool
    granted_at: datetime
    expires_at: Optional[datetime]
    is_active: bool

    class Config:
        from_attributes = True


class PageAccessListResponse(BaseModel):
    """Ответ со списком доступов к страницам"""
    items: List[PageAccessListItem]
    total: int
    page: int
    size: int


class GrantedAccessListResponse(BaseModel):
    """Ответ со списком предоставленных доступов"""
    items: List[GrantedAccessListItem]
    total: int
    page: int
    size: int


class PageAccessBase(BaseModel):
    """Базовая схема доступа к странице"""
    page_id: uuid.UUID
    user_id: uuid.UUID
    can_view: bool = False
    can_edit: bool = False
    expires_at: Optional[datetime] = None
    is_active: bool = True


class PageAccessCreate(PageAccessBase):
    """Схема для создания доступа"""
    granted_by: Optional[uuid.UUID] = None


class PageAccessUpdate(BaseModel):
    """Схема для обновления доступа"""
    can_view: Optional[bool] = None
    can_edit: Optional[bool] = None
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None


class PageAccessResponse(PageAccessBase):
    """Полный ответ с информацией о доступе"""
    id_access: uuid.UUID
    granted_by: Optional[uuid.UUID]
    granted_at: datetime

    class Config:
        from_attributes = True


class GrantAccessRequest(BaseModel):
    """Запрос на предоставление доступа"""
    page_id: uuid.UUID
    user_id: uuid.UUID
    can_view: bool = True
    can_edit: bool = False
    expires_at: Optional[datetime] = None


class RevokeAccessRequest(BaseModel):
    """Запрос на отзыв доступа"""
    page_id: uuid.UUID
    user_id: uuid.UUID


# Вспомогательные функции для преобразования результатов SQL-запросов
def build_page_access_item_from_raw(row: Any) -> PageAccessListItem:
    """Строит PageAccessListItem из сырых данных SQL-запроса"""
    # Преобразуем строку в словарь или работаем с объектом
    if hasattr(row, '_asdict'):
        data = row._asdict()
    elif hasattr(row, '__dict__'):
        data = row.__dict__.copy()
        if '_sa_instance_state' in data:
            del data['_sa_instance_state']
    else:
        data = dict(row)
    
    item_data = {
        "id_access": data.get('id_access'),
        "user_id": data.get('user_id'),
        "granted_by": data.get('granted_by'),
        "can_view": data.get('can_view', False),
        "can_edit": data.get('can_edit', False),
        "granted_at": data.get('granted_at'),
        "expires_at": data.get('expires_at'),
        "is_active": data.get('is_active', True),
    }
    
    # Добавляем информацию о предоставившем доступ
    if data.get('grantor_full_name') or data.get('grantor_username'):
        item_data["grantor_info"] = {
            "id_user": data.get('granted_by'),
            "full_name": data.get('grantor_full_name'),
            "username": data.get('grantor_username')
        }
    
    # Добавляем информацию об агенте
    if data.get('id_agent'):
        agent_data = {
            "id_agent": data.get('id_agent'),
            "full_name": data.get('agent_full_name'),
            "is_human": data.get('is_human', True),
        }
        
        # Добавляем информацию о странице
        if data.get('id_page'):
            agent_data["page"] = {
                "id_page": data.get('id_page'),
                "is_public": data.get('is_public', False),
                "is_draft": data.get('is_draft', False)
            }
        
        item_data["agent"] = agent_data
    
    return PageAccessListItem(**item_data)


def build_granted_access_item_from_raw(row: Any) -> GrantedAccessListItem:
    """Строит GrantedAccessListItem из сырых данных SQL-запроса"""
    if hasattr(row, '_asdict'):
        data = row._asdict()
    elif hasattr(row, '__dict__'):
        data = row.__dict__.copy()
        if '_sa_instance_state' in data:
            del data['_sa_instance_state']
    else:
        data = dict(row)
    
    item_data = {
        "id_access": data.get('id_access'),
        "granted_by": data.get('granted_by'),
        "user_id": data.get('user_id'),
        "can_view": data.get('can_view', False),
        "can_edit": data.get('can_edit', False),
        "granted_at": data.get('granted_at'),
        "expires_at": data.get('expires_at'),
        "is_active": data.get('is_active', True),
    }
    
    # Добавляем информацию о получателе
    if data.get('recipient_full_name') or data.get('recipient_username'):
        item_data["recipient_info"] = {
            "id_user": data.get('user_id'),
            "full_name": data.get('recipient_full_name'),
            "username": data.get('recipient_username')
        }
    
    # Добавляем информацию об агенте
    if data.get('id_agent'):
        agent_data = {
            "id_agent": data.get('id_agent'),
            "full_name": data.get('agent_full_name'),
            "is_human": data.get('is_human', True),
        }
        
        # Добавляем информацию о странице
        if data.get('id_page'):
            agent_data["page"] = {
                "id_page": data.get('id_page'),
                "is_public": data.get('is_public', False),
                "is_draft": data.get('is_draft', False)
            }
        
        item_data["agent"] = agent_data
    
    return GrantedAccessListItem(**item_data)


# Добавим в конец файла schemas.py
# ... после существующих схем ...

class AgentFullInfo(BaseModel):
    """Полная информация об агенте"""
    id_agent: uuid.UUID
    full_name: Optional[str]
    gender: Optional[str]
    birth_date: Optional[date]
    death_date: Optional[date]
    place_of_birth: Optional[str]
    place_of_death: Optional[str]
    avatar_url: Optional[str]
    is_human: bool
    user_id: uuid.UUID
    
    class Config:
        from_attributes = True


class PageFullInfo(BaseModel):
    """Полная информация о странице"""
    id_page: uuid.UUID
    epitaph: Optional[str]
    biography: Optional[Any]  # Может быть JSON или другим типом
    is_public: bool
    is_draft: bool
    agent_id: uuid.UUID
    user_id: uuid.UUID
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class PageAccessDetails(BaseModel):
    """Подробная информация о доступе к странице"""
    access_info: Optional[PageAccessListItem] = None
    page: PageFullInfo
    agent: AgentFullInfo
    grantor_info: Optional[UserShortInfo]
    current_user_permissions: dict = Field(
        default_factory=lambda: {"can_view": False, "can_edit": False}
    )
    
    class Config:
        from_attributes = True


class PageAccessCheckResponse(BaseModel):
    """Ответ на проверку доступа к странице"""
    has_access: bool
    can_view: bool = False
    can_edit: bool = False
    access_details: Optional[PageAccessDetails] = None
    message: Optional[str] = None
    
    class Config:
        from_attributes = True


# Добавим в конец schemas.py

def create_page_access_details_from_models(
    access_control: Optional[Any],
    page: Any,
    agent: Any,
    grantor: Optional[Any] = None,
    recipient: Optional[Any] = None,
    current_user_id: Optional[uuid.UUID] = None
) -> PageAccessDetails:
    """
    Создает объект PageAccessDetails из моделей SQLAlchemy.
    
    Args:
        access_control: Модель PageAccessControl или None
        page: Модель PageBD
        agent: Модель AgentBD
        grantor: Модель User (кто предоставил доступ)
        recipient: Модель User (кому предоставлен доступ)
        current_user_id: ID текущего пользователя для определения прав
    
    Returns:
        PageAccessDetails объект
    """
    # Преобразуем страницу
    page_info = PageFullInfo(
        id_page=uuid.UUID(page.id_page),
        epitaph=page.epitaph,
        biography=page.biography,
        is_public=page.is_public,
        is_draft=page.is_draft,
        agent_id=uuid.UUID(page.agent_id),
        user_id=uuid.UUID(page.user_id),
        created_at=page.created_at,
        updated_at=page.updated_at
    )
    
    # Преобразуем агента
    agent_info = AgentFullInfo(
        id_agent=uuid.UUID(agent.id_agent),
        full_name=agent.full_name,
        gender=agent.gender,
        birth_date=agent.birth_date,
        death_date=agent.death_date,
        place_of_birth=agent.place_of_birth,
        place_of_death=agent.place_of_death,
        avatar_url=agent.avatar_url,
        is_human=agent.is_human,
        user_id=uuid.UUID(agent.user_id)
    )
    
    # Преобразуем информацию о доступе
    access_info = None
    if access_control:
        # Определяем права
        can_view = access_control.can_view if hasattr(access_control, 'can_view') else False
        can_edit = access_control.can_edit if hasattr(access_control, 'can_edit') else False
        
        # Преобразуем grantor
        grantor_info = None
        if grantor:
            grantor_info = UserShortInfo(
                id_user=grantor.id_user,
                full_name=grantor.full_name,
                username=grantor.username
            )
        
        access_info = PageAccessListItem(
            id_access=access_control.id_access,
            user_id=access_control.user_id,
            granted_by=access_control.granted_by,
            grantor_info=grantor_info,
            agent=AgentShortInfo(
                id_agent=uuid.UUID(agent.id_agent),
                full_name=agent.full_name,
                is_human=agent.is_human,
                page=PageShortInfo(
                    id_page=uuid.UUID(page.id_page),
                    is_public=page.is_public,
                    is_draft=page.is_draft
                )
            ),
            can_view=can_view,
            can_edit=can_edit,
            granted_at=access_control.granted_at,
            expires_at=access_control.expires_at,
            is_active=access_control.is_active if hasattr(access_control, 'is_active') else True
        )
    
    # Определяем права текущего пользователя
    current_user_permissions = {"can_view": False, "can_edit": False}
    if current_user_id:
        # Проверяем, является ли текущий пользователь владельцем
        if str(page.user_id) == str(current_user_id):
            current_user_permissions = {"can_view": True, "can_edit": True}
        elif access_control and str(access_control.user_id) == str(current_user_id):
            current_user_permissions = {
                "can_view": access_control.can_view,
                "can_edit": access_control.can_edit
            }
    
    return PageAccessDetails(
        access_info=access_info,
        page=page_info,
        agent=agent_info,
        grantor_info=UserShortInfo(
            id_user=grantor.id_user,
            full_name=grantor.full_name,
            username=grantor.username
        ) if grantor else None,
        current_user_permissions=current_user_permissions
    )