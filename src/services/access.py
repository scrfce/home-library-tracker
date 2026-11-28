"""Общая проверка прав доступа к книгам (NFR-04)."""

from src.models import Book
from src.models.repositories import BookRepository
from src.utils.errors import AccessDeniedError, NotFoundError


def get_owned_book(books: BookRepository, owner_id: int, book_id: int) -> Book:
    """Находит книгу и проверяет, что она принадлежит указанному Владельцу.

    Raises:
        NotFoundError: Книга не найдена.
        AccessDeniedError: Книга принадлежит другой библиотеке.
    """
    book = books.get(book_id)
    if book is None:
        raise NotFoundError("Книга не найдена.")
    if book.owner_id != owner_id:
        raise AccessDeniedError("Эта книга принадлежит другой библиотеке.")
    return book
