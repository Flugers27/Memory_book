"""
Pydantic схемы для валидации данных Memory Service.
"""
from pydantic import BaseModel, Field, Json
from typing import Optional, List, Any, Dict
from datetime import date, datetime
from collections import defaultdict
import uuid

# ========== BASE SCHEMAS ==========
class MemoryBase(BaseModel):
    """Базовый класс для всех схем Memory Service"""
    class Config:
        from_attributes = True  # Заменяет orm_mode в Pydantic v2
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            date: lambda v: v.isoformat() if v else None,
            uuid.UUID: lambda v: str(v) if v else None,
        }

class BiographyItem(BaseModel):
    title: str = Field(..., description="Заголовок раздела")
    info: str = Field("", description="Текстовая информация")
    titles: List['BiographyItem'] = Field(
        default_factory=list, 
        description="Вложенные подразделы"
    )
    
    class Config:
        from_attributes = True


# Для рекурсивной ссылки
BiographyItem.update_forward_refs()


# ========== AGENT SCHEMAS ==========
class AgentBase(MemoryBase):
    """Базовая схема для агента"""
    full_name: str = Field(..., max_length=255, description="Полное имя агента")
    gender: Optional[str] = Field(None, max_length=50, description="Пол")
    birth_date: Optional[date] = Field(None, description="Дата рождения")
    death_date: Optional[date] = Field(None, description="Дата смерти")
    place_of_birth: Optional[str] = Field(None, max_length=100, description="Место рождения")
    place_of_death: Optional[str] = Field(None, max_length=100, description="Место смерти")
    avatar_url: Optional[str] = Field(None, description="URL аватара")
    is_human: bool = Field(True, description="Человек")

class AgentCreate(AgentBase):
    """Схема для создания агента"""
    pass


class AgentUpdate(AgentBase):
    """Схема для обновления агента"""
    pass


class AgentInListResponse(AgentBase):
    """Схема агента в списке"""
    id_agent: uuid.UUID


class AgentResponse(AgentInListResponse):
    """Полная схема ответа для агента"""
    user_id: uuid.UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class AgentListResponse(MemoryBase):
    """Схема списка агентов"""
    user_id: uuid.UUID
    agent_list: List[AgentInListResponse] = []
    
    @classmethod
    def from_agents(cls, user_id: uuid.UUID, agents: List[Any]) -> "AgentListResponse":
        """Создает объект из списка моделей агентов"""
        agent_list = [
            AgentInListResponse(
                id_agent=agent.id_agent,
                full_name=agent.full_name,
                gender=agent.gender,
                birth_date=agent.birth_date,
                death_date=agent.death_date,
                place_of_birth=agent.place_of_birth,
                place_of_death=agent.place_of_death,
                avatar_url=agent.avatar_url,
            )
            for agent in agents
        ]
        return cls(user_id=user_id, agent_list=agent_list)


# ========== PAGE SCHEMAS ==========
class PageBase(MemoryBase):
    """Базовая схема для страницы памяти"""
    epitaph: Optional[str] = Field(None, description="Эпитафия")
    biography: Optional[List[BiographyItem]] = Field(None, description="Биография в формате JSON")
    is_public: bool = Field(False, description="Публичный доступ")
    is_draft: bool = Field(False, description="Черновик")


class PageCreate(PageBase):
    """Схема для создания страницы"""
    agent_id: uuid.UUID = Field(..., description="ID агента памяти")


class PageUpdate(PageBase):
    """Схема для обновления страницы"""
    pass


class PageInListResponse(PageBase):
    """Схема страницы в списке"""
    id_page: uuid.UUID
    updated_at: datetime


class PageResponse(PageInListResponse):
    """Полная схема ответа для страницы"""
    agent_id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime


class PageListResponse(MemoryBase):
    """Схема списка страниц"""
    user_id: uuid.UUID
    agent_id: uuid.UUID
    page_list: List[PageInListResponse] = []
    
    @classmethod
    def from_pages(cls, user_id: uuid.UUID, agent_id: uuid.UUID, pages: List[Any]) -> "PageListResponse":
        """Создает объект из списка моделей страниц"""
        page_list = [
            PageInListResponse(
                id_page=page.id_page,
                epitaph=page.epitaph,
                biography=page.biography,
                is_public=page.is_public,
                is_draft=page.is_draft,
                updated_at=page.updated_at,
            )
            for page in pages
        ]
        return cls(user_id=user_id, agent_id=agent_id, page_list=page_list)


