"""Проверка функций проверки входных данных."""

from datetime import date

import pytest

from src.utils.errors import ValidationError
from src.utils.validation import (
    require_text,
    validate_email,
    validate_isbn,
    validate_loan_dates,
    validate_password,
    validate_year,
)


def test_require_text_strips_spaces():
    assert require_text("  Война и мир  ", "название", 50) == "Война и мир"


@pytest.mark.parametrize("value", ["", "   ", None])
def test_require_text_rejects_empty_required(value):
    with pytest.raises(ValidationError):
        require_text(value, "название", 50)


def test_require_text_optional_empty_returns_none():
    assert require_text("  ", "жанр", 50, required=False) is None


def test_require_text_rejects_too_long():
    with pytest.raises(ValidationError):
        require_text("а" * 51, "название", 50)


def test_require_text_rejects_non_string():
    with pytest.raises(ValidationError):
        require_text(123, "название", 50)


def test_validate_email_normalizes_case():
    assert validate_email("  User@Example.COM ") == "user@example.com"


@pytest.mark.parametrize(
    "email", ["user", "user@", "@example.com", "user@example", "a b@example.com"]
)
def test_validate_email_rejects_bad_format(email):
    with pytest.raises(ValidationError):
        validate_email(email)


def test_validate_password_too_short():
    with pytest.raises(ValidationError):
        validate_password("short")


def test_validate_password_ok():
    assert validate_password("long-enough-1") == "long-enough-1"


@pytest.mark.parametrize("year", [999, 3000, "1999", True, 19.5])
def test_validate_year_rejects_bad_values(year):
    with pytest.raises(ValidationError):
        validate_year(year)


def test_validate_year_accepts_none_and_valid():
    assert validate_year(None) is None
    assert validate_year(1967) == 1967


def test_validate_isbn_accepts_hyphens():
    assert validate_isbn("978-5-17-090353-0") == "978-5-17-090353-0"
    assert validate_isbn(None) is None


@pytest.mark.parametrize("isbn", ["12345", "abcdefghij", "978-5-17-09035"])
def test_validate_isbn_rejects_bad_values(isbn):
    with pytest.raises(ValidationError):
        validate_isbn(isbn)


def test_validate_loan_dates_ok():
    assert validate_loan_dates(date(2026, 11, 1), date(2026, 11, 15)) == (
        date(2026, 11, 1),
        date(2026, 11, 15),
    )


def test_validate_loan_dates_due_before_issue():
    with pytest.raises(ValidationError):
        validate_loan_dates(date(2026, 11, 10), date(2026, 11, 9))


def test_validate_loan_dates_too_long():
    with pytest.raises(ValidationError):
        validate_loan_dates(date(2026, 1, 1), date(2027, 1, 1))
