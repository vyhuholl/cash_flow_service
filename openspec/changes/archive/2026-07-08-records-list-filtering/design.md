## Context

`cash-flow-records` exposes `/api/records/` with CRUD but no filtering, ordering, or table-optimized payload. The ТЗ's главная страница is a table filterable by date period, status, type, category, and subcategory. This change adds that queryable, table-ready list surface that `web-frontend` will consume. Pagination defaults already exist from `bootstrap-django-app`.

## Goals / Non-Goals

**Goals:**
- Date-period filter (`date_from`/`date_to`) plus exact filters for status/type/category/subcategory on the records list.
- Composable filters, deterministic ordering (newest first), pagination.
- Table-ready rows with resolved reference labels.

**Non-Goals:**
- Any change to record create/update/delete behavior (owned by `cash-flow-records`).
- The frontend table/controls (owned by `web-frontend`).
- Full-text/comment search, aggregation, CSV export — out of scope.

## Decisions

- **`django-filter` `FilterSet` as a DRF filter backend.** Add `django-filter` to deps and to `REST_FRAMEWORK['DEFAULT_FILTER_BACKENDS']`. A `CashFlowRecordFilter` declares: `date_from = DateFilter(field_name='created_date', lookup_expr='gte')`, `date_to = ...'lte'`, and `status`/`type`/`category`/`subcategory` as exact `ModelChoiceFilter`/`NumberFilter`. *Alternative:* hand-rolled `get_queryset` param parsing (as used for the small catalog filters) — rejected here because the records filter set is larger and django-filter also generates the browsable-API filter form, aiding review.
- **Default ordering `-created_date` (then `-id` as tiebreaker)** set on the viewset/model `Meta` for stable pagination.
- **Dedicated list serializer for table rows.** `CashFlowRecordListSerializer` adds read-only label fields (`status_name`, `type_name`, `category_name`, `subcategory_name` via `source=...`) alongside date/amount/comment. The viewset returns it for `list` and keeps the write serializer for create/update (`get_serializer_class`). *Alternative:* one serializer with nested objects — heavier payload; labels are enough for the table.
- **`select_related` on the list queryset** (`status`, `type`, `category`, `subcategory`) to avoid N+1 when resolving labels.
- **Pagination inherited** from the project default (`PageNumberPagination`, page size 25) — no per-view override.

## Risks / Trade-offs

- **New dependency (`django-filter`)** → small, standard, DRF-blessed; low risk.
- **Invalid filter values** (e.g. non-date `date_from`, non-int `type`) → django-filter returns 400 with field errors by default; keep `STRICTNESS` at the default rather than silently ignoring.
- **Label fields duplicate data already reachable by id** → intentional for table rendering; documented in the spec.
- **Ordering must be deterministic for pagination** → include a unique tiebreaker (`-id`) so equal dates don't reshuffle across pages.

## Migration Plan

1. Add `django-filter` to `pyproject.toml`; add `'django_filters'` to `INSTALLED_APPS` and set `DEFAULT_FILTER_BACKENDS`.
2. Add `CashFlowRecordFilter` (date range + four exact filters).
3. Add `CashFlowRecordListSerializer`; wire `get_serializer_class` + `select_related` + default ordering on the viewset.
4. Add tests (each filter, combined filters, empty filter, ordering, labels present); run `pytest` + ruff.

Rollback: remove the filter backend/setting, the filter class, and the list serializer; the CRUD surface from `cash-flow-records` is unaffected.

## Open Questions

- Expose `amount_min`/`amount_max` filtering too? Not in the ТЗ — deferred.
