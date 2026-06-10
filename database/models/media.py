"""
SQLAlchemy модель для медиафайлов (соответствует существующей таблице media в БД)
"""
from sqlalchemy import Column, String, Text, Integer, BigInteger, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from database.base import Base


class MediaBD(Base):
    __tablename__ = "media"
    __table_args__ = {'extend_existing': True}
    
    id_media = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)  # кто загрузил
    page_id = Column(UUID(as_uuid=True), nullable=False)
    
    file_extension = Column(String(10), nullable=False)  # character в БД, но мы используем String
    file_size = Column(BigInteger, nullable=False)  # bigint
    media_type = Column(String(20), nullable=False)  # character
    mime_type = Column(String(100), nullable=False)  # character
    
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    duration = Column(Integer, nullable=True)  # в секундах
    
    has_thumbnail = Column(Boolean, nullable=True, default=False)
    has_medium = Column(Boolean, nullable=True, default=False)
    
    is_public = Column(Boolean, nullable=False, default=False)
    sort_order = Column(Integer, nullable=True)
    
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
    
    is_temp = Column(Boolean, nullable=False, default=False)
    
    # Relationships
    page = relationship("PageBD", backref="media")
    
    def to_dict(self):
        """Преобразует объект в словарь"""
        return {
            'id_media': str(self.id_media),
            'user_id': str(self.user_id),
            'page_id': str(self.page_id),
            'file_extension': self.file_extension,
            'file_size': self.file_size,
            'media_type': self.media_type,
            'mime_type': self.mime_type,
            'width': self.width,
            'height': self.height,
            'duration': self.duration,
            'has_thumbnail': self.has_thumbnail,
            'has_medium': self.has_medium,
            'is_public': self.is_public,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_temp': self.is_temp,
        }