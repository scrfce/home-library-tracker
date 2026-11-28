"""Проверка входных данных (NFR-06).

Функции возвращают очищенное значение или выбрасывают ValidationError.
"""

import re
from datetime import date

from config import settings
from src.utils.errors import ValidationError

_EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$")


def require_text(value: object, field: str, max_length: int, required: bool = True) -> str | None:
    """Проверяет текстовое поле и убирает пробелы по краям.

    Args:
        value: Проверяемое значение.
        field: Название поля для сообщения об ошибке.
        max_length: Максимально допустимая длина.
        required: Если False, пустое значение допустимо и вернётся None.

    Returns:
        Очищенная строка или None для пустого необязательного поля.

    Raises:
        ValidationError: Значение не строка, пустое обязательное или слишком длинное.
    """
    if value is None:
        text = ""
    elif isinstance(value, str):
        text = value.strip()
    else:
        raise ValidationError(f"Поле «{field}» должно быть текстом.", field)
    if not text:
        if required:
            raise ValidationError(f"Поле «{field}» обязательно для заполнения.", field)
        return None
    if len(text) > max_length:
        raise ValidationError(
            f"Поле «{field}» не должно быть длиннее {max_length} символов.", field
        )
    return text


def validate_email(email: object) -> str:
    """Проверяет адрес электронной почты и приводит его к нижнему регистру."""
    text = require_text(email, "email", settings.MAX_EMAIL_LENGTH)
    if not _EMAIL_RE.match(text):
        raise ValidationError("Адрес электронной почты имеет неверный формат.", "email")
    return text.lower()


def validate_password(password: object) -> str:
    """Проверяет длину пароля (FR-01: не короче 8 символов)."""
    if not isinstance(password, str) or not password.strip():
        raise ValidationError("Пароль обязателен для заполнения.", "password")
    if len(password) < settings.MIN_PASSWORD_LENGTH:
        raise ValidationError(
            f"Пароль должен содержать не менее {settings.MIN_PASSWORD_LENGTH} символов.", "password"
        )
    if len(password) > settings.MAX_PASSWORD_LENGTH:
        raise ValidationError(
            f"Пароль не должен быть длиннее {settings.MAX_PASSWORD_LENGTH} символов.", "password"
        )
    return password


def validate_year(year: object) -> int | None:
    """Проверяет год издания: пустое значение допустимо, иначе от 1000 до следующего года."""
    if year is None or year == "":
        return None
    if isinstance(year, bool) or not isinstance(year, int):
        raise ValidationError("Год издания должен быть целым числом.", "year")
    if not 1000 <= year <= date.today().year + 1:
        raise ValidationError("Год издания указан вне допустимого диапазона.", "year")
    return year


def validate_isbn(isbn: object) -> str | None:
    """Проверяет ISBN (10 или 13 цифр, дефисы допускаются); пустое значение допустимо."""
    text = require_text(isbn, "ISBN", 20, required=False)
    if text is None:
        return None
    digits = text.replace("-", "").replace(" ", "")
    if (
        not digits[:-1].isdigit()
        or len(digits) not in (10, 13)
        or not (digits[-1].isdigit() or digits[-1] in "Xx")
    ):
        raise ValidationError("ISBN должен содержать 10 или 13 цифр.", "ISBN")
    return text


def validate_loan_dates(issue_date: object, due_date: object) -> tuple[date, date]:
    """Проверяет даты выдачи (FR-10): срок не раньше даты выдачи и не больше MAX_LOAN_DAYS."""
    if not isinstance(issue_date, date) or not isinstance(due_date, date):
        raise ValidationError("Даты выдачи и возврата должны быть датами.", "due_date")
    if due_date < issue_date:
        raise ValidationError("Срок возврата не может быть раньше даты выдачи.", "due_date")
    if (due_date - issue_date).days > settings.MAX_LOAN_DAYS:
        raise ValidationError(
            f"Срок выдачи не может превышать {settings.MAX_LOAN_DAYS} дней.", "due_date"
        )
    return issue_date, due_date
