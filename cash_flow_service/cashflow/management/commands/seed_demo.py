"""Populate the database with demonstration data.

Seeds the reference catalog and a handful of sample records taken from the ТЗ
examples (statuses Бизнес/Личное/Налог, types Пополнение/Списание, categories
Инфраструктура→VPS,Proxy and Маркетинг→Farpost,Avito under «Списание»). Every
row is created with ``get_or_create`` so the command is idempotent — running it
repeatedly never duplicates data.

Usage (from the nested project dir): ``manage.py seed_demo``.
"""

from datetime import date
from decimal import Decimal
from typing import Any

from django.core.management.base import BaseCommand
from django.db import transaction

from cashflow.models import (
    CashFlowRecord,
    Category,
    Status,
    Subcategory,
    Type,
)

# Категория → её подкатегории (все относятся к типу «Списание» по ТЗ).
CATALOG: dict[str, tuple[str, ...]] = {
    'Инфраструктура': ('VPS', 'Proxy'),
    'Маркетинг': ('Farpost', 'Avito'),
}

# (дата, статус, категория, подкатегория, сумма, комментарий)
DEMO_RECORDS: list[tuple[date, str, str, str, Decimal, str]] = [
    (
        date(2025, 1, 1),
        'Бизнес',
        'Инфраструктура',
        'VPS',
        Decimal('1000.00'),
        'Аренда VPS',
    ),
    (
        date(2025, 1, 5),
        'Бизнес',
        'Инфраструктура',
        'Proxy',
        Decimal('500.00'),
        'Прокси на месяц',
    ),
    (
        date(2025, 1, 10),
        'Личное',
        'Маркетинг',
        'Farpost',
        Decimal('2500.00'),
        'Объявление на Farpost',
    ),
    (
        date(2025, 2, 1),
        'Бизнес',
        'Маркетинг',
        'Avito',
        Decimal('3200.00'),
        'Продвижение на Avito',
    ),
    (
        date(2025, 2, 15),
        'Налог',
        'Инфраструктура',
        'VPS',
        Decimal('1500.00'),
        '',
    ),
]


class Command(BaseCommand):
    help = 'Заполняет базу демонстрационными данными (идемпотентно).'

    @transaction.atomic
    def handle(self, *args: Any, **options: Any) -> None:
        statuses = {
            name: Status.objects.get_or_create(name=name)[0]
            for name in ('Бизнес', 'Личное', 'Налог')
        }
        types = {
            name: Type.objects.get_or_create(name=name)[0]
            for name in ('Пополнение', 'Списание')
        }

        spisanie = types['Списание']
        categories: dict[str, Category] = {}
        subcategories: dict[tuple[str, str], Subcategory] = {}
        for category_name, subcategory_names in CATALOG.items():
            category, _ = Category.objects.get_or_create(
                type=spisanie, name=category_name
            )
            categories[category_name] = category
            for subcategory_name in subcategory_names:
                subcategory, _ = Subcategory.objects.get_or_create(
                    category=category, name=subcategory_name
                )
                subcategories[(category_name, subcategory_name)] = subcategory

        created = 0
        for (
            created_date,
            status_name,
            category_name,
            subcategory_name,
            amount,
            comment,
        ) in DEMO_RECORDS:
            _, was_created = CashFlowRecord.objects.get_or_create(
                created_date=created_date,
                type=spisanie,
                category=categories[category_name],
                subcategory=subcategories[(category_name, subcategory_name)],
                amount=amount,
                defaults={
                    'status': statuses[status_name],
                    'comment': comment,
                },
            )
            if was_created:
                created += 1

        self.stdout.write(
            self.style.SUCCESS(
                'Демо-данные готовы: '
                f'статусов {len(statuses)}, типов {len(types)}, '
                f'категорий {len(categories)}, '
                f'подкатегорий {len(subcategories)}, '
                f'новых записей {created}.'
            )
        )
