"""DRF serializers for the reference catalog.

Each hierarchy relation is exposed as a writable parent id plus a read-only
parent name, so cascading-select clients get a human-readable label without an
extra fetch while writes stay a simple id assignment.
"""

from rest_framework import serializers

from cashflow.models import Category, Status, Subcategory, Type


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