# ========== PUBLIC SCHEMAS ==========
class PublicPageResponse(PageBase):
    """Публичная схема страницы (без user_id)"""
    id_page: uuid.UUID
    agent_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class PublicAgentResponse(AgentBase):
    """Публичная схема агента (без user_id)"""
    id_agent: uuid.UUID
    page: Optional[PublicPageResponse] = None


# ========== COMBINED SCHEMAS ==========
class PublicMemoryPageResponse(PublicAgentResponse):
    """Публичная схема агента со страницей"""
    @classmethod
    def from_agent_and_page(cls, agent: Any, page: Optional[Any] = None) -> "PublicMemoryPageResponse":
        """Создает объект из модели агента и опционально страницы"""
        page_response = None

        if page:
            biography_val = page.biography
            if str(page.biography)[0] =="{":
               biography_val = [page.biography]

            page_response = PublicPageResponse(
                id_page=page.id_page,
                epitaph=page.epitaph,
                biography=biography_val,
                is_public=page.is_public,
                is_draft=page.is_draft,
                agent_id=page.agent_id,
                created_at=page.created_at,
                updated_at=page.updated_at,
            )
        
        return cls(
            id_agent=agent.id_agent,
            full_name=agent.full_name,
            gender=agent.gender,
            birth_date=agent.birth_date,
            death_date=agent.death_date,
            place_of_birth=agent.place_of_birth,
            place_of_death=agent.place_of_death,
            avatar_url=agent.avatar_url,
            page=page_response,
        )
        
class PublicMemoryPageListResponse(MemoryBase):
    """Схема списка публичных страниц памяти"""
    memory_page_list: List[PublicMemoryPageResponse] = []
    
    @classmethod
    def from_public_memory_pages(cls, memory_pages: List[Any]) -> "PublicMemoryPageListResponse":
        """Создает список публичных страниц памяти"""
        memory_page_list = [
            PublicMemoryPageResponse.from_agent_and_page(agent, page)
            for agent, page in memory_pages
        ]
        return cls(memory_page_list=memory_page_list)

class MemoryPageResponse(MemoryBase):
    """Объединенная схема агента и его страниц (для авторизованных пользователей)"""
    agent: AgentResponse  # Объект агента
    pages: List[PageResponse] = []  # Список страниц этого агента
    

    @classmethod
    def from_models(cls, agent: Any, pages: List[Any]) -> "MemoryPageResponse":
        """Создает объект из модели агента и списка его страниц"""
        # Сначала создаем AgentResponse
        agent_response = AgentResponse(
            id_agent=agent.id_agent,
            full_name=agent.full_name,
            gender=agent.gender,
            birth_date=agent.birth_date,
            death_date=agent.death_date,
            place_of_birth=agent.place_of_birth,
            place_of_death=agent.place_of_death,
            avatar_url=agent.avatar_url,
            user_id=agent.user_id,
            created_at=agent.created_at,
            updated_at=agent.updated_at,
        )
        
        # Затем создаем список PageResponse
        page_responses = []

        for page in pages:
            if not page:
                return cls(agent=agent_response, pages=page_responses)

            page_responses.append(PageResponse(
                id_page=page.id_page,
                epitaph=page.epitaph,
                biography=page.biography,
                is_public=page.is_public,
                is_draft=page.is_draft,
                agent_id=page.agent_id,
                user_id=page.user_id,
                created_at=page.created_at,
                updated_at=page.updated_at,
            ))
        
        # Возвращаем объект с полями agent и pages
        return cls(
            agent=agent_response,
            pages=page_responses
        )


class MemoryPageListResponse(MemoryBase):
    """Схема списка страниц памяти (агенты с их страницами)"""
    user_id: uuid.UUID
    memory_page_list: List[MemoryPageResponse] = []
    
    @classmethod
    def from_memory_pages(cls, user_id: uuid.UUID, memory_pages: List[tuple]) -> "MemoryPageListResponse":
        """
        Создает список из объектов, содержащих агента и его страницы
        
        Args:
            user_id: ID пользователя
            memory_pages: Список кортежей (agent, page)
        """
        # Группируем страницы по агентам
        pages_by_agent = defaultdict(list)
        agents_by_id = {}
        
        for agent, page in memory_pages:
            agent_id = agent.id_agent
            agents_by_id[agent_id] = agent  # Последний агент перезапишет предыдущего
            #if page:
            pages_by_agent[agent_id].append(page)
        
        # Создаем ответы в одном цикле
        memory_page_list = [
            MemoryPageResponse.from_models(agents_by_id[agent_id], pages)
            for agent_id, pages in pages_by_agent.items()
        ]
        
        return cls(user_id=user_id, memory_page_list=memory_page_list)