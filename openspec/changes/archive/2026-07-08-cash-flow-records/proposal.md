## Why

The core purpose of the service is to record cash-flow movements (ДДС записи). Users must be able to create, view, edit, and delete individual records, each classified by the reference dictionaries. The ТЗ also imposes required fields and cross-field business rules that must be enforced on the server regardless of any client-side checks. This change delivers the record entity and its validated CRUD API.

## What Changes

- Add the `CashFlowRecord` model with fields:
  - `created_date` (Дата) — defaults to today, but editable by the user.
  - `status` (FK → Status), `type` (FK → Type), `category` (FK → Category), `subcategory` (FK → Subcategory).
  - `amount` (Сумма) — positive decimal in rubles.
  - `comment` (Комментарий) — free-form, optional/blank.
- Provide CRUD via a DRF serializer + viewset: create, retrieve, update (full record editable), and delete (any record deletable).
- Server-side validation:
  - Required fields: `amount`, `type`, `category`, `subcategory` (per ТЗ). `status` and `created_date` handling decided in design (`created_date` auto-defaults).
  - `amount` must be positive.
  - **Hierarchy integrity (business rules):** `category` must belong to the selected `type`; `subcategory` must belong to the selected `category`. Reject inconsistent combinations with clear field errors.
- Register `CashFlowRecord` in the Django admin (with the reference FKs, list display, and date hierarchy) for quick back-office CRUD.

## Capabilities

### New Capabilities
- `cash-flow-records`: The ДДС record entity and its validated create/retrieve/update/delete REST API, including required-field validation and Type→Category→Subcategory hierarchy-integrity enforcement.

### Modified Capabilities
<!-- None. The list-with-filters surface is introduced separately in records-list-filtering. -->

## Impact

- New `CashFlowRecord` model + migration in the `cashflow` app.
- New serializer (with `validate`/field-level validation), viewset, and router registration (`/api/records/`).
- Admin registration.
- Depends on: `bootstrap-django-app`, `reference-catalog`.
- Blocks: `records-list-filtering` (extends the records list surface), `web-frontend` (consumes the record API).
