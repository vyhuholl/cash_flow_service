## Why

The repository currently contains only a bare `django-admin startproject` skeleton: there is no application to hold domain models, Django REST Framework is a declared dependency but is not enabled, and there is no API routing. Every subsequent feature (справочники, ДДС records, filtering, frontend) needs this foundation in place first.

## What Changes

- Create a single Django app (e.g. `cashflow`) to host all domain models, serializers, viewsets, and admin registrations.
- Enable Django REST Framework: add `rest_framework` and the new app to `INSTALLED_APPS`.
- Configure DRF project defaults (pagination, default renderers incl. the browsable API for manual testing, and a sensible default schema for filtering later).
- Enable **drf-spectacular** to generate an OpenAPI 3 schema and serve interactive API docs (Swagger UI + ReDoc), so the growing API is self-documenting for reviewers.
- Add a versioned API URL namespace (e.g. `path('api/', include(...))`) alongside the existing `admin/` route, wired through a DRF router that later changes register onto.
- Set locale/formatting defaults appropriate to the domain: `LANGUAGE_CODE`/`TIME_ZONE` and decimal handling for ruble amounts.
- Establish the test setup (pytest-django settings) so later changes can add tests.

This change ships no business behavior — it is purely the scaffolding the other five changes build on.

## Capabilities

### New Capabilities
- `project-foundation`: A configured Django + DRF project with one domain app, an API router mounted under `/api/`, DRF defaults, and locale/formatting settings — the platform all other capabilities plug into.

### Modified Capabilities
<!-- None — this is the first change; no existing specs. -->

## Impact

- `cash_flow_service/cash_flow_service/settings.py` — `INSTALLED_APPS` (+ `drf_spectacular`), `REST_FRAMEWORK` (incl. `DEFAULT_SCHEMA_CLASS`), `SPECTACULAR_SETTINGS`, locale/formatting, test settings.
- `cash_flow_service/cash_flow_service/urls.py` — mount API router under `/api/`, plus the schema + Swagger UI + ReDoc routes.
- New app package (models/serializers/views/admin/urls/apps modules, initial empty state).
- `pyproject.toml` — confirm/pin `djangorestframework` (already present); add `drf-spectacular`; add `django-filter` only when `records-list-filtering` needs it.
- Blocks: `reference-catalog`, `cash-flow-records`, `records-list-filtering`, `web-frontend` all depend on this.
