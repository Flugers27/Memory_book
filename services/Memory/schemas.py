"""
Pydantic схемы для валидации данных Memory Service.
"""
from pydantic import BaseModel, Field, Json
from typing import Optional, List
from datetime import date, datetime
import uuid

# ========== BASE SCHEMAS ==========
class MemoryBase(BaseModel):
    class Config:
        from_attributes = True  # Заменяет orm_mode в Pydantic v2

# ========== MEMORY AGENT SCHEMAS ==========
class MemoryAgentBase(MemoryBase):
    full_name: str = Field(..., max_length=255, description="Полное имя агента")
    birth_date: Optional[date] = Field(None, description="Дата рождения")
    death_date: Optional[date] = Field(None, description="Дата смерти")
    avatar_url: Optional[str] = Field(None, description="URL аватара")

class MemoryAgentCreate(MemoryAgentBase):
    pass

class MemoryAgentUpdate(MemoryBase):
    full_name: Optional[str] = Field(None, max_length=255)
    birth_date: Optional[date] = None
    death_date: Optional[date] = None
    avatar_url: Optional[str] = None

class MemoryAgent(MemoryAgentBase):
    id_agent: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

class MemoryAgentWithPages(MemoryAgent):
    memory_pages: List["MemoryPage"] = []

# ========== MEMORY PAGE SCHEMAS ==========
class MemoryPageBase(MemoryBase):
    epitaph: Optional[str] = Field(None, description="Эпитафия")
    place_of_birth: Optional[str] = Field(None, max_length=500, description="Место рождения")
    place_of_death: Optional[str] = Field(None, max_length=500, description="Место смерти")
    biography: Json = Field(None, description="Биография")
    is_public: bool = Field(False, description="Публичный доступ")
    is_draft: bool = Field(False, description="Черновик")
    memory_agent_id: uuid.UUID = Field(..., description="ID агента памяти")

class MemoryPageCreate(MemoryPageBase):
    pass

class MemoryPageUpdate(MemoryBase):
    epitaph: Optional[str] = None
    place_of_birth: Optional[str] = None
    place_of_death: Optional[str] = None
    biography: Json = None
    is_public: Optional[bool] = None
    is_draft: Optional[bool] = None

class MemoryPage(MemoryPageBase):
    id_page: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

class MemoryPageWithTitles(MemoryPage):
    memory_titles: List["MemoryTitles"] = []

# ========== MEMORY TITLES SCHEMAS ==========
class MemoryTitlesBase(MemoryBase):
    head: str = Field(..., max_length=100, description="Заголовок")
    body: Optional[str] = Field(None, description="Содержимое")
    sort_order: int = Field(0, description="Порядок сортировки")
    parent_id: Optional[uuid.UUID] = Field(None, description="ID родительского заголовка")
    page_id: uuid.UUID = Field(..., description="ID страницы")

class MemoryTitlesCreate(MemoryTitlesBase):
    pass

class MemoryTitlesUpdate(MemoryBase):
    head: Optional[str] = Field(None, max_length=100)
    body: Optional[str] = None
    sort_order: Optional[int] = None

class MemoryTitles(MemoryTitlesBase):
    id_titles: uuid.UUID
    created_at: datetime
    expires_at: datetime

class MemoryTitlesWithChildren(MemoryTitles):
    children: List["MemoryTitles"] = []

# ========== COMPOSITE SCHEMAS ==========
class FullMemoryPageResponse(MemoryBase):
    """Полная информация о странице с агентом и заголовками"""
    memory_page: MemoryPageWithTitles
    memory_agent: MemoryAgent
    memory_titles: List[MemoryTitlesWithChildren] = []

# Обновляем ссылки для рекурсивных типов
MemoryPageWithTitles.update_forward_refs()
MemoryTitlesWithChildren.update_forward_refs()