"""Исключения приложения.

Сервисы выбрасывают только эти исключения. Слой маршрутов (routes)
преобразует их в понятные пользователю сообщения и коды ответа HTTP.
"""


class AppError(Exception):
    """Базовое исключение приложения."""


class ValidationError(AppError):
    """Некорректные входные данные (HTTP 400)."""

    def __init__(self, message: str, field: str | None = None) -> None:
        super().__init__(message)
        self.field = field


class AuthenticationError(AppError):
    """Не удалось подтвердить личность пользователя (HTTP 401)."""


class AccessDeniedError(AppError):
    """Недостаточно прав для действия или чужие данные (HTTP 403, NFR-04)."""


class NotFoundError(AppError):
    """Запрошенный объект не найден (HTTP 404)."""


class BusinessRuleError(AppError):
    """Нарушено правило предметной области, например книга уже выдана (HTTP 409)."""
