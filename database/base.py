"""
Базовый класс для всех моделей SQLAlchemy (SQLAlchemy 2.x).
"""
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime
from sqlalchemy.sql import func
from datetime import datetime


class Base(DeclarativeBase):
    pass


class BaseModel(Base):
    """
    Абстрактный базовый класс для всех моделей.
    """
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    def to_dict(self) -> dict:
        """
        Безопасная сериализация модели (только колонки).
        """
        return {
            column.name: (
                getattr(self, column.name).isoformat()
                if hasattr(getattr(self, column.name), "isoformat")
                else getattr(self, column.name)
            )
            for column in self.__table__.columns
        }
