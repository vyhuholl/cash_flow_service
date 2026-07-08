"""Reference dictionaries for classifying cash-flow records.

Four runtime-extensible catalogs. ``Status`` and ``Type`` are flat lists;
``Category`` belongs to a ``Type`` and ``Subcategory`` belongs to a
``Category``, forming the Тип → Категория → Подкатегория hierarchy. Both
hierarchy foreign keys use ``PROTECT`` so a parent cannot be deleted while it
still has children — the hierarchy is never left dangling.
"""

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
