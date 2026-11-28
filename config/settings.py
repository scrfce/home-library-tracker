"""Настройки приложения.

Значения по умолчанию подходят для разработки. В рабочей среде их
переопределяют переменными окружения (см. config/.env.example).
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# База данных (NFR-12: SQLite).
DATABASE_URL = os.getenv("HOMELIBRARY_DATABASE_URL", f"sqlite:///{BASE_DIR / 'library.db'}")

# Пароли (FR-01, NFR-03).
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128
PASSWORD_HASH_ITERATIONS = 200_000

# Ограничения на текстовые поля.
MAX_NAME_LENGTH = 100
MAX_EMAIL_LENGTH = 254
MAX_TEXT_LENGTH = 200
MAX_NOTE_LENGTH = 500

# Правила выдачи книг (FR-10).
MAX_LOAN_DAYS = 90
