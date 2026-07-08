## 1. Wire up django-filter

- [ ] 1.1 Add `django-filter` to `pyproject.toml` and run `uv sync`
- [ ] 1.2 Add `'django_filters'` to `INSTALLED_APPS`
- [ ] 1.3 Set `REST_FRAMEWORK['DEFAULT_FILTER_BACKENDS']` to include `DjangoFilterBackend`

## 2. Filter set

- [ ] 2.1 `CashFlowRecordFilter`: `date_from`/`date_to` over `created_date` (gte/lte)
- [ ] 2.2 Add exact filters for `status`, `type`, `category`, `subcategory`
- [ ] 2.3 Attach the filter set to `CashFlowRecordViewSet`

## 3. Table-ready list + ordering

- [ ] 3.1 `CashFlowRecordListSerializer` with read-only `*_name` label fields + date/amount/comment
- [ ] 3.2 `get_serializer_class` returns the list serializer for `list`, write serializer otherwise
- [ ] 3.3 Add `select_related` for the four reference FKs and default ordering `-created_date`, `-id`

## 4. Tests and verification

- [ ] 4.1 Test each filter individually (date period incl. open-ended, status, type, category, subcategory)
- [ ] 4.2 Test combined filters (AND semantics) and empty filter returns all
- [ ] 4.3 Test default ordering is newest-first and pagination works
- [ ] 4.4 Test rows include resolved label fields; assert no N+1 (query count)
- [ ] 4.5 Run `pytest` and `ruff check`/`ruff format --check`
- [ ] 4.6 Manually exercise the filter form in the browsable API at `/api/records/`
