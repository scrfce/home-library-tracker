"""Модель книги (класс Book диаграммы классов)."""

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class BookStatus(enum.Enum):
    """Статус книги: в наличии или выдана."""

    AVAILABLE = "available"
    ON_LOAN = "on_loan"


class Book(Base):
    """Книга в каталоге Владельца."""

    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    author: Mapped[str] = mapped_column(String(200))
    genre: Mapped[str | None] = mapped_column(String(200))
    year: Mapped[int | None] = mapped_column(Integer)
    isbn: Mapped[str | None] = mapped_column(String(20))
    location: Mapped[str | None] = mapped_column(String(200))
    condition: Mapped[str | None] = mapped_column(String(200))
    status: Mapped[BookStatus] = mapped_column(Enum(BookStatus), default=BookStatus.AVAILABLE)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # История выдач удаляется вместе с книгой.
    loans: Mapped[list["Loan"]] = relationship(  # noqa: F821
        back_populates="book", cascade="all, delete-orphan", order_by="Loan.id"
    )

    def is_available(self) -> bool:
        """Возвращает True, если книгу можно выдать."""
        return self.status is BookStatus.AVAILABLE

    def change_status(self, status: BookStatus) -> None:
        """Меняет статус книги."""
        self.status = status
