## 1. Model

- [x] 1.1 Add `CashFlowRecord` to `cashflow/models.py`: `created_date = DateField(default=date.today)`, `amount = DecimalField(12,2)` with `MinValueValidator`, `comment = TextField(blank=True)`
- [x] 1.2 Add FKs `status` (null/blank), `type`, `category`, `subcategory`, all `on_delete=PROTECT`
- [x] 1.3 Add a shared hierarchy-check helper and call it from `Model.clean()` (category∈type, subcategory∈category)
- [x] 1.4 `make makemigrations cashflow` and review the migration

## 2. Serializer with validation

- [x] 2.1 `CashFlowRecordSerializer` exposing all fields; enforce required amount/type/category/subcategory
- [x] 2.2 `validate()`: positive amount, category belongs to type, subcategory belongs to category — with clear field/non-field errors
- [x] 2.3 Reuse the shared hierarchy helper so serializer and model stay in sync

## 3. API

- [x] 3.1 `CashFlowRecordViewSet` (`ModelViewSet`)
- [x] 3.2 Register `records` on the router in `cashflow/urls.py`

## 4. Admin

- [x] 4.1 Register `CashFlowRecordAdmin` with `list_display`, `list_filter` on reference fields, `date_hierarchy`, `search_fields`

## 5. Tests and verification

- [x] 5.1 Test required-field errors (missing amount/type/category/subcategory)
- [x] 5.2 Test non-positive amount rejected; date defaults to today and can be overridden
- [x] 5.3 Test hierarchy rules: mismatched category→type and subcategory→category rejected; consistent ones accepted
- [x] 5.4 Test PROTECT: deleting a catalog row referenced by a record is rejected
- [x] 5.5 Run `make migrate`, `make test`, `make validate`
- [x] 5.6 Manually create/edit/delete a record via the browsable API and the admin
