## Context

Builds on `bootstrap-django-app` (app, DRF, `/api/` router) and `reference-catalog` (Status/Type/Category/Subcategory with the Type→Category→Subcategory hierarchy). This change adds the central `CashFlowRecord` entity and its validated CRUD API. The ТЗ specifies which fields are mandatory (`amount`, `type`, `category`, `subcategory`) and two cross-field business rules (category∈type, subcategory∈category) that MUST hold server-side irrespective of the client. The filtered list surface and the UI are separate later changes.

## Goals / Non-Goals

**Goals:**
- `CashFlowRecord` model with correct field types, defaults, and delete-protection into the catalog.
- CRUD REST API at `/api/records/` with server-side validation of required fields, positive amount, and hierarchy integrity.
- Admin registration.

**Non-Goals:**
- Filtering/period/pagination of the list (owned by `records-list-filtering`).
- Any frontend or client-side validation (owned by `web-frontend`).
- Seed data (owned by `run-docs`).

## Decisions

- **`created_date = DateField(default=date.today)`** — a plain `DateField` (dates, not datetimes; the ТЗ example is `01.01.2025`), defaulted rather than `auto_now_add` so it stays user-editable on create *and* update. *Alternative:* `auto_now_add` — rejected, it would make the date read-only, violating "может быть изменена вручную".
- **`amount = DecimalField(max_digits=12, decimal_places=2)` with a positive validator** — decimals (never floats) for money; `MinValueValidator(Decimal('0.01'))`. Rendered as a string via the bootstrap `COERCE_DECIMAL_TO_STRING`.
- **`status` optional; `type`/`category`/`subcategory` required.** The ТЗ's validation section lists only amount/type/category/subcategory as mandatory — status is deliberately `null=True, blank=True`. *Alternative:* make status required — rejected as contradicting the spec's explicit required-field list.
- **All four catalog FKs use `on_delete=PROTECT`.** This is the record side of the integrity boundary noted in `reference-catalog`: a catalog row in use by a record cannot be deleted. Deletion attempts surface as the same 409 pattern.
- **Hierarchy validation in `serializer.validate()`**, not just the model. Cross-field checks (`category.type_id == type_id`, `subcategory.category_id == category_id`) run in the serializer so DRF returns clean field/non-field errors; `Model.clean()` mirrors them for admin safety. *Alternative:* DB constraints only — can't express "FK's FK equals another FK" cleanly and yields poor error messages.
- **`ModelViewSet` at `/api/records/`, registered on the bootstrap router.** Default (write) serializer here; the table-optimized list serializer is introduced by `records-list-filtering`.
- **Admin:** `list_display` (date, type, category, subcategory, amount, status), `list_filter` on the reference fields, `date_hierarchy='created_date'`, `search_fields` on comment.

## Risks / Trade-offs

- **Validation duplicated in serializer and `Model.clean()`** → mitigate by factoring the two hierarchy checks into a shared helper both call.
- **PROTECT means deleting an in-use catalog row 409s** → intended; the frontend/admin should surface it. Consistent with `reference-catalog`.
- **`date.today` uses server local date** → acceptable for this scope; `USE_TZ=True` affects datetimes, not `DateField`. Note if a timezone-sensitive "today" is ever required.
- **Amount precision `max_digits=12`** → supports up to 9,999,999,999.99 ₽; revisit only if larger sums are expected.

## Migration Plan

1. Add `CashFlowRecord` to `cashflow/models.py` (fields, defaults, PROTECT FKs, `clean()`); `makemigrations` → migration.
2. Add `CashFlowRecordSerializer` with `validate()` enforcing positive amount + the two hierarchy rules.
3. Add `CashFlowRecordViewSet`; register `records` on the router.
4. Register the admin.
5. `migrate`; add tests (required fields, positive amount, both hierarchy rules pass/fail, PROTECT on catalog delete); run `pytest` + ruff.

Rollback: drop the migration and remove the model/serializer/view/admin/route.

## Open Questions

- Should `status` become required later if the product wants it? Deferred — follow the ТЗ (optional) for now.
