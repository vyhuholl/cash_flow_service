## Why

ДДС records are classified by Status (Статус), Type (Тип), Category (Категория), and Subcategory (Подкатегория). The ТЗ requires every one of these lists to be **extensible** ("Данный список должен иметь возможность расширяться") and to encode a strict hierarchy (Subcategory belongs to Category, Category belongs to Type). This rules out Python `choices`/enums and requires first-class, DB-backed, editable dictionaries with referential integrity. This change delivers those dictionaries and their management API before any record can reference them.

## What Changes

- Add four models: `Status`, `Type`, `Category`, `Subcategory`.
- Encode the hierarchy with foreign keys: `Category.type → Type`, `Subcategory.category → Category`. `Status` and `Type` are flat lists.
- Make each dictionary extensible at runtime (rows are data, not code) with a human-readable `name` and uniqueness constraints where appropriate (e.g. unique subcategory name within a category).
- Provide full CRUD over each dictionary via DRF serializers + viewsets (Добавление/редактирование/удаление статусов, типов, категорий и подкатегорий).
- Register all four models in the Django admin with inlines/list filters that make the hierarchy visible and editable.
- Enforce hierarchy integrity on delete (protect or cascade — decided in design) so records can't be orphaned.
- Provide read endpoints suitable for the frontend's cascading selects: categories filterable by type, subcategories filterable by category.

## Capabilities

### New Capabilities
- `reference-catalog`: The Status/Type/Category/Subcategory dictionaries, their Type→Category→Subcategory hierarchy, referential-integrity rules, and full CRUD REST API + admin for managing them.

### Modified Capabilities
<!-- None. -->

## Impact

- New models + initial migration in the `cashflow` app.
- New serializers, viewsets, and router registrations under `/api/` (`statuses/`, `types/`, `categories/`, `subcategories/`).
- Admin registrations for the four models.
- Depends on: `bootstrap-django-app`.
- Blocks: `cash-flow-records` (records reference these), `web-frontend` (cascading selects consume these endpoints).
