"""
Pydantic схемы для сервиса Family Tree
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Any
from datetime import datetime
import uuid


# ========== Базовые схемы ==========

class FamilyTreeBase(BaseModel):
    """Базовая схема семейного древа"""
    name_family_tree: str = Field(..., description="Название древа")
    is_public: bool = Field(False, description="Публичный доступ")
    is_draft: bool = Field(True, description="Черновик")

    @validator('name_family_tree', pre=True, always=True)
    def strip_name(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v


class FamilyTreeCreate(FamilyTreeBase):
    """Схема для создания древа"""
    pass


class FamilyTreeUpdate(BaseModel):
    """Схема для обновления древа"""
    name_family_tree: Optional[str] = Field(None, description="Название древа")
    is_public: Optional[bool] = Field(None, description="Публичный доступ")
    is_draft: Optional[bool] = Field(None, description="Черновик")


class FamilyTreeResponse(FamilyTreeBase):
    """Схема ответа с информацией о древе"""
    id_family_tree: uuid.UUID
    user_id: uuid.UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class FamilyTreeListResponse(BaseModel):
    """Схема списка древ"""
    trees: List[FamilyTreeResponse]
    total: int
    page: int = 1
    page_size: int = 20


# ========== Агенты в древе ==========

class FamilyTreeAgentResponse(BaseModel):
    """Схема агента в древе"""
    id_tree_agent: uuid.UUID
    family_tree_id: uuid.UUID
    agent_id: uuid.UUID

    class Config:
        orm_mode = True


class AddAgentRequest(BaseModel):
    """Запрос на добавление агента в древо"""
    agent_id: uuid.UUID = Field(..., description="ID агента")


# ========== Связи между агентами ==========

class RelationshipBase(BaseModel):
    """Базовая схема родственной связи"""
    type_relative: str = Field(..., description="Тип родства (parent, child, spouse, sibling, etc.)")
    is_blood_relative: bool = Field(False, description="Кровное родство")
    agent_from: uuid.UUID = Field(..., description="Агент-источник")
    agent_to: uuid.UUID = Field(..., description="Агент-цель")

    @validator('type_relative', pre=True, always=True)
    def strip_type_relative(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v


class RelationshipCreate(RelationshipBase):
    """Схема для создания связи"""
    pass


class RelationshipUpdate(BaseModel):
    """Схема для обновления связи"""
    type_relative: Optional[str] = Field(None, description="Тип родства")
    is_blood_relative: Optional[bool] = Field(None, description="Кровное родство")

    @validator('type_relative', pre=True, always=True)
    def strip_type_relative(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v


class RelationshipResponse(RelationshipBase):
    """Схема ответа с информацией о связи"""
    id_relationships: uuid.UUID
    family_tree_id: uuid.UUID
    user_id: uuid.UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class RelationshipListResponse(BaseModel):
    """Схема списка связей"""
    relationships: List[RelationshipResponse]
    total: int


# ========== Полное древо ==========

class FamilyTreeFullResponse(FamilyTreeResponse):
    """Схема полной информации о древе со всеми агентами и связями"""
    agents: List[FamilyTreeAgentResponse] = []
    relationships: List[RelationshipResponse] = []


# ========== Публичные схемы ==========

class PublicFamilyTreeResponse(FamilyTreeBase):
    """Публичная схема древа (без user_id)"""
    id_family_tree: uuid.UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class PublicFamilyTreeListResponse(BaseModel):
    """Схема списка публичных древ"""
    trees: List[PublicFamilyTreeResponse]
    total: int
    page: int = 1
    page_size: int = 20


class PublicFamilyTreeFullResponse(PublicFamilyTreeResponse):
    """Полная публичная информация о древе"""
    agents: List[FamilyTreeAgentResponse] = []
    relationships: List[RelationshipResponse] = []


# ========== Вспомогательные схемы ==========

class DeleteResponse(BaseModel):
    """Схема ответа при удалении"""
    message: str