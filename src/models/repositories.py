"""Репозитории: единственное место, где выполняются запросы к базе данных.

Сервисы работают с данными только через эти классы (интерфейс IRepository
на диаграмме компонентов).
"""

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from src.models.book import Book, BookStatus
from src.models.loan import Borrower, Loan
from src.models.user import User


class UserRepository:
    """Доступ к пользователям."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, user: User) -> User:
        self._session.add(user)
        self._session.flush()
        return user

    def get(self, user_id: int) -> User | None:
        return self._session.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        return self._session.scalar(select(User).where(User.email == email))


class BookRepository:
    """Доступ к книгам."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, book: Book) -> Book:
        self._session.add(book)
        self._session.flush()
        return book

    def get(self, book_id: int) -> Book | None:
        return self._session.get(Book, book_id)

    def delete(self, book: Book) -> None:
        self._session.delete(book)

    def search(
        self,
        owner_id: int,
        query: str | None = None,
        genre: str | None = None,
        status: BookStatus | None = None,
    ) -> list[Book]:
        """Ищет книги Владельца по названию или автору и фильтрует по жанру и статусу."""
        stmt = select(Book).where(Book.owner_id == owner_id)
        if query:
            pattern = f"%{query.lower()}%"
            stmt = stmt.where(
                or_(_lower_like(Book.title, pattern), _lower_like(Book.author, pattern))
            )
        if genre:
            stmt = stmt.where(_lower_like(Book.genre, f"%{genre.lower()}%"))
        if status is not None:
            stmt = stmt.where(Book.status == status)
        return list(self._session.scalars(stmt.order_by(Book.title, Book.id)))


class LoanRepository:
    """Доступ к выдачам и получателям."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add_borrower(self, borrower: Borrower) -> Borrower:
        self._session.add(borrower)
        self._session.flush()
        return borrower

    def add(self, loan: Loan) -> Loan:
        self._session.add(loan)
        self._session.flush()
        return loan

    def get(self, loan_id: int) -> Loan | None:
        return self._session.get(Loan, loan_id)

    def list_open(self, owner_id: int) -> list[Loan]:
        """Невозвращённые выдачи книг Владельца, ближайший срок возврата первым."""
        stmt = (
            select(Loan)
            .join(Book, Loan.book_id == Book.id)
            .where(Book.owner_id == owner_id, Loan.return_date.is_(None))
            .order_by(Loan.due_date, Loan.id)
        )
        return list(self._session.scalars(stmt))

    def list_by_book(self, book_id: int) -> list[Loan]:
        """Вся история выдач книги, новые записи первыми."""
        stmt = select(Loan).where(Loan.book_id == book_id).order_by(Loan.id.desc())
        return list(self._session.scalars(stmt))


def _lower_like(column, pattern: str):
    """Регистронезависимое сравнение (lower() подменён в database.py на Unicode-версию)."""
    return func.lower(column).like(pattern)
