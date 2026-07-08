"""Django admin for the cash-flow records and the reference catalog.

Registers all four dictionaries with the Тип → Категория → Подкатегория
hierarchy visible and editable: categories are filterable by type and show
their subcategories inline, so the catalog can be managed without the API.
``CashFlowRecord`` is registered with a summary list display, reference-field
filters, and date-based navigation for quick back-office CRUD.
"""

from django.contrib import admin

from cashflow.models import (
    CashFlowRecord,
    Category,
    Status,
    Subcategory,
    Type,
)


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Type)
class TypeAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


class SubcategoryInline(admin.TabularInline):
    model = Subcategory
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'type']
    list_filter = ['type']
    search_fields = ['name']
    inlines = [SubcategoryInline]


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']
    list_filter = ['category']
    search_fields = ['name']


@admin.register(CashFlowRecord)
class CashFlowRecordAdmin(admin.ModelAdmin):
    list_display = [
        'created_date',
        'type',
        'category',
        'subcategory',
        'amount',
        'status',
    ]
    list_filter = ['status', 'type', 'category', 'subcategory']
    date_hierarchy = 'created_date'
    search_fields = ['comment']
