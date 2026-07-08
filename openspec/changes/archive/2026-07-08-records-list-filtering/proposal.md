## Why

The main screen of the service is a table of all ДДС records ("Просмотр списка всех записей"), and the ТЗ requires filtering that table by a date period, status, type, category, and subcategory. The record API from `cash-flow-records` returns records but has no filtering/period/ordering surface. This change adds the queryable list capability the главная страница depends on.

## What Changes

- Add a filter backend to the records list endpoint supporting:
  - **Date period** — `date_from` / `date_to` range over `created_date` (inclusive).
  - **Status**, **Type**, **Category**, **Subcategory** — exact-match filters (by id).
- Ensure filters compose (any subset can be combined) and an empty filter returns all records.
- Add deterministic default ordering (e.g. newest `created_date` first) and stable pagination for large datasets.
- Expose the list as a table-friendly payload: each row carries date, status, type, category, subcategory, amount, comment (the columns named in the ТЗ), with related names resolved so the client doesn't need extra lookups.
- Introduce `django-filter` as a dependency (or an equivalent DRF FilterSet) and wire it into DRF's `DEFAULT_FILTER_BACKENDS`.

## Capabilities

### New Capabilities
- `records-filtering`: A filterable, ordered, paginated list of ДДС records — filterable by date period, status, type, category, and subcategory — returning table-ready rows.

### Modified Capabilities
- `cash-flow-records`: the list surface of the records endpoint gains filter/order/pagination behavior (the create/retrieve/update/delete requirements are unchanged).

## Impact

- New DRF `FilterSet` (or filter backend) applied to the records viewset.
- `settings.py` — `REST_FRAMEWORK['DEFAULT_FILTER_BACKENDS']`, pagination defaults.
- `pyproject.toml` — add `django-filter`.
- List serializer/`to_representation` adjustments so rows are table-ready.
- Depends on: `bootstrap-django-app`, `reference-catalog`, `cash-flow-records`.
- Blocks: `web-frontend` (the главная страница table + filters consume this endpoint).
