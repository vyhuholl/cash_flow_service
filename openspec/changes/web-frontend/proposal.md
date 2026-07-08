## Why

The ТЗ requires a usable, intuitive interface with three specific pages and cross-field UX rules — most notably a create/edit form whose Category select auto-filters Subcategories, and where the user cannot pick a subcategory not tied to the chosen category (or a category not tied to the chosen type). The DRF API from the earlier changes exposes all the data and validation; this change builds the custom Bootstrap frontend on top of it, satisfying the "Интерфейс" and "Бизнес-правила" (client side) criteria.

## What Changes

- **Главная страница** (`records-web-ui`): a Bootstrap table of records (date, status, type, category, subcategory, amount, comment) with the filter controls (date period, status, type, category, subcategory) driving the `records-filtering` endpoint; per-row edit/delete actions.
- **Create/Edit record page** (`records-web-ui`): a form for all record fields backed by the record API, with:
  - **Cascading selects** — choosing a Type filters the Category options; choosing a Category filters the Subcategory options (options fetched from the `reference-catalog` endpoints). Stale child selections reset when the parent changes.
  - **Client-side validation** mirroring the server rules: `amount`/`type`/`category`/`subcategory` required, positive amount, and the hierarchy constraints — so invalid combinations can't even be submitted. Server errors from DRF are surfaced inline.
- **Reference management page** (`reference-web-ui`): CRUD UI for statuses, types, categories, and subcategories, including setting the Type→Category and Category→Subcategory links, over the `reference-catalog` endpoints.
- Serve these via lightweight Django `TemplateView`s (or static templates) + vanilla JS/`fetch`; wire their URLs (root `/` = главная).

## Capabilities

### New Capabilities
- `records-web-ui`: The главная страница records table with filters and the create/edit record form with cascading Type→Category→Subcategory selects and client-side validation.
- `reference-web-ui`: The справочник management page for CRUD over statuses/types/categories/subcategories and their hierarchy links.

### Modified Capabilities
<!-- None — this change is purely additive UI over existing APIs. -->

## Impact

- New Django templates (Bootstrap) and static JS/CSS assets.
- New `TemplateView`s / plain views + URL routes (root `/`, `/records/new`, `/records/<id>/edit`, `/reference`).
- No API changes — consumes `reference-catalog`, `cash-flow-records`, and `records-filtering` endpoints.
- Depends on: `bootstrap-django-app`, `reference-catalog`, `cash-flow-records`, `records-list-filtering`.
