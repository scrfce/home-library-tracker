"""Проверка модуля «Выдача и возврат» (FR-10–FR-13)."""

from datetime import date, timedelta

import pytest

from src.models import BookStatus
from src.utils.errors import (
    AccessDeniedError,
    BusinessRuleError,
    NotFoundError,
    ValidationError,
)

TODAY = date(2026, 11, 26)


def issue(loans, owner, book, **kwargs):
    params = {
        "borrower_name": "Иван Петров",
        "due_date": TODAY + timedelta(days=14),
        "issue_date": TODAY,
    }
    params.update(kwargs)
    return loans.issue_book(owner.id, book.id, **params)


def test_issue_book_changes_status_and_creates_loan(loans, owner, book):
    loan = issue(loans, owner, book, borrower_contact="+7 900 000-00-00")
    assert loan.id is not None
    assert loan.borrower.name == "Иван Петров"
    assert loan.is_open()
    assert book.status is BookStatus.ON_LOAN


def test_cannot_issue_book_twice(loans, owner, book):
    issue(loans, owner, book)
    with pytest.raises(BusinessRuleError):
        issue(loans, owner, book, borrower_name="Другой человек")


def test_issue_requires_borrower_name(loans, owner, book):
    with pytest.raises(ValidationError):
        issue(loans, owner, book, borrower_name="  ")
    assert book.status is BookStatus.AVAILABLE


def test_issue_due_date_before_issue_date(loans, owner, book):
    with pytest.raises(ValidationError):
        issue(loans, owner, book, due_date=TODAY - timedelta(days=1))
    assert book.status is BookStatus.AVAILABLE


def test_issue_due_date_too_far(loans, owner, book):
    with pytest.raises(ValidationError):
        issue(loans, owner, book, due_date=TODAY + timedelta(days=400))


def test_issue_missing_book(loans, owner):
    with pytest.raises(NotFoundError):
        loans.issue_book(owner.id, 999, "Иван", TODAY + timedelta(days=3))


def test_other_owner_cannot_issue_foreign_book(loans, other_owner, book):
    with pytest.raises(AccessDeniedError):
        loans.issue_book(other_owner.id, book.id, "Иван", date.today() + timedelta(days=3))


def test_return_book_makes_it_available(loans, owner, book):
    loan = issue(loans, owner, book)
    closed = loans.return_book(
        owner.id, loan.id, return_date=TODAY + timedelta(days=10), note="Без повреждений"
    )
    assert closed.return_date == TODAY + timedelta(days=10)
    assert closed.note == "Без повреждений"
    assert book.status is BookStatus.AVAILABLE
    assert closed.days_overdue(TODAY + timedelta(days=30)) == 0


def test_return_late_counts_overdue_days(loans, owner, book):
    loan = issue(loans, owner, book)
    closed = loans.return_book(owner.id, loan.id, return_date=TODAY + timedelta(days=17))
    assert closed.days_overdue(TODAY + timedelta(days=40)) == 3


def test_cannot_return_twice(loans, owner, book):
    loan = issue(loans, owner, book)
    loans.return_book(owner.id, loan.id, return_date=TODAY + timedelta(days=1))
    with pytest.raises(BusinessRuleError):
        loans.return_book(owner.id, loan.id, return_date=TODAY + timedelta(days=2))


def test_return_date_before_issue_date(loans, owner, book):
    loan = issue(loans, owner, book)
    with pytest.raises(ValidationError):
        loans.return_book(owner.id, loan.id, return_date=TODAY - timedelta(days=1))
    assert loan.is_open()


def test_return_unknown_loan(loans, owner):
    with pytest.raises(NotFoundError):
        loans.return_book(owner.id, 999)


def test_other_owner_cannot_return_foreign_loan(loans, owner, other_owner, book):
    loan = issue(loans, owner, book)
    with pytest.raises(AccessDeniedError):
        loans.return_book(other_owner.id, loan.id)


def test_list_active_and_overdue(loans, catalog, owner, book):
    second = catalog.add_book(owner.id, "Идиот", "Фёдор Достоевский")
    issue(loans, owner, book, due_date=TODAY + timedelta(days=5))
    issue(loans, owner, second, due_date=TODAY + timedelta(days=1))
    active = loans.list_active_loans(owner.id)
    assert [item.book.title for item in active] == ["Идиот", "Мастер и Маргарита"]
    overdue = loans.list_overdue_loans(owner.id, today=TODAY + timedelta(days=3))
    assert [item.book.title for item in overdue] == ["Идиот"]


def test_returned_loans_leave_active_list(loans, owner, book):
    loan = issue(loans, owner, book)
    loans.return_book(owner.id, loan.id, return_date=TODAY + timedelta(days=2))
    assert loans.list_active_loans(owner.id) == []


def test_history_shows_all_loans_newest_first(loans, owner, book):
    first = issue(loans, owner, book, borrower_name="Первый")
    loans.return_book(owner.id, first.id, return_date=TODAY + timedelta(days=2))
    issue(loans, owner, book, borrower_name="Второй")
    history = loans.get_book_history(owner.id, book.id)
    assert [item.borrower.name for item in history] == ["Второй", "Первый"]


def test_history_of_foreign_book_is_denied(loans, other_owner, book):
    with pytest.raises(AccessDeniedError):
        loans.get_book_history(other_owner.id, book.id)
