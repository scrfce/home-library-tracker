"""Точка входа: демонстрация работы модулей без веб-интерфейса.

Запуск из корня проекта: ``python -m src.main``.
Сценарий работает с базой в памяти и ничего не сохраняет на диск.
Веб-интерфейс (маршруты, шаблоны) подключается на следующем этапе.
"""

from datetime import date, timedelta

from src.database import create_session_factory
from src.services.auth_service import AuthService
from src.services.catalog_service import CatalogService
from src.services.loan_service import LoanService
from src.utils.errors import AppError


def step(title: str) -> None:
    """Печатает заголовок шага сценария."""
    print(f"\n=== {title} ===")


def attempt(description: str, action) -> None:
    """Выполняет действие и печатает результат или понятное сообщение об ошибке."""
    try:
        result = action()
    except AppError as error:
        print(f"  [отказ]  {description}: {error}")
    else:
        print(f"  [успех]  {description}")
        return result


def main() -> None:
    session = create_session_factory("sqlite:///:memory:")()
    auth, catalog, loans = AuthService(session), CatalogService(session), LoanService(session)
    today = date.today()

    step("Модуль «Аутентификация»")
    owner = attempt(
        "регистрация Владельца",
        lambda: auth.register_user("Мария", "maria@example.com", "secret-pass-1"),
    )
    attempt(
        "повторная регистрация с тем же email",
        lambda: auth.register_user("Мария", "maria@example.com", "secret-pass-1"),
    )
    attempt(
        "регистрация с коротким паролем",
        lambda: auth.register_user("Пётр", "petr@example.com", "123"),
    )
    attempt("вход с верным паролем", lambda: auth.login("maria@example.com", "secret-pass-1"))
    attempt("вход с неверным паролем", lambda: auth.login("maria@example.com", "wrong-password"))
    print(f"  Пароль в базе хранится как: {owner.password_hash[:32]}...")

    step("Модуль «Каталог»")
    master = attempt(
        "добавление книги",
        lambda: catalog.add_book(
            owner.id, "Мастер и Маргарита", "Михаил Булгаков", genre="Роман", year=1967
        ),
    )
    idiot = attempt(
        "добавление книги",
        lambda: catalog.add_book(owner.id, "Идиот", "Фёдор Достоевский", genre="Роман", year=1869),
    )
    attempt("добавление книги без автора", lambda: catalog.add_book(owner.id, "Без автора", ""))
    attempt(
        "изменение места хранения",
        lambda: catalog.update_book(owner.id, master.id, location="Шкаф 2, полка 3"),
    )
    found = catalog.search_books(owner.id, query="булгаков")
    print(f"  Поиск «булгаков»: {[book.title for book in found]}")

    step("Модуль «Выдача и возврат»")
    loan = attempt(
        "выдача «Мастера и Маргариты» Ивану",
        lambda: loans.issue_book(owner.id, master.id, "Иван Петров", today + timedelta(days=14)),
    )
    attempt(
        "повторная выдача той же книги",
        lambda: loans.issue_book(owner.id, master.id, "Анна", today + timedelta(days=7)),
    )
    attempt(
        "срок возврата раньше даты выдачи",
        lambda: loans.issue_book(owner.id, idiot.id, "Анна", today - timedelta(days=1)),
    )
    attempt("удаление выданной книги", lambda: catalog.delete_book(owner.id, master.id))
    print(f"  Книги «на руках»: {[item.book.title for item in loans.list_active_loans(owner.id)]}")
    in_a_month = today + timedelta(days=30)
    overdue = loans.list_overdue_loans(owner.id, today=in_a_month)
    overdue_info = [(item.book.title, item.days_overdue(in_a_month)) for item in overdue]
    print(f"  Просрочены через 30 дней (книга, дней): {overdue_info}")
    attempt("возврат книги", lambda: loans.return_book(owner.id, loan.id, note="Состояние хорошее"))
    attempt("повторный возврат", lambda: loans.return_book(owner.id, loan.id))
    print(f"  Статус книги после возврата: {master.status.value}")
    history = loans.get_book_history(owner.id, master.id)
    print(f"  История выдач: {[(item.borrower.name, str(item.return_date)) for item in history]}")
    session.close()


if __name__ == "__main__":
    main()
