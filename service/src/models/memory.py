from sqlalchemy import Column, String, Boolean, DateTime, text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

from src.models.base import Base

class MemoryAgent(Base):
    """Модель memory_agent (умершие люди)"""
    __tablename__ = "memory_agent"
    __table_args__ = {"schema": "public"}
    
    id_agent = Column(
        "id_agent",
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )
    full_name = Column(String(255), nullable=False)
    birth_date = Column(DateTime)
    death_date = Column(DateTime)
    avatar_url = Column(String)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("public.users.id_user"),
        nullable=False
    )
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), server_default=text("now()"))

class MemoryPage(Base):
    """Модель memory_page (страницы памяти)"""
    __tablename__ = "memory_page"
    __table_args__ = {"schema": "public"}
    
    id_page = Column(
        "id_page",
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )
    epitaph = Column(String)
    place_of_birth = Column(String(500))
    place_of_death = Column(String(500))
    is_public = Column(Boolean, default=False, nullable=False)
    is_draft = Column(Boolean, default=False, nullable=False)
    memory_agent_id = Column(
        UUID(as_uuid=True),
        ForeignKey("public.memory_agent.id_agent"),
        nullable=False
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("public.users.id_user"),
        nullable=False
    )
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), server_default=text("now()"))

class MemoryTitles(Base):
    """Модель memory_titles (заголовки на страницах)"""
    __tablename__ = "memory_titles"
    __table_args__ = {"schema": "public"}
    
    id_titles = Column(
        "id_titles",
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )
    head = Column(String(100), nullable=False)
    body = Column(String)
    page_id = Column(
        UUID(as_uuid=True),
        ForeignKey("public.memory_page.id_page"),
        nullable=False
    )
    expires_at = Column(DateTime(timezone=True), server_default=text("now()"))
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))