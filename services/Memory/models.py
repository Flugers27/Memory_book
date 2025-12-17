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

from .config import Base

class AgentBD(Base):
    __tablename__ = "memory_agent"
    __table_args__ = {'extend_existing': True}
    
    id_agent = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    full_name = Column(String(255), nullable=False)
    gender = Column(String(1), nullable=False)
    birth_date = Column(Date, nullable=True)
    death_date = Column(Date, nullable=True)
    place_of_birth = Column(String(500), nullable=True)
    place_of_death = Column(String(500), nullable=True)
    avatar_url = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    user_id = Column(String(36), nullable=False)

    # Добавляем relationship
    pages = relationship("PageBD", back_populates="agent", cascade="all, delete-orphan")

    def to_dict(self):
        """Преобразует объект в словарь"""
        return {
            'id_agent': str(self.id_agent),
            'full_name': self.full_name,
            'gender': self.gender,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'death_date': self.death_date.isoformat() if self.death_date else None,
            'place_of_birth' : self.place_of_birth,
            'place_of_death' : self.place_of_death,
            'avatar_url': self.avatar_url,
            'user_id': str(self.user_id)
        }

    

class PageBD(Base):
    __tablename__ = "memory_page"
    __table_args__ = {'extend_existing': True}
    
    id_page = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    epitaph = Column(Text, nullable=True)
    is_public = Column(Boolean, nullable=False, default=False)
    is_draft = Column(Boolean, nullable=False, default=False)
    memory_agent_id = Column(String(36), ForeignKey('memory_agent.id_agent'), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    user_id = Column(String(36), nullable=False)
    biography = Column(JSON, nullable=True)

    # Добавляем relationship
    agent = relationship("AgentBD", back_populates="pages")
    
    def to_dict(self):
        """Преобразует объект в словарь"""

        return {
            'id_page': self.id_page,
            'epitaph': self.epitaph,
            'is_public': self.is_public,
            'is_draft': self.is_draft,
            'memory_agent_id': self.memory_agent_id,
            'user_id': self.user_id,
            'biography': self.biography,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }