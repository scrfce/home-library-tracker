"""Подключение к базе данных и создание таблиц."""

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from config import settings
from src.models import Base


def _register_unicode_lower(engine: Engine) -> None:
    """Подменяет lower() в SQLite версией с поддержкой Unicode.

    Встроенная функция SQLite приводит к нижнему регистру только латиницу,
    поэтому без подмены поиск «булгаков» не находит «Булгаков».
    """
    if engine.dialect.name != "sqlite":
        return

    @event.listens_for(engine, "connect")
    def _on_connect(dbapi_connection, _record) -> None:
        dbapi_connection.create_function(
            "lower",
            1,
            lambda value: value.lower() if value is not None else None,
            deterministic=True,
        )


def create_session_factory(
    database_url: str | None = None, echo: bool = False
) -> sessionmaker[Session]:
    """Создаёт подключение, таблицы (если их нет) и фабрику сессий.

    Args:
        database_url: Адрес базы данных; по умолчанию берётся из настроек.
        echo: Выводить SQL-запросы в консоль (для отладки).
    """
    engine = create_engine(database_url or settings.DATABASE_URL, echo=echo)
    _register_unicode_lower(engine)
    Base.metadata.create_all(engine)
    return sessionmaker(engine, expire_on_commit=False)
