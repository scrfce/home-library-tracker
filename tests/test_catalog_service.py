"""Проверка модуля «Каталог» (FR-04–FR-09)."""

import pytest

from src.models import BookStatus
from src.utils.errors import AccessDeniedError, BusinessRuleError, NotFoundError, ValidationError


def test_add_book_sets_available_status(catalog, owner):
    book = catalog.add_book(owner.id, "  Идиот ", "Фёдор Достоевский", genre="Роман", year=1869)
    assert book.id is not None
    assert book.title == "Идиот"
    assert book.status is BookStatus.AVAILABLE


@pytest.mark.parametrize(("title", "author"), [("", "Автор"), ("Название", "  ")])
def test_add_book_requires_title_and_author(catalog, owner, title, author):
    with pytest.raises(ValidationError):
        catalog.add_book(owner.id, title, author)


def test_add_book_rejects_invalid_year(catalog, owner):
    with pytest.raises(ValidationError):
        catalog.add_book(owner.id, "Книга", "Автор", year=1500000)


def test_reader_cannot_add_book(catalog, reader):
    with pytest.raises(AccessDeniedError):
        catalog.add_book(reader.id, "Книга", "Автор")


def test_update_book_changes_fields(catalog, owner, book):
    updated = catalog.update_book(owner.id, book.id, location="Шкаф 2", year=1966)
    assert updated.location == "Шкаф 2"
    assert updated.year == 1966


def test_update_book_rejects_unknown_field(catalog, owner, book):
    with pytest.raises(ValidationError):
        catalog.update_book(owner.id, book.id, status=BookStatus.ON_LOAN)


def test_update_book_rejects_empty_title(catalog, owner, book):
    with pytest.raises(ValidationError):
        catalog.update_book(owner.id, book.id, title="  ")


def test_other_owner_cannot_change_foreign_book(catalog, other_owner, book):
    with pytest.raises(AccessDeniedError):
        catalog.update_book(other_owner.id, book.id, title="Взлом")
    with pytest.raises(AccessDeniedError):
        catalog.delete_book(other_owner.id, book.id)


def test_get_missing_book(catalog, owner):
    with pytest.raises(NotFoundError):
        catalog.get_book(owner.id, 999)


def test_delete_available_book(catalog, owner, book):
    catalog.delete_book(owner.id, book.id)
    assert catalog.search_books(owner.id) == []


def test_delete_book_on_loan_is_forbidden(catalog, loans, owner, book):
    from datetime import date, timedelta

    loans.issue_book(owner.id, book.id, "Иван", date.today() + timedelta(days=7))
    with pytest.raises(BusinessRuleError):
        catalog.delete_book(owner.id, book.id)


def test_search_is_case_insensitive_for_cyrillic(catalog, owner, book):
    catalog.add_book(owner.id, "Собачье сердце", "Михаил Булгаков", genre="Повесть")
    catalog.add_book(owner.id, "Идиот", "Фёдор Достоевский", genre="Роман")
    by_author = catalog.search_books(owner.id, query="булгаков")
    assert [item.title for item in by_author] == ["Мастер и Маргарита", "Собачье сердце"]
    assert [item.title for item in catalog.search_books(owner.id, query="ИДИОТ")] == ["Идиот"]


def test_search_filters_by_genre_and_status(catalog, loans, owner, book):
    from datetime import date, timedelta

    other = catalog.add_book(owner.id, "Идиот", "Фёдор Достоевский", genre="Роман")
    loans.issue_book(owner.id, other.id, "Иван", date.today() + timedelta(days=7))
    assert len(catalog.search_books(owner.id, genre="роман")) == 2
    on_loan = catalog.search_books(owner.id, status=BookStatus.ON_LOAN)
    assert [item.title for item in on_loan] == ["Идиот"]
    assert [item.title for item in catalog.search_books(owner.id, status=BookStatus.AVAILABLE)] == [
        "Мастер и Маргарита"
    ]


def test_search_does_not_show_foreign_books(catalog, other_owner, book):
    assert catalog.search_books(other_owner.id) == []


def test_search_rejects_wrong_status_type(catalog, owner):
    with pytest.raises(ValidationError):
        catalog.search_books(owner.id, status="on_loan")
