"""DRF serializers for the catalog and cash-flow records.

Catalog serializers expose each hierarchy relation as a writable parent id plus
a read-only parent name, so cascading-select clients get a human-readable label
without an extra fetch while writes stay a simple id assignment. The record
serializer enforces required fields, a positive amount, and the
category∈type / subcategory∈category rules via the shared
:func:`~cashflow.models.check_hierarchy` helper.
"""

from typing import Any

from rest_framework import serializers

from cashflow.models import (
    Category,
    CashFlowRecord,
    Status,
    Subcategory,
    Type,
    check_hierarchy,
)


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ['id', 'name']


class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = ['id', 'name']


class CategorySerializer(serializers.ModelSerializer):
    type_name = serializers.CharField(source='type.name', read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'type', 'type_name']


class SubcategorySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source='category.name', read_only=True
    )

    class Meta:
        model = Subcategory
        fields = ['id', 'name', 'category', 'category_name']


class CashFlowRecordSerializer(serializers.ModelSerializer):
    """Read/write serializer for cash-flow records.

    ``amount``, ``type``, ``category`` and ``subcategory`` are required (the
    model makes ``status`` nullable, ``created_date`` defaulted and ``comment``
    blank, so DRF marks those optional). The positive-amount rule rides on the
    model's ``MinValueValidator``; ``validate`` adds the cross-field hierarchy
    checks.
    """

    class Meta:
        model = CashFlowRecord
        fields = [
            'id',
            'created_date',
            'status',
            'type',
            'category',
            'subcategory',
            'amount',
            'comment',
        ]

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        # On partial update only changed fields arrive; fall back to the
        # stored value so the hierarchy is checked against the full record.
        def resolve(field: str) -> Any:
            if field in attrs:
                return attrs[field]
            if self.instance is not None:
                return getattr(self.instance, field)
            return None

        errors = check_hierarchy(
            resolve('type'),
            resolve('category'),
            resolve('subcategory'),
        )
        if errors:
            raise serializers.ValidationError(errors)
        return attrs
