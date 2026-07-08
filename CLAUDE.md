# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Проект

Веб-сервис для учёта движения денежных средств (ДДС): создание, просмотр,
редактирование и удаление записей о денежных операциях с классификацией по
статусу, типу, категории и подкатегории. Справочники расширяемы, между ними
действует иерархия Тип → Категория → Подкатегория. Бэкенд — REST API на DRF,
фронтенд — свои страницы (таблица с фильтрами, форма записи с каскадными
селектами, страница управления справочниками).

## Стек

- **Python 3.14**, менеджер зависимостей — **uv**.
- **Django 6** (+ Django ORM), **Django REST Framework**.
- **SQLite** (для простоты).
- Фронтенд: Django-шаблоны + Bootstrap 5 + vanilla JS (`fetch`).

Django-проект лежит во вложенной директории `cash_flow_service/` — команды
`manage.py` запускать оттуда. Весь код приложения — в app `cashflow`.

## Ключевые зависимости

- Runtime: `django`, `djangorestframework` (плюс `django-filter` — добавляется
  в рамках фильтрации списка записей).
- Dev: `ruff` (форматтер + линтер), `mypy` + `django-stubs` (тайпчекер),
  `pytest` + `pytest-django` + `pytest-cov` (тесты).

## Требования к качеству кода

- **Все команды запускать внутри виртуального окружения через `uv run`.**
- **Проверка кода — `make validate`**: форматтер, линтер и тайпчекер
  (`ruff format` → `ruff check` → `mypy`). Код должен проходить её без ошибок.
- **Тесты — `make test`** (`pytest --cov`).
- Ruff: длина строки **79**, одинарные кавычки. Тип-аннотации обязательны
  (проверяются mypy с `django-stubs`).
- Pre-commit hook запускает `make validate` на изменённых Python-файлах
  (миграции исключены) — не коммитить непроверенный код.

## Рабочий процесс

Работа спланирована как OpenSpec changes в `openspec/changes/` (6 изменений,
реализуются по порядку зависимостей: `bootstrap-django-app` →
`reference-catalog` → `cash-flow-records` → `records-list-filtering` →
`web-frontend` → `run-docs`). Каждое изменение содержит proposal / specs /
design / tasks. Реализация — через `/opsx:apply <change>`.
