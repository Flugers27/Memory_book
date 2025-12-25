"""
SQLAlchemy модели для сервиса памяти (упрощенная версия)
"""
from sqlalchemy import Column, String, Date, Text, Boolean, DateTime, JSON,ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
import json
from datetime import datetime as dt

from database.base import Base

class PageAccessControl(Base):
    __tablename__ = "page_access_control"
    __table_args__ = {'extend_existing': True}

    id_access = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    page_id = Column(UUID(as_uuid=True), ForeignKey('memory_page.id_page'), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('auth_user.id_user'), nullable=False, index=True)
    can_view = Column(Boolean, default=False, nullable=False)
    can_edit = Column(Boolean, default=False, nullable=False)
    granted_by = Column(UUID(as_uuid=True), ForeignKey('auth_user.id_user'), nullable=True)
    granted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    page = relationship("MemoryPage", foreign_keys=[page_id])
    user = relationship("AuthUser", foreign_keys=[user_id])
    grantor = relationship("AuthUser", foreign_keys=[granted_by])

    def to_dict(self):
        """Преобразует объект в словарь"""
        return {
            'id_access': str(self.id_access),
            'page_id': str(self.page_id),
            'user_id': str(self.user_id),
            'can_view': self.can_view,
            'can_edit': self.can_edit,
            'granted_by': str(self.granted_by),
            'granted_at': self.granted_at.isoformat() if self.granted_at else None,
            'expires_at': self.expires_at.isoformat(),
            'is_active' : self.is_active
        }