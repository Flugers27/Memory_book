from sqlalchemy import Column, String, DateTime, ForeignKey, text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, INET

from src.models.base import Base

class RefreshToken(Base):
    """Модель refresh токена (соответствует вашей таблице sys.refresh_tokens)"""
    __tablename__ = "refresh_tokens"
    __table_args__ = (
        {"schema": "sys"},
        UniqueConstraint('user_id', 'device_info', name='refresh_tokens_user_id_device_info_key')
    )
    
    id_user_token = Column(
        "id_user_token",
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )
    user_id = Column(
        "user_id",  # Явно указываем имя столбца
        UUID(as_uuid=True),
        ForeignKey("public.users.id_user", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    token_hash = Column(String(512), nullable=False, index=True)
    device_info = Column(String)
    ip_address = Column(INET)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))