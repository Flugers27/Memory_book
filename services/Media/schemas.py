"""
Pydantic схемы для сервиса Media
"""
from pydantic import BaseModel, Field, validator, ConfigDict
from typing import Optional, List
from datetime import datetime
import uuid


class MediaBase(BaseModel):
    """Базовая схема для медиа"""
    page_id: Optional[uuid.UUID] = None
    file_extension: str = Field(..., max_length=10)
    file_size: int = Field(..., ge=1)
    media_type: str = Field(..., max_length=20)
    mime_type: str = Field(..., max_length=100)
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[int] = None
    is_public: bool = False
    sort_order: Optional[int] = None
    is_temp: bool = True  # По умолчанию временный файл


class MediaCreate(MediaBase):
    """Схема для создания медиа"""
    user_id: uuid.UUID


class MediaUploadResponse(BaseModel):
    """Ответ на загрузку медиа"""
    id_media: uuid.UUID
    filename: str
    url: str
    temp_url: Optional[str] = None
    expires_at: Optional[datetime] = None
    message: str


class MediaUpdate(BaseModel):
    """Схема для обновления медиа"""
    page_id: Optional[uuid.UUID] = None
    is_public: Optional[bool] = None
    sort_order: Optional[int] = None
    is_temp: Optional[bool] = None


class MediaResponse(BaseModel):
    """Схема ответа с информацией о медиа"""
    id_media: uuid.UUID
    user_id: uuid.UUID
    page_id: Optional[uuid.UUID] = None
    file_extension: str
    file_size: int
    media_type: str
    mime_type: str
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[int] = None
    has_thumbnail: Optional[bool] = None
    has_medium: Optional[bool] = None
    is_public: bool
    sort_order: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    is_temp: bool
    
    model_config = ConfigDict(from_attributes=True)


class MediaListResponse(BaseModel):
    """Схема ответа со списком медиа"""
    media: List[MediaResponse]
    total: int
    page: int
    page_size: int


class TempMediaCleanupResponse(BaseModel):
    """Ответ на очистку временных медиа"""
    deleted_count: int
    message: str


class MediaConfirmRequest(BaseModel):
    """Запрос на подтверждение временного медиа"""
    page_id: uuid.UUID
    make_permanent: bool = True


class MediaConfirmResponse(BaseModel):
    """Ответ на подтверждение медиа"""
    id_media: uuid.UUID
    is_temp: bool
    page_id: uuid.UUID
    message: str