"""Базовый класс всех ORM-моделей."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Общий родитель моделей SQLAlchemy."""
