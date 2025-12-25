"""
Модели SQLAlchemy для сервиса авторизации
"""
import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from database.base import Base

class UserRole(Base):
    __tablename__ = "user_roles"

    id_role = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_name = Column(String(50), unique=True, nullable=False)
    role_description = Column(Text, nullable=True)
    permissions = Column(JSON, nullable=False, default={"edit_own": True, "create_page": True, "view_public": True})
    is_system = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class User(Base):
    __tablename__ = "users"
    
    id_user = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True)
    full_name = Column(String)

    password_hash = Column(String, nullable=False)

    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey("user_roles.id_role"), nullable=False)
    last_login_at = Column(DateTime)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def to_dict(self):
        """Конвертирует объект в словарь"""
        return {
            'id_user': str(self.id_user),
            'email': self.email,
            'username': self.username,
            'full_name': self.full_name,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'role_id': self.role_id
            # 'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
            # 'created_at': self.created_at.isoformat(),
            # 'updated_at': self.updated_at.isoformat()
        }

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    __table_args__ = {'schema': 'sys'}
    
    id_user_token = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    token_hash = Column(String(512), nullable=False)
    device_info = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def to_dict(self):
        """Конвертирует объект в словарь"""
        return {
            'id_user_token': str(self.id_user_token),
            'user_id': str(self.user_id),
            'device_info': self.device_info,
            'ip_address': str(self.ip_address) if self.ip_address else None,
            'expires_at': self.expires_at.isoformat(),
            'created_at': self.created_at.isoformat()
        }
    
class EmailVerificationToken(Base):
    __tablename__ = "email_verification_tokens"

    id_token = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    token = Column(String, nullable=False, unique=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())