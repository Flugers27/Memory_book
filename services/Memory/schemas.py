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
        json_encoders = {
            str: lambda v: str(v) if v else None,}

class AgentBase(MemoryBase):
    full_name: str = Field(..., max_length=255, description="Полное имя агента")
    gender: Optional[str] = Field(..., max_length=255, description="Пол")
    birth_date: Optional[date] = Field(None, description="Дата рождения")
    death_date: Optional[date] = Field(None, description="Дата смерти")
    place_of_birth: Optional[str] = Field(..., max_length=100, description="Место рождения")
    place_of_death: Optional[str] = Field(..., max_length=100, description="Место смерти")
    avatar_url: Optional[str] = Field(None, description="URL аватара")

class PageBase(MemoryBase):
    epitaph: Optional[str] = Field(None, description="Эпитафия")
    biography: Json = Field(None, description="Биография")
    is_public: bool = Field(False, description="Публичный доступ")
    is_draft: bool = Field(False, description="Черновик")
    memory_agent_id: str = Field(..., description="ID агента памяти")


# ========== MEMORY RESPONSE SCHEMAS ==========
class AgentResponse(MemoryBase):
    id_agent: str
    full_name: str
    gender: Optional[str] = None
    birth_date: Optional[date] = None
    death_date: Optional[date] = None
    place_of_birth_date: Optional[date] = None
    place_of_death_date: Optional[date] = None
    avatar_url: Optional[str] = None
    user_id: str

class PageResponse(MemoryBase):
    id_page: str
    epitaph: Optional[str] = None
    biography: Json = None
    is_public: bool
    is_draft: bool
    memory_agent_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime


# ========== MEMORY RESPONSE LIST SCHEMAS ==========
class AgentInListResponse(MemoryBase):
    id_agent: str
    full_name: str
    gender: Optional[str] = None
    birth_date: Optional[date] = None
    death_date: Optional[date] = None
    place_of_birth_date: Optional[date] = None
    place_of_death_date: Optional[date] = None
    avatar_url: Optional[str] = None


class AgentListResponse(MemoryBase):
    user_id: str = None
    agent_list: List[AgentInListResponse] = []

    def write_list(self, agents):
        agent_list = []

        for agent in agents:
            agent_list.append(AgentInListResponse(
                id_agent=str(agent.id_agent),  # Оставляем как UUID, Pydantic сам сериализует в строку
                full_name=agent.full_name,
                gender=agent.gender,
                birth_date=agent.birth_date,
                death_date=agent.death_date,
                place_of_birth=agent.place_of_birth,
                place_of_death=agent.place_of_death,
                avatar_url=agent.avatar_url,
            ))
        
        self.user_id = str(agents[0].user_id)
        self.agent_list = agent_list

class PageInListResponse(MemoryBase):
    id_page: str
    epitaph: Optional[str] = None
    is_public: bool
    is_draft: bool
    updated_at: datetime

class PageListResponse(MemoryBase):
    user_id: Optional[str] = None
    memory_agent_id: str 
    page_list: List[PageResponse]

#class MemoryPageInListResponse(AgentInListResponse):
 #   page: Optional[PublicPageResponse] = None

class MemoryPageListResponse(MemoryBase):
    user_id: str
    memory_page_list: List[AgentInListResponse]


# ========== MEMORY RESPONSE PUBLIC SCHEMAS ==========
class PublicPageResponse(MemoryBase):
    id_page: str
    epitaph: Optional[str] = None
    biography: Json = None
    is_public: bool
    is_draft: bool
    memory_agent_id: str
    created_at: datetime
    updated_at: datetime

class PublicAgentResponse(MemoryBase):
    id_agent: str
    full_name: str
    gender: str
    birth_date: Optional[date] = None
    death_date: Optional[date] = None
    place_of_birth: Optional[str] = None
    place_of_death: Optional[str] = None
    avatar_url: Optional[str] = None
    page: Optional[PublicPageResponse] = None




# ========== MEMORY CREATE SCHEMAS ==========
class AgentCreate(AgentBase):
    pass

class PageCreate(PageBase):
    pass

# ========== MEMORY UPDATE SCHEMAS ==========
class AgentUpdate(AgentBase):
    pass

class PageUpdate(MemoryBase):
    epitaph: Optional[str] = None
    biography: Json = None
    is_public: Optional[bool] = None
    is_draft: Optional[bool] = None

# ========== MEMORY CREATE SCHEMAS ==========


