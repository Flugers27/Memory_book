"""
SQLAlchemy модели для семейного древа
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from database.base import Base

# Импортируем все связанные модели для регистрации в реестре SQLAlchemy,
# чтобы ForeignKey и relationship могли найти целевые таблицы и классы
from database.models.memory import AgentBD
from database.models.auth import User


class FamilyTree(Base):
    __tablename__ = "family_tree"
    __table_args__ = {'extend_existing': True}

    id_family_tree = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name_family_tree = Column(String(255), nullable=False)
    is_public = Column(Boolean, nullable=False, default=False)
    is_draft = Column(Boolean, nullable=False, default=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id_user'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    agents = relationship("FamilyTreeAgent", back_populates="family_tree", cascade="all, delete-orphan")
    relationships = relationship("RelationshipAgent", back_populates="family_tree", cascade="all, delete-orphan")

    def to_dict(self):
        """Преобразует объект в словарь"""
        return {
            'id_family_tree': str(self.id_family_tree),
            'name_family_tree': self.name_family_tree,
            'is_public': self.is_public,
            'is_draft': self.is_draft,
            'user_id': str(self.user_id),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class FamilyTreeAgent(Base):
    __tablename__ = "family_tree_agents"
    __table_args__ = {'extend_existing': True}

    id_tree_agent = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_tree_id = Column(UUID(as_uuid=True), ForeignKey('family_tree.id_family_tree'), nullable=False)
    agent_id = Column(UUID(as_uuid=True), ForeignKey('agents.id_agent'), nullable=False)

    # Relationships
    family_tree = relationship("FamilyTree", back_populates="agents")
    agent = relationship("AgentBD", backref="family_tree_agents")

    def to_dict(self):
        """Преобразует объект в словарь"""
        return {
            'id_tree_agent': str(self.id_tree_agent),
            'family_tree_id': str(self.family_tree_id),
            'agent_id': str(self.agent_id),
        }


class RelationshipAgent(Base):
    __tablename__ = "relationships_agents"
    __table_args__ = {'extend_existing': True}

    id_relationships = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type_relative = Column(String(50), nullable=False)
    is_blood_relative = Column(Boolean, nullable=False, default=False)
    agent_from = Column(UUID(as_uuid=True), ForeignKey('agents.id_agent'), nullable=False)
    agent_to = Column(UUID(as_uuid=True), ForeignKey('agents.id_agent'), nullable=False)
    family_tree_id = Column(UUID(as_uuid=True), ForeignKey('family_tree.id_family_tree'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id_user'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    family_tree = relationship("FamilyTree", back_populates="relationships")
    agent_from_rel = relationship("AgentBD", foreign_keys=[agent_from], backref="relationships_from")
    agent_to_rel = relationship("AgentBD", foreign_keys=[agent_to], backref="relationships_to")

    def to_dict(self):
        """Преобразует объект в словарь"""
        return {
            'id_relationships': str(self.id_relationships),
            'type_relative': self.type_relative,
            'is_blood_relative': self.is_blood_relative,
            'agent_from': str(self.agent_from),
            'agent_to': str(self.agent_to),
            'family_tree_id': str(self.family_tree_id),
            'user_id': str(self.user_id),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }