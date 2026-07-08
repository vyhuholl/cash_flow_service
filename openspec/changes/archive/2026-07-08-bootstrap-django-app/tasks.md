## 1. Create the domain app

- [x] 1.1 From the inner `cash_flow_service/` directory, run `python manage.py startapp cashflow`
- [x] 1.2 Trim generated boilerplate to the modules used now (keep `apps.py`, `admin.py`, `models.py`, `migrations/`); remove unused stubs
- [x] 1.3 Set a clear `AppConfig.verbose_name` in `cashflow/apps.py`

## 2. Enable DRF and configure settings

- [x] 2.1 Add `'rest_framework'` and `'cashflow'` to `INSTALLED_APPS`
- [x] 2.2 Add a `REST_FRAMEWORK` block: `DEFAULT_PAGINATION_CLASS` = `PageNumberPagination`, `PAGE_SIZE = 25`, `DEFAULT_RENDERER_CLASSES` = JSON + BrowsableAPI, `COERCE_DECIMAL_TO_STRING = True`
- [x] 2.3 Make `TIME_ZONE` explicit and keep `USE_TZ = True`; set `LANGUAGE_CODE = 'ru-RU'` and `TIME_ZONE = 'Europe/Moscow'`
- [x] 2.4 Add `drf-spectacular` (`uv add drf-spectacular`) and `'drf_spectacular'` to `INSTALLED_APPS`
- [x] 2.5 Set `REST_FRAMEWORK['DEFAULT_SCHEMA_CLASS'] = 'drf_spectacular.openapi.AutoSchema'` and add a `SPECTACULAR_SETTINGS` block (title, description, version)

## 3. Mount the API router

- [x] 3.1 Create `cashflow/urls.py` with a DRF `DefaultRouter` and an empty registration list (viewsets added by later changes)
- [x] 3.2 In `cash_flow_service/urls.py`, `include('cashflow.urls')` under the `api/` prefix, keeping the existing `admin/` route
- [x] 3.3 Add drf-spectacular routes: `/api/schema/` (`SpectacularAPIView`), `/api/schema/swagger-ui/` (Swagger UI), `/api/schema/redoc/` (ReDoc)

## 4. Test harness

- [x] 4.1 Add `[tool.pytest.ini_options]` to `pyproject.toml` with `DJANGO_SETTINGS_MODULE = 'cash_flow_service.settings'` and a `python_files`/`testpaths` setting
- [x] 4.2 Add a smoke test (`cashflow/tests.py` or `tests/`) asserting `GET /api/` returns 200 and `GET /admin/` serves the login page

## 5. Verify

- [x] 5.1 Run `uv run manage.py check` and `uv run manage.py migrate` — no errors
- [x] 5.2 Run `make test` — smoke test passes, zero collection errors
- [x] 5.3 Run `make validate`
- [x] 5.4 Manually open `/api/` (browsable API root renders) and `/admin/`
- [x] 5.5 Open `/api/schema/swagger-ui/` and confirm the schema loads (no operations until viewsets register)
