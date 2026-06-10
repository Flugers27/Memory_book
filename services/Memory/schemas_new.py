"""
Pydantic схемы для валидации данных Memory Service.
"""
from pydantic import BaseModel, Field, Json, validator
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

class BiographySection(BaseModel):
    """Секция биографии

    Одна секция в структуре биографии. Секции могут быть вложенными:
    level=1 — основной раздел, level=2 — подраздел, level=3 — подподраздел.
    Порядок секций определяется полем order.
    """
    title: str = Field(
        ...,
        description="Заголовок раздела (например: 'Ранние годы', 'Образование', 'Трудовая биография')"
    )
    level: int = Field(
        1,
        ge=1, le=10,
        description="Уровень вложенности: 1 — основной раздел, 2 — подраздел, 3 — подподраздел и т.д."
    )
    order: int = Field(
        0,
        ge=0,
        description="Порядок сортировки. Секции сортируются по возрастанию order. Рекомендация: 10, 20, 30... для основных разделов, 35, 40... для подразделов"
    )
    content: str = Field(
        "",
        description="HTML-содержимое секции. Можно использовать <p> для абзацев, <img> для изображений, <b>, <i> и другие HTML-теги"
    )


class BiographyData(BaseModel):
    """Структура биографии в формате JSONB

    Хранится в колонке biography таблицы pages.
    Содержит список ID медиафайлов и массив секций с HTML-содержимым.

    Формат:
    {
      "media_ids": ["uuid-медиафайла1", "uuid-медиафайла2"],
      "sections": [
        {
          "title": "Название раздела",
          "level": 1,
          "order": 10,
          "content": "<p>HTML-содержимое раздела</p>"
        }
      ]
    }

    media_ids — список UUID медиафайлов из Media Service, привязанных к биографии.
    sections — массив секций биографии, отсортированных по полю order.
    Каждая секция содержит заголовок (title), уровень вложенности (level),
    порядковый номер (order) и HTML-содержимое (content).
    """
    media_ids: List[uuid.UUID] = Field(
        default_factory=list,
        description="Список UUID медиафайлов из Media Service, привязанных к данной биографии. Может быть пустым."
    )
    sections: List[BiographySection] = Field(
        default_factory=list,
        description="Массив секций биографии. Секции автоматически сортируются по полю order. Может быть пустым."
    )


def convert_old_biography_to_new(bio: Any) -> Any:
    """Преобразует старый формат биографии в новый.

    Старый формат (рекурсивный список):
        [
            {"title": "...", "info": "...", "titles": [{"title": "...", "info": "...", "titles": [...]}]},
            ...
        ]

    Новый формат (плоский список секций):
        {
            "media_ids": [],
            "sections": [
                {"title": "...", "level": 1, "order": 10, "content": "<p>...</p>"},
                ...
            ]
        }

    Если bio уже в новом формате (dict с ключами media_ids/sections) — возвращается как есть.
    Если bio — список (старый формат) — рекурсивно преобразуется в новый.
    Если bio — None или уже BiographyData — возвращается без изменений.
    """
    if bio is None or isinstance(bio, BiographyData):
        return bio

    # Если это уже новый формат (dict с ключами media_ids и sections)
    if isinstance(bio, dict):
        if "media_ids" in bio or "sections" in bio:
            return bio
        # Если это dict, но не новый формат — возможно, одиночный объект старого формата
        if "title" in bio:
            bio = [bio]  # Оборачиваем в список для единообразной обработки
        else:
            return bio

    # Если это список — старый формат
    if isinstance(bio, list):
        sections = []
        order_counter = 0

        def flatten_items(items: List[Any], parent_level: int = 1):
            """Рекурсивно преобразует старые вложенные items в плоские секции"""
            nonlocal order_counter
            for item in items:
                if not isinstance(item, dict):
                    continue
                title = item.get("title", "")
                info = item.get("info", "")
                titles = item.get("titles") or item.get("items") or []

                # Конвертируем info (plain text) в content (HTML)
                content = f"<p>{info}</p>" if info else ""

                order_counter += 10
                sections.append({
                    "title": title,
                    "level": parent_level,
                    "order": order_counter,
                    "content": content,
                })

                # Рекурсивно обрабатываем вложенные titles
                if isinstance(titles, list) and titles:
                    flatten_items(titles, parent_level + 1)

        flatten_items(bio)
        return {"media_ids": [], "sections": sections}

    return bio


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
                is_human=agent.is_human,
            )
            for agent in agents
        ]
        return cls(user_id=user_id, agent_list=agent_list)


# ========== PAGE SCHEMAS ==========
class PageBase(MemoryBase):
    """Базовая схема для страницы памяти"""
    epitaph: Optional[str] = Field(None, description="Эпитафия")
    biography: Optional[BiographyData] = Field(None, description="Биография в формате JSON")
    is_public: bool = Field(False, description="Публичный доступ")
    is_draft: bool = Field(False, description="Черновик")

    @validator('biography', pre=True, always=True)
    def validate_biography(cls, v):
        """Преобразует biography из БД в BiographyData.

        Поддерживает:
        - Новый формат: {"media_ids": [...], "sections": [...]}
        - Старый формат: [{"title": "...", "info": "...", "titles": [...]}]
        - None
        - Уже BiographyData
        """
        if v is None or isinstance(v, BiographyData):
            return v
        # Конвертируем старый формат в новый, затем в BiographyData
        converted = convert_old_biography_to_new(v)
        if isinstance(converted, dict):
            return BiographyData(**converted)
        return converted


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
                biography=convert_old_biography_to_new(page.biography),
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
            # Преобразуем biography из любого формата (старый или новый) в BiographyData
            biography_data = convert_old_biography_to_new(page.biography)

            page_response = PublicPageResponse(
                id_page=page.id_page,
                epitaph=page.epitaph,
                biography=biography_data,
                is_public=page.is_public,
                is_draft=page.is_draft,
                agent_id=page.agent_id,
                created_at=page.created_at,
                updated_at=page.updated_at,
            )
        
        return cls(
            id_agent=agent.id_agent,
            full_name=agent.full_name,
            is_human=agent.is_human,
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
        print(agent.is_human)
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
            is_human=agent.is_human,
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
                biography=convert_old_biography_to_new(page.biography),
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