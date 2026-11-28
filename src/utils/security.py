"""Хэширование и проверка паролей (NFR-03).

Используется PBKDF2-HMAC-SHA256 из стандартной библиотеки с уникальной
солью для каждого пароля. Пароль в открытом виде нигде не хранится.
"""

import hashlib
import hmac
import os

from config import settings

_ALGORITHM = "pbkdf2_sha256"


def hash_password(password: str, iterations: int | None = None) -> str:
    """Возвращает строку вида ``pbkdf2_sha256$итерации$соль$хэш``."""
    rounds = iterations or settings.PASSWORD_HASH_ITERATIONS
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, rounds)
    return f"{_ALGORITHM}${rounds}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Проверяет пароль по сохранённому хэшу; при повреждённом хэше возвращает False."""
    try:
        algorithm, rounds, salt_hex, digest_hex = stored_hash.split("$")
        if algorithm != _ALGORITHM:
            return False
        candidate = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), int(rounds)
        )
        return hmac.compare_digest(candidate, bytes.fromhex(digest_hex))
    except (ValueError, TypeError):
        return False
