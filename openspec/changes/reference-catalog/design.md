## Context

Builds on `bootstrap-django-app`, which provides the `cashflow` app, DRF, and a `DefaultRouter` mounted at `/api/`. The ТЗ requires four extensible dictionaries with a strict hierarchy (Тип → Категория → Подкатегория) plus an independent Статус, and full CRUD for managing them. Because the lists must be extensible at runtime, they are modelled as tables, not Python `choices`. `cash-flow-records` will reference these models next, and `web-frontend` will consume the hierarchy-scoped reads for cascading selects.

## Goals / Non-Goals

**Goals:**
- Four models — `Status`, `Type`, `Category (→Type)`, `Subcategory (→Category)` — with correct uniqueness and referential integrity.
- Full CRUD REST API for each, registered on the existing router.
- Hierarchy-scoped list reads (`?type=`, `?category=`) for dependent dropdowns.
- Admin management with the hierarchy visible.

**Non-Goals:**
- The `CashFlowRecord` model and its FKs into this catalog (owned by `cash-flow-records`).
- The management *UI* page (owned by `web-frontend`); this change ships API + admin only.
- Seed/demo data (owned by `run-docs`).
- `django-filter` — hierarchy filters here are done with a `get_queryset` override to avoid pulling the dependency before `records-list-filtering` needs it.

## Decisions

- **Four concrete models, each with a `name` CharField.** `Status` and `Type` have a globally unique `name`. `Category` has `type = FK(Type)` with `unique_together = (type, name)`. `Subcategory` has `category = FK(Category)` with `unique_together = (category, name)`. Each defines `__str__` and a stable default ordering by `name`. *Alternative:* a single generic tree/MPTT table — rejected as over-engineered for a fixed 2-level hierarchy.
- **`on_delete=PROTECT` for both hierarchy FKs.** Deleting a parent that still has children is rejected, satisfying the "referential integrity on delete" requirement and preventing dangling rows. The DRF `DELETE` traps `ProtectedError` and returns HTTP 409 with a message naming the blockers. *Alternative:* `CASCADE` — rejected: silently deleting a type would wipe its categories, subcategories, and (later) records.
- **Flat serializers exposing parent by id + read-only parent name.** `CategorySerializer` exposes `type` (writable id) and `type_name` (read-only); `SubcategorySerializer` exposes `category`/`category_name`. Keeps writes simple and gives the frontend a label without an extra fetch. *Alternative:* fully nested writable serializers — more complex, unnecessary here.
- **Hierarchy-scoped reads via `get_queryset` query params.** `CategoryViewSet` filters on `?type=`; `SubcategoryViewSet` on `?category=`. No new dependency. `records-list-filtering` will later introduce `django-filter` for the records endpoint; catalog filtering stays lightweight.
- **`ModelViewSet` per dictionary, registered on the bootstrap router** (`statuses`, `types`, `categories`, `subcategories`), so `/api/` auto-lists them in the browsable API.
- **Admin: `SubcategoryInline` under `CategoryAdmin`; `Category` `list_filter`/`list_display` by type.** Makes the hierarchy visible and editable without the API, satisfying the admin requirement.

## Risks / Trade-offs

- **PROTECT surfaces `ProtectedError` on delete** → mitigate by catching it in `perform_destroy`/`destroy` and returning a 409 with a clear message rather than a 500.
- **Uniqueness is scoped to the parent, not global** → intentional (Маркетинг can exist under two types); enforced by `unique_together` + surfaced as DRF `UniqueTogetherValidator` errors.
- **Records will later FK into these models** → their delete behavior (e.g. block deleting a status still used by records) is defined in `cash-flow-records`, not here; keep that boundary clean.
- **Query-param filtering is unvalidated** → a non-integer `?type=abc` should yield an empty list or 400, not a 500; handle in `get_queryset`.

## Migration Plan

1. Define the four models in `cashflow/models.py`; `makemigrations cashflow` → one initial migration.
2. Add serializers (`cashflow/serializers.py`) and `ModelViewSet`s (`cashflow/views.py`).
3. Register the four viewsets on the router in `cashflow/urls.py`.
4. Register admin classes with the subcategory inline and type filter.
5. `migrate`; add tests (uniqueness, PROTECT-on-delete → 409, `?type=`/`?category=` filtering); run `pytest` + ruff.

Rollback: drop the migration and remove the models/serializers/views/admin/router registrations (no other change depends on it yet at implementation time).

## Open Questions

- Should `Status` also participate in a hierarchy? No — per ТЗ it is an independent classification, kept flat.
