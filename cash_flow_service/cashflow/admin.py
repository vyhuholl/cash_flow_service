"""Django admin for the reference catalog.

Registers all four dictionaries with the Тип → Категория → Подкатегория
hierarchy visible and editable: categories are filterable by type and show
their subcategories inline, so the catalog can be managed without the API.
"""

from django.contrib import admin

from cashflow.models import Category, Status, Subcategory, Type


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
