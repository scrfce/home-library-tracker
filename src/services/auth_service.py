"""Модуль «Аутентификация»: регистрация и вход пользователей (FR-01, FR-02)."""

from sqlalchemy.orm import Session

from config import settings
from src.models import Role, User
from src.models.repositories import UserRepository
from src.utils.errors import AuthenticationError, BusinessRuleError, NotFoundError, ValidationError
from src.utils.security import hash_password, verify_password
from src.utils.validation import require_text, validate_email, validate_password


class AuthService:
    """Регистрация и проверка учётных данных."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self._users = UserRepository(session)

    def register_user(self, name: str, email: str, password: str, role: Role = Role.OWNER) -> User:
        """Создаёт учётную запись (FR-01).

        Args:
            name: Имя пользователя.
            email: Адрес электронной почты, уникальный в системе.
            password: Пароль не короче MIN_PASSWORD_LENGTH символов.
            role: Роль нового пользователя.

        Returns:
            Созданный пользователь.

        Raises:
            ValidationError: Имя, email или пароль некорректны.
            BusinessRuleError: Пользователь с таким email уже существует.
        """
        clean_name = require_text(name, "имя", settings.MAX_NAME_LENGTH)
        clean_email = validate_email(email)
        clean_password = validate_password(password)

        if self._users.get_by_email(clean_email) is not None:
            raise BusinessRuleError(
                "Пользователь с таким адресом электронной почты уже существует."
            )

        user = User(
            name=clean_name,
            email=clean_email,
            password_hash=hash_password(clean_password),
            role=role,
        )
        self._users.add(user)
        self._session.commit()
        return user

    def login(self, email: str, password: str) -> User:
        """Проверяет email и пароль (FR-02).

        Raises:
            ValidationError: Email или пароль не заполнены.
            AuthenticationError: Неверный email или пароль. Сообщение одинаково для обоих
                случаев, чтобы не раскрывать, зарегистрирован ли адрес.
        """
        clean_email = validate_email(email)
        if not isinstance(password, str) or not password:
            raise ValidationError("Пароль обязателен для заполнения.", "password")

        user = self._users.get_by_email(clean_email)
        if user is None or not verify_password(password, user.password_hash):
            raise AuthenticationError("Неверный адрес электронной почты или пароль.")
        return user

    def get_user(self, user_id: int) -> User:
        """Возвращает пользователя по идентификатору.

        Raises:
            NotFoundError: Пользователь не найден.
        """
        user = self._users.get(user_id)
        if user is None:
            raise NotFoundError("Пользователь не найден.")
        return user
