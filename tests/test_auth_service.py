"""Проверка модуля «Аутентификация» (FR-01, FR-02)."""

import pytest

from src.models import Role
from src.utils.errors import AuthenticationError, BusinessRuleError, NotFoundError, ValidationError


def test_register_creates_user_with_hashed_password(auth):
    user = auth.register_user("Мария", "Maria@Example.com", "secret-pass-1")
    assert user.id is not None
    assert user.email == "maria@example.com"
    assert user.role is Role.OWNER
    assert user.password_hash != "secret-pass-1"
    assert "secret-pass-1" not in user.password_hash


def test_register_duplicate_email_is_rejected(auth, owner):
    with pytest.raises(BusinessRuleError):
        auth.register_user("Другая Мария", "MARIA@example.com", "another-pass-9")


@pytest.mark.parametrize(
    ("name", "email", "password"),
    [
        ("", "a@example.com", "secret-pass-1"),
        ("Имя", "не-почта", "secret-pass-1"),
        ("Имя", "a@example.com", "short"),
    ],
)
def test_register_invalid_data_is_rejected(auth, name, email, password):
    with pytest.raises(ValidationError):
        auth.register_user(name, email, password)


def test_login_with_correct_credentials(auth, owner):
    user = auth.login("maria@example.com", "secret-pass-1")
    assert user.id == owner.id


def test_login_is_case_insensitive_for_email(auth, owner):
    assert auth.login("MARIA@example.com", "secret-pass-1").id == owner.id


def test_login_wrong_password_is_rejected(auth, owner):
    with pytest.raises(AuthenticationError):
        auth.login("maria@example.com", "wrong-password")


def test_login_unknown_email_gives_same_error(auth, owner):
    with pytest.raises(AuthenticationError) as error:
        auth.login("nobody@example.com", "secret-pass-1")
    assert "Неверный адрес электронной почты или пароль" in str(error.value)


def test_login_empty_password_is_rejected(auth, owner):
    with pytest.raises(ValidationError):
        auth.login("maria@example.com", "")


def test_get_user_not_found(auth):
    with pytest.raises(NotFoundError):
        auth.get_user(999)
