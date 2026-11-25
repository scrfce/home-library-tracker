# Диаграммы проекта «ДомБиблиотека»

Комплект из десяти диаграмм (День 3) плюс диаграмма Use Case (День 2). Исходные файлы лежат в каталоге [src](src).

| № | Диаграмма | Изображение | Исходник | Что описывает |
| --- | --- | --- | --- | --- |
| 0 | Use Case | [use-case.png](use-case.png) | [use-case.py](src/use-case.py) | Акторы и варианты использования (День 2) |
| 1 | Диаграмма классов | [class.png](class.png) | [class.puml](src/class.puml) | Статическая структура: классы, атрибуты, методы, связи |
| 2 | Диаграмма компонентов | [component.png](component.png) | [component.puml](src/component.puml) | Слои приложения, интерфейсы и зависимости |
| 3 | Диаграмма развёртывания | [deployment.png](deployment.png) | [deployment.puml](src/deployment.puml) | Узлы инфраструктуры и сетевые соединения |
| 4 | Диаграмма деятельности | [activity.png](activity.png) | [activity.puml](src/activity.puml) | Процесс оформления выдачи книги |
| 5 | Диаграмма состояний | [state-machine.png](state-machine.png) | [state-machine.puml](src/state-machine.puml) | Жизненный цикл объекта «Выдача» |
| 6 | Диаграмма кооперации | [communication.png](communication.png) | [communication.py](src/communication.py) | Сообщения между объектами при выдаче книги |
| 7 | IDEF0 A-0 | [idef0-a-0.png](idef0-a-0.png) | [idef0.py](src/idef0.py) | Система как единая функция |
| 8 | IDEF0 A0 | [idef0-a0.png](idef0-a0.png) | [idef0.py](src/idef0.py) | Декомпозиция на пять подфункций |
| 9 | DFD уровня 0 | [dfd-level-0.png](dfd-level-0.png) | [dfd-level-0.dot](src/dfd-level-0.dot) | Потоки данных между сущностями, процессами и хранилищами |
| 10 | DFD уровня 1 | [dfd-level-1.png](dfd-level-1.png) | [dfd-level-1.dot](src/dfd-level-1.dot) | Декомпозиция процесса 4.0 |

## Сквозное соответствие

| Область | Классы | Компонент | Use Case и требования | IDEF0 | DFD |
| --- | --- | --- | --- | --- | --- |
| Доступ пользователей | User, Owner, Reader, Invitation | AuthService | UC-01–UC-03 (FR-01–FR-03) | A1 | 1.0, D1 |
| Каталог книг | Library, Book, Category, Tag | CatalogService | UC-04–UC-09, UC-14 (FR-04–FR-09, FR-14) | A2 | 2.0, D2 |
| Запросы читателей | BookRequest | RequestService | UC-16, UC-18 (FR-16, FR-18) | A3 | 3.0, D4 |
| Выдача и возврат | Loan, Borrower | LoanService | UC-10–UC-13, UC-17 (FR-10–FR-13, FR-17) | A4 | 4.0 (4.1–4.4), D3 |
| Напоминания | Reminder | ReminderService | UC-15 (FR-15) | A5 | 5.0 |

## Как пересобрать диаграммы

- PlantUML (`*.puml`): `java -jar plantuml.jar -tpng -charset UTF-8 имя.puml`
- Graphviz (`*.dot`): `dot -Tpng -Gdpi=110 имя.dot -o имя.png`
- Python (`*.py`): `pip install matplotlib`, затем `python имя.py`
