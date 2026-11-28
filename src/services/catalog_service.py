"""Модуль «Каталог»: ведение каталога книг и поиск (FR-04–FR-09)."""

from sqlalchemy.orm import Session

from config import settings
from src.models import Book, BookStatus
from src.models.repositories import BookRepository, UserRepository
from src.services.access import get_owned_book
from src.utils.errors import AccessDeniedError, BusinessRuleError, ValidationError
from src.utils.validation import require_text, validate_isbn, validate_year

_EDITABLE_FIELDS = {"title", "author", "genre", "year", "isbn", "location", "condition"}


class CatalogService:
    """Добавление, изменение, удаление и поиск книг Владельца."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self._books = BookRepository(session)
        self._users = UserRepository(session)

    def add_book(
        self,
        owner_id: int,
        title: str,
        author: str,
        genre: str | None = None,
        year: int | None = None,
        isbn: str | None = None,
        location: str | None = None,
        condition: str | None = None,
    ) -> Book:
        """Добавляет книгу со статусом «в наличии» (FR-04).

        Raises:
            AccessDeniedError: Пользователь не найден или не является Владельцем.
            ValidationError: Название или автор не заполнены, поля некорректны.
        """
        owner = self._users.get(owner_id)
        if owner is None or not owner.is_owner():
            raise AccessDeniedError("Добавлять книги может только Владелец библиотеки.")

        book = Book(
            owner_id=owner_id,
            title=require_text(title, "название", settings.MAX_TEXT_LENGTH),
            author=require_text(author, "автор", settings.MAX_TEXT_LENGTH),
            genre=require_text(genre, "жанр", settings.MAX_TEXT_LENGTH, required=False),
            year=validate_year(year),
            isbn=validate_isbn(isbn),
            location=require_text(
                location, "место хранения", settings.MAX_TEXT_LENGTH, required=False
            ),
            condition=require_text(
                condition, "состояние", settings.MAX_TEXT_LENGTH, required=False
            ),
            status=BookStatus.AVAILABLE,
        )
        self._books.add(book)
        self._session.commit()
        return book

    def update_book(self, owner_id: int, book_id: int, **changes: object) -> Book:
        """Изменяет сведения о книге (FR-05).

        Args:
            owner_id: Идентификатор Владельца.
            book_id: Идентификатор книги.
            **changes: Изменяемые поля: title, author, genre, year, isbn, location, condition.

        Raises:
            ValidationError: Указано неизвестное поле или значение некорректно.
            NotFoundError: Книга не найдена.
            AccessDeniedError: Книга принадлежит другому Владельцу.
        """
        unknown = set(changes) - _EDITABLE_FIELDS
        if unknown:
            raise ValidationError(f"Нельзя изменить поля: {', '.join(sorted(unknown))}.")

        book = get_owned_book(self._books, owner_id, book_id)
        for field, value in changes.items():
            setattr(book, field, self._clean_field(field, value))
        self._session.commit()
        return book

    def delete_book(self, owner_id: int, book_id: int) -> None:
        """Удаляет книгу вместе с историей выдач (FR-06).

        Raises:
            BusinessRuleError: Книга выдана, удалять её нельзя.
        """
        book = get_owned_book(self._books, owner_id, book_id)
        if not book.is_available():
            raise BusinessRuleError("Нельзя удалить книгу, которая сейчас выдана.")
        self._books.delete(book)
        self._session.commit()

    def get_book(self, owner_id: int, book_id: int) -> Book:
        """Возвращает карточку книги (FR-09)."""
        return get_owned_book(self._books, owner_id, book_id)

    def search_books(
        self,
        owner_id: int,
        query: str | None = None,
        genre: str | None = None,
        status: BookStatus | None = None,
    ) -> list[Book]:
        """Возвращает список книг, при необходимости отфильтрованный (FR-07, FR-08).

        Без параметров возвращает весь каталог Владельца.
        """
        clean_query = require_text(query, "запрос", settings.MAX_TEXT_LENGTH, required=False)
        clean_genre = require_text(genre, "жанр", settings.MAX_TEXT_LENGTH, required=False)
        if status is not None and not isinstance(status, BookStatus):
            raise ValidationError("Неизвестный статус книги.", "status")
        return self._books.search(owner_id, clean_query, clean_genre, status)

    # --- внутренние методы ---

    @staticmethod
    def _clean_field(field: str, value: object) -> object:
        """Проверяет значение одного изменяемого поля."""
        if field in ("title", "author"):
            return require_text(value, field, settings.MAX_TEXT_LENGTH)
        if field == "year":
            return validate_year(value)
        if field == "isbn":
            return validate_isbn(value)
        return require_text(value, field, settings.MAX_TEXT_LENGTH, required=False)
