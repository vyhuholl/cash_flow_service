## 1. Model

- [ ] 1.1 Add `CashFlowRecord` to `cashflow/models.py`: `created_date = DateField(default=date.today)`, `amount = DecimalField(12,2)` with `MinValueValidator`, `comment = TextField(blank=True)`
- [ ] 1.2 Add FKs `status` (null/blank), `type`, `category`, `subcategory`, all `on_delete=PROTECT`
- [ ] 1.3 Add a shared hierarchy-check helper and call it from `Model.clean()` (category∈type, subcategory∈category)
- [ ] 1.4 `makemigrations cashflow` and review the migration

## 2. Serializer with validation

- [ ] 2.1 `CashFlowRecordSerializer` exposing all fields; enforce required amount/type/category/subcategory
- [ ] 2.2 `validate()`: positive amount, category belongs to type, subcategory belongs to category — with clear field/non-field errors
- [ ] 2.3 Reuse the shared hierarchy helper so serializer and model stay in sync

## 3. API

- [ ] 3.1 `CashFlowRecordViewSet` (`ModelViewSet`)
- [ ] 3.2 Register `records` on the router in `cashflow/urls.py`

## 4. Admin

- [ ] 4.1 Register `CashFlowRecordAdmin` with `list_display`, `list_filter` on reference fields, `date_hierarchy`, `search_fields`

## 5. Tests and verification

- [ ] 5.1 Test required-field errors (missing amount/type/category/subcategory)
- [ ] 5.2 Test non-positive amount rejected; date defaults to today and can be overridden
- [ ] 5.3 Test hierarchy rules: mismatched category→type and subcategory→category rejected; consistent ones accepted
- [ ] 5.4 Test PROTECT: deleting a catalog row referenced by a record is rejected
- [ ] 5.5 Run `manage.py migrate`, `pytest`, `ruff check`/`ruff format --check`
- [ ] 5.6 Manually create/edit/delete a record via the browsable API and the admin
