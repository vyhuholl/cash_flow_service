## Context

The repo is a bare `django-admin startproject` skeleton (`cash_flow_service/`): default `INSTALLED_APPS`, SQLite, `DEBUG=True`, only the `/admin/` route. `djangorestframework` is declared in `pyproject.toml` but not enabled, and there is no domain app. Stack is Django 6, Python 3.14, managed with `uv`; ruff (line length 79, single quotes) and pytest-django are dev dependencies. This change lays the platform every later capability (`reference-catalog`, `cash-flow-records`, `records-list-filtering`, `web-frontend`) plugs into; it ships no business behavior.

## Goals / Non-Goals

**Goals:**
- One domain app to hold all models/serializers/views/admin.
- DRF enabled with project-wide defaults (pagination, renderers incl. browsable API, precise decimals).
- A single DRF router mounted at `/api/` that later viewsets register onto with no further URLconf edits.
- An OpenAPI 3 schema + Swagger UI/ReDoc docs (drf-spectacular).
- A working pytest-django harness.

**Non-Goals:**
- Any domain models, endpoints, or UI (owned by later changes).
- `django-filter` wiring (deferred to `records-list-filtering`).
- Production hardening (secret management, `DEBUG=False`, `ALLOWED_HOSTS`, static serving) — out of scope for a test task on SQLite.
- Auth/permissions beyond DRF defaults (endpoints are open for review convenience).

## Decisions

- **Single app `cashflow` (not one app per entity).** The domain is small and tightly coupled (records reference every dictionary); one app keeps imports, migrations, and admin simple. Created via `manage.py startapp cashflow` inside the project package. *Alternative:* separate `records`/`catalog` apps — rejected as premature for this scope.
- **`DefaultRouter` mounted at `/api/`.** Gives a browsable API root that auto-lists registered viewsets, so later changes only call `router.register(...)`. Wired in `cashflow/urls.py` and `include()`d from the project `urls.py`. *Alternative:* hand-written `path()` entries per view — more boilerplate, no auto root.
- **Pagination = `PageNumberPagination`, page size 25.** Predictable page-number UX for the frontend table; set globally via `REST_FRAMEWORK`. *Alternative:* limit/offset — fine too, but page-number maps more directly onto a paged table UI.
- **Renderers = JSON + BrowsableAPI.** Keeps `curl`/frontend on JSON while giving reviewers a clickable API — directly supports the "correct DRF use" evaluation criterion.
- **drf-spectacular for the OpenAPI schema + docs.** Set `REST_FRAMEWORK['DEFAULT_SCHEMA_CLASS'] = 'drf_spectacular.openapi.AutoSchema'`, add a `SPECTACULAR_SETTINGS` block (title/description/version), and expose `/api/schema/` plus Swagger UI (`/api/schema/swagger-ui/`) and ReDoc (`/api/schema/redoc/`). Gives reviewers live, typed API docs that stay in sync as capabilities register endpoints. *Alternative:* DRF's built-in schema/`coreapi` — deprecated and less capable; rejected.
- **`COERCE_DECIMAL_TO_STRING = True` (DRF default, made explicit).** Ruble amounts stay exact decimals as strings; no float rounding. Documented here so `cash-flow-records` relies on it.
- **Locale kept `en-us` / `TIME_ZONE` explicit, `USE_TZ=True`.** Domain data is Russian *content*, not a UI-translation requirement; keeping the admin in English avoids partial-translation noise. Record dates are `DateField` (tz-independent).
- **pytest-django config in `pyproject.toml`** (`[tool.pytest.ini_options]` with `DJANGO_SETTINGS_MODULE`), rather than a separate `pytest.ini`, to keep configuration centralized.

## Risks / Trade-offs

- **Empty `/api/` root until viewsets register** → acceptable and expected; the next change (`reference-catalog`) fills it. The spec scenario asserts an empty route set, not an error.
- **Open (unauthenticated) endpoints** → fine for a local test-task review; noted as a Non-Goal rather than silently assumed.
- **`startapp` generates boilerplate files** (`tests.py`, `views.py`) → keep or trim to the modules actually used; not load-bearing.
- **Nested project layout** (`cash_flow_service/cash_flow_service/`) → run all `manage.py` commands from the inner `cash_flow_service/` dir; call this out in `run-docs`.

## Migration Plan

1. `manage.py startapp cashflow`; add `cashflow` and `rest_framework` to `INSTALLED_APPS`.
2. Add `drf_spectacular` to `INSTALLED_APPS`; add the `REST_FRAMEWORK` block (pagination, renderers, `COERCE_DECIMAL_TO_STRING`, `DEFAULT_SCHEMA_CLASS`) and a `SPECTACULAR_SETTINGS` block.
3. Create `cashflow/urls.py` with a `DefaultRouter`; `include('cashflow.urls')` under `api/` in the project `urls.py`; add the schema + Swagger UI + ReDoc routes.
4. Add `[tool.pytest.ini_options]` with `DJANGO_SETTINGS_MODULE`; add a trivial smoke test asserting `/api/` returns 200.
5. `manage.py migrate` + `manage.py check`; run `pytest`.

Rollback: revert the settings/urls edits and delete the `cashflow` app package (no data migrations shipped).

## Open Questions

- Should `LANGUAGE_CODE` become `ru-ru` for the admin? Deferred — decide when building `web-frontend`/admin polish; not blocking.
