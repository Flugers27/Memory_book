"""
SQLAlchemy модели для контроля доступа к страницам
"""
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from database.base import Base


class PageAccessControl(Base):
    __tablename__ = "page_access_control"
    __table_args__ = {'extend_existing': True}

    id_access = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    page_id = Column(UUID(as_uuid=True), ForeignKey('pages.id_page'), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id_user'), nullable=False, index=True)
    can_view = Column(Boolean, default=False)
    can_edit = Column(Boolean, default=False)
    granted_by = Column(UUID(as_uuid=True), ForeignKey('users.id_user'), nullable=True)
    granted_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    taget_type = Column(String(50), nullable=True)

    # Relationships
    page = relationship("PageBD", foreign_keys=[page_id], backref="access")
    user = relationship("User", foreign_keys=[user_id], backref="access_granted")
    grantor = relationship("User", foreign_keys=[granted_by], backref="access_granted_by")

    def to_dict(self):
        """Преобразует объект в словарь"""
        return {
            'id_access': str(self.id_access),
            'page_id': str(self.page_id),
            'user_id': str(self.user_id),
            'can_view': self.can_view,
            'can_edit': self.can_edit,
            'granted_by': str(self.granted_by) if self.granted_by else None,
            'granted_at': self.granted_at.isoformat() if self.granted_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'taget_type': self.taget_type,
        }