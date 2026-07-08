## Context

The API layer is complete after `reference-catalog`, `cash-flow-records`, and `records-list-filtering`: catalog CRUD with hierarchy-scoped reads, record CRUD with server validation, and a filterable table-ready records list. This change adds the custom Bootstrap frontend the ТЗ asks for — главная страница (table + filters), a create/edit form with cascading Type→Category→Subcategory selects and client-side validation, and a справочник management page — all consuming the existing endpoints. No API changes.

## Goals / Non-Goals

**Goals:**
- Three pages: home table+filters (`/`), record form (`/records/new`, `/records/<id>/edit`), reference management (`/reference`).
- Cascading dependent selects and client-side validation mirroring the server rules.
- Inline surfacing of DRF/409 errors.

**Non-Goals:**
- Any new API/endpoint or validation logic (already delivered upstream).
- Authentication/login UI (endpoints stay open for review, matching the API changes).
- A SPA framework/build step; keep it dependency-light.

## Decisions

- **Server-rendered Django templates + vanilla JS/`fetch`, Bootstrap 5.** Lightweight `TemplateView`s return HTML shells; JS calls the JSON API for data and mutations. *Alternative:* a React/Vue SPA — rejected as overkill for three pages and it complicates the "one command to run" story; *Alternative:* pure Django forms/ModelForm server round-trips — rejected because the cascading select + live client validation UX is far cleaner with the JSON API already built.
- **Cascading selects call the catalog reads** `GET /api/categories/?type=` and `GET /api/subcategories/?category=` on `change`, repopulating and clearing stale child selections. On edit, the initial load pre-selects the record's existing type/category/subcategory.
- **Client validation mirrors, does not replace, the server.** A small JS validator checks required amount/type/category/subcategory, positive amount, and hierarchy consistency before submit; the server remains the source of truth and its field errors are mapped back onto the inputs. *Alternative:* rely on server errors only — rejected; the ТЗ explicitly wants client-side validation.
- **CSRF handling.** Unsafe requests (`POST`/`PUT`/`PATCH`/`DELETE`) send the `X-CSRFToken` header read from the `csrftoken` cookie; DRF `SessionAuthentication` + Django CSRF middleware validate it. Ensure the CSRF cookie is set on the rendered pages.
- **Routing.** Frontend routes live in `cashflow/urls.py` (or a dedicated `web` urlconf) mounted at the project root, separate from the `/api/` namespace: `''` → home, `records/new`, `records/<int:pk>/edit`, `reference`.
- **Assets.** Bootstrap and any JS served as app static files (vendored or CDN); templates extend a shared `base.html` with the nav.
- **Reference page structure.** One section per dictionary with an inline add/edit row and a delete button; parent selectors for category (type) and subcategory (category); 409 responses rendered as a dismissible alert.

## Risks / Trade-offs

- **Client/server validation drift** → keep the client validator minimal and always defer to server errors; treat client checks as UX, not enforcement.
- **CSRF/session friction with `fetch`** → verify the cookie is present and the header is attached on every unsafe call; this is the most common failure point.
- **Cascading race conditions** (rapid parent changes) → ignore stale responses (track the latest request) so the child list matches the current parent.
- **No build step means hand-written JS** → keep it small, per-page, and unminified for reviewability; acceptable for this scope.

## Migration Plan

1. Add a `base.html` (Bootstrap + nav) and page templates; add `TemplateView`/thin views and frontend routes at the project root.
2. Home page JS: load `/api/records/` with filter params into the table; wire edit/delete row actions.
3. Form page JS: load field options, cascading selects, client validation, create/update submit, inline error mapping.
4. Reference page JS: list + CRUD per dictionary, parent selectors, 409 handling.
5. Smoke tests: each route returns 200 and renders its shell; manual walkthrough of create→filter→edit→delete and catalog management. Run ruff on any Python.

Rollback: remove the templates, static JS, frontend views, and routes; the API is untouched.

## Open Questions

- Bootstrap via CDN vs vendored static? Prefer vendored so the app runs offline / in Docker without external calls — confirm when wiring `run-docs`.
