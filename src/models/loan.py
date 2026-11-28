"""Модели выдачи книги (классы Loan и Borrower диаграммы классов)."""

from datetime import date

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.models.book import Book


class Borrower(Base):
    """Получатель книги: читатель библиотеки или человек без учётной записи (FR-10)."""

    __tablename__ = "borrowers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    contact: Mapped[str | None] = mapped_column(String(200))
    reader_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))


class Loan(Base):
    """Запись о выдаче книги."""

    __tablename__ = "loans"

    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), index=True)
    borrower_id: Mapped[int] = mapped_column(ForeignKey("borrowers.id"))
    issue_date: Mapped[date] = mapped_column(Date)
    due_date: Mapped[date] = mapped_column(Date)
    return_date: Mapped[date | None] = mapped_column(Date)
    note: Mapped[str | None] = mapped_column(String(500))

    book: Mapped[Book] = relationship(back_populates="loans")
    borrower: Mapped[Borrower] = relationship()

    def is_open(self) -> bool:
        """Возвращает True, если книга ещё не возвращена."""
        return self.return_date is None

    def is_overdue(self, today: date) -> bool:
        """Возвращает True, если книга не возвращена и срок возврата истёк."""
        return self.is_open() and today > self.due_date

    def days_overdue(self, today: date) -> int:
        """Число дней просрочки на дату ``today`` (для возвращённой выдачи — на дату возврата)."""
        end = self.return_date or today
        return max((end - self.due_date).days, 0)

    def close(self, return_date: date) -> None:
        """Закрывает выдачу, фиксируя дату возврата."""
        self.return_date = return_date
