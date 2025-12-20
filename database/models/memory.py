"""
Модели для сервиса памяти.
"""
from sqlalchemy import Column, String, Date, Text, Boolean, ForeignKey, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..base import BaseModel

class MemoryAgent(BaseModel):
    __tablename__ = "memory_agent"
    
    id_agent = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    full_name = Column(String(255), nullable=False)
    gender = Column(String(1), nullable=False)  # Добавляем gender
    birth_date = Column(Date)
    death_date = Column(Date)
    place_of_birth = Column(String(100))
    place_of_death = Column(String(100))
    avatar_url = Column(Text)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    is_human = Column(Boolean, default=True)
    
    # Relationships
    pages = relationship("MemoryPage", back_populates="agent", cascade="all, delete-orphan")

class MemoryPage(BaseModel):
    __tablename__ = "memory_page"
    
    id_page = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    epitaph = Column(Text)
    is_public = Column(Boolean, default=False, nullable=False)
    is_draft = Column(Boolean, default=True, nullable=False)
    memory_agent_id = Column(UUID(as_uuid=True), ForeignKey('memory_agent.id_agent'), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    biography = Column(JSON)
    is_human = Column(Boolean, default=True)
    
    # Relationships
    agent = relationship("MemoryAgent", back_populates="pages")
    titles = relationship("MemoryTitles", back_populates="page", cascade="all, delete-orphan")

class MemoryTitles(BaseModel):
    __tablename__ = "memory_titles"
    
    id_titles = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    head = Column(String(100), nullable=False)
    body = Column(Text)
    page_id = Column(UUID(as_uuid=True), ForeignKey('memory_page.id_page'), nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), server_default=func.now())
    sort_order = Column(Integer, default=0)
    parent_id = Column(UUID(as_uuid=True), ForeignKey('memory_titles.id_titles'))
    
    # Relationships
    page = relationship("MemoryPage", back_populates="titles")
    parent = relationship("MemoryTitles", remote_side=[id_titles], backref="children")