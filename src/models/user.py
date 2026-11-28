"""Модель пользователя (классы User, Owner, Reader диаграммы классов)."""

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class Role(enum.Enum):
    """Роль пользователя в системе."""

    OWNER = "owner"
    READER = "reader"


class User(Base):
    """Учётная запись Владельца или Читателя."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.OWNER)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    def is_owner(self) -> bool:
        """Возвращает True, если пользователь — Владелец библиотеки."""
        return self.role is Role.OWNER
