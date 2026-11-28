"""Общие фикстуры тестов: база данных в памяти и готовые сервисы."""

import pytest

from config import settings
from src.database import create_session_factory
from src.models import Role
from src.services.auth_service import AuthService
from src.services.catalog_service import CatalogService
from src.services.loan_service import LoanService


@pytest.fixture(autouse=True)
def fast_password_hash(monkeypatch):
    """Уменьшает число итераций хэширования, чтобы тесты работали быстро."""
    monkeypatch.setattr(settings, "PASSWORD_HASH_ITERATIONS", 1000)


@pytest.fixture
def session():
    """Новая пустая база SQLite в памяти для каждого теста."""
    factory = create_session_factory("sqlite:///:memory:")
    with factory() as db_session:
        yield db_session


@pytest.fixture
def auth(session):
    return AuthService(session)


@pytest.fixture
def catalog(session):
    return CatalogService(session)


@pytest.fixture
def loans(session):
    return LoanService(session)


@pytest.fixture
def owner(auth):
    """Зарегистрированный Владелец."""
    return auth.register_user("Мария", "maria@example.com", "secret-pass-1")


@pytest.fixture
def other_owner(auth):
    """Второй Владелец с отдельной библиотекой."""
    return auth.register_user("Пётр", "petr@example.com", "secret-pass-2")


@pytest.fixture
def reader(auth):
    """Читатель (не может изменять каталог)."""
    return auth.register_user("Анна", "anna@example.com", "reader-pass-3", Role.READER)


@pytest.fixture
def book(catalog, owner):
    """Книга в каталоге Владельца."""
    return catalog.add_book(
        owner.id, "Мастер и Маргарита", "Михаил Булгаков", genre="Роман", year=1967
    )
