"""Модуль «Выдача и возврат»: учёт выдачи книг (FR-10–FR-13)."""

from datetime import date

from sqlalchemy.orm import Session

from config import settings
from src.models import BookStatus, Borrower, Loan
from src.models.repositories import BookRepository, LoanRepository
from src.services.access import get_owned_book
from src.utils.errors import BusinessRuleError, NotFoundError, ValidationError
from src.utils.validation import require_text, validate_loan_dates


class LoanService:
    """Оформление выдачи и возврата, списки «на руках» и история."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self._books = BookRepository(session)
        self._loans = LoanRepository(session)

    def issue_book(
        self,
        owner_id: int,
        book_id: int,
        borrower_name: str,
        due_date: date,
        borrower_contact: str | None = None,
        issue_date: date | None = None,
        reader_id: int | None = None,
    ) -> Loan:
        """Выдаёт книгу получателю (FR-10).

        Args:
            owner_id: Идентификатор Владельца.
            book_id: Идентификатор книги.
            borrower_name: Имя получателя.
            due_date: Срок возврата.
            borrower_contact: Контакт получателя (необязательно).
            issue_date: Дата выдачи, по умолчанию сегодня.
            reader_id: Идентификатор Читателя, если получатель — читатель библиотеки.

        Returns:
            Созданная запись о выдаче.

        Raises:
            ValidationError: Не указан получатель или некорректны даты.
            NotFoundError: Книга не найдена.
            AccessDeniedError: Книга принадлежит другому Владельцу.
            BusinessRuleError: Книга уже выдана.
        """
        name = require_text(borrower_name, "получатель", settings.MAX_NAME_LENGTH)
        contact = require_text(
            borrower_contact, "контакт", settings.MAX_TEXT_LENGTH, required=False
        )
        start, end = validate_loan_dates(issue_date or date.today(), due_date)

        book = get_owned_book(self._books, owner_id, book_id)
        if not book.is_available():
            raise BusinessRuleError("Книга уже выдана.")

        borrower = self._loans.add_borrower(
            Borrower(name=name, contact=contact, reader_id=reader_id)
        )
        loan = self._loans.add(
            Loan(book_id=book.id, borrower_id=borrower.id, issue_date=start, due_date=end)
        )
        book.change_status(BookStatus.ON_LOAN)
        self._session.commit()
        return loan

    def return_book(
        self,
        owner_id: int,
        loan_id: int,
        return_date: date | None = None,
        note: str | None = None,
    ) -> Loan:
        """Принимает возврат книги (FR-11).

        Raises:
            NotFoundError: Выдача не найдена.
            AccessDeniedError: Выдача относится к чужой библиотеке.
            BusinessRuleError: Книга уже возвращена.
            ValidationError: Дата возврата раньше даты выдачи или заметка слишком длинная.
        """
        loan = self._loans.get(loan_id)
        if loan is None:
            raise NotFoundError("Выдача не найдена.")
        get_owned_book(self._books, owner_id, loan.book_id)
        if not loan.is_open():
            raise BusinessRuleError("Книга уже возвращена.")

        end = return_date or date.today()
        if end < loan.issue_date:
            raise ValidationError("Дата возврата не может быть раньше даты выдачи.", "return_date")
        loan.note = require_text(note, "заметка", settings.MAX_NOTE_LENGTH, required=False)

        loan.close(end)
        loan.book.change_status(BookStatus.AVAILABLE)
        self._session.commit()
        return loan

    def list_active_loans(self, owner_id: int) -> list[Loan]:
        """Возвращает книги «на руках» (FR-12), ближайший срок возврата первым."""
        return self._loans.list_open(owner_id)

    def list_overdue_loans(self, owner_id: int, today: date | None = None) -> list[Loan]:
        """Возвращает выдачи с истёкшим сроком возврата (FR-12)."""
        current = today or date.today()
        return [loan for loan in self._loans.list_open(owner_id) if loan.is_overdue(current)]

    def get_book_history(self, owner_id: int, book_id: int) -> list[Loan]:
        """Возвращает историю выдач книги (FR-13), новые записи первыми."""
        book = get_owned_book(self._books, owner_id, book_id)
        return self._loans.list_by_book(book.id)
