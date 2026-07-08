"""Cash-flow records and the reference dictionaries that classify them.

Four runtime-extensible catalogs. ``Status`` and ``Type`` are flat lists;
``Category`` belongs to a ``Type`` and ``Subcategory`` belongs to a
``Category``, forming the Тип → Категория → Подкатегория hierarchy. Both
hierarchy foreign keys use ``PROTECT`` so a parent cannot be deleted while it
still has children — the hierarchy is never left dangling.

``CashFlowRecord`` is the central entity; it references the catalog through
``PROTECT`` foreign keys (an in-use catalog row cannot be deleted) and enforces
the category∈type / subcategory∈category rules via the shared
:func:`check_hierarchy` helper, which the model and its serializer both call so
they never diverge.
"""

from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class Status(models.Model):
    """Статус — an independent, flat classification of a record."""

    name = models.CharField('название', max_length=255, unique=True)

    class Meta:
        verbose_name = 'статус'
        verbose_name_plural = 'статусы'
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class Type(models.Model):
    """Тип — top of the Тип → Категория → Подкатегория hierarchy."""

    name = models.CharField('название', max_length=255, unique=True)

    class Meta:
        verbose_name = 'тип'
        verbose_name_plural = 'типы'
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class Category(models.Model):
    """Категория — belongs to exactly one parent ``Type``."""

    name = models.CharField('название', max_length=255)
    type = models.ForeignKey(
        Type,
        on_delete=models.PROTECT,
        related_name='categories',
        verbose_name='тип',
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'
        ordering = ['name']
        unique_together = ('type', 'name')

    def __str__(self) -> str:
        return self.name


class Subcategory(models.Model):
    """Подкатегория — belongs to exactly one parent ``Category``."""

    name = models.CharField('название', max_length=255)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='subcategories',
        verbose_name='категория',
    )

    class Meta:
        verbose_name = 'подкатегория'
        verbose_name_plural = 'подкатегории'
        ordering = ['name']
        unique_together = ('category', 'name')

    def __str__(self) -> str:
        return self.name


def check_hierarchy(
    type: Type | None,
    category: Category | None,
    subcategory: Subcategory | None,
) -> dict[str, str]:
    """Validate the Тип → Категория → Подкатегория chain of a record.

    Returns a field-name → message mapping of any mismatches (empty when the
    combination is consistent). Shared by ``CashFlowRecord.clean`` and
    ``CashFlowRecordSerializer.validate`` so model- and API-level checks stay
    identical.
    """
    errors: dict[str, str] = {}
    if type is not None and category is not None:
        if category.type_id != type.pk:
            errors['category'] = 'Категория не принадлежит выбранному типу.'
    if category is not None and subcategory is not None:
        if subcategory.category_id != category.pk:
            errors['subcategory'] = (
                'Подкатегория не принадлежит выбранной категории.'
            )
    return errors


class CashFlowRecord(models.Model):
    """Запись ДДС — one cash-flow movement, classified by the catalog."""

    created_date = models.DateField('дата', default=date.today)
    status = models.ForeignKey(
        Status,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='records',
        verbose_name='статус',
    )
    type = models.ForeignKey(
        Type,
        on_delete=models.PROTECT,
        related_name='records',
        verbose_name='тип',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='records',
        verbose_name='категория',
    )
    subcategory = models.ForeignKey(
        Subcategory,
        on_delete=models.PROTECT,
        related_name='records',
        verbose_name='подкатегория',
    )
    amount = models.DecimalField(
        'сумма',
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    comment = models.TextField('комментарий', blank=True)

    class Meta:
        verbose_name = 'запись ДДС'
        verbose_name_plural = 'записи ДДС'
        ordering = ['-created_date', '-id']

    def __str__(self) -> str:
        return f'{self.created_date} — {self.amount} ₽'

    def clean(self) -> None:
        super().clean()
        errors = check_hierarchy(
            self.type if self.type_id else None,
            self.category if self.category_id else None,
            self.subcategory if self.subcategory_id else None,
        )
        if errors:
            raise ValidationError(errors)
