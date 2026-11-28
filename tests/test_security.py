"""Проверка хэширования паролей (NFR-03)."""

from src.utils.security import hash_password, verify_password


def test_hash_is_not_plain_password():
    stored = hash_password("my-secret-1")
    assert "my-secret-1" not in stored
    assert stored.startswith("pbkdf2_sha256$")


def test_same_password_gives_different_hashes():
    assert hash_password("my-secret-1") != hash_password("my-secret-1")


def test_verify_correct_and_wrong_password():
    stored = hash_password("my-secret-1")
    assert verify_password("my-secret-1", stored) is True
    assert verify_password("another-pass", stored) is False


def test_verify_broken_hash_returns_false():
    assert verify_password("my-secret-1", "это-не-хэш") is False
    assert verify_password("my-secret-1", "md5$1$zz$zz") is False
