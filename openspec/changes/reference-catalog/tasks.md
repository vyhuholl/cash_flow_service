## 1. Models

- [ ] 1.1 Add `Status` and `Type` models (unique `name`, `__str__`, ordering) in `cashflow/models.py`
- [ ] 1.2 Add `Category` with `type = FK(Type, on_delete=PROTECT)` and `unique_together = (type, name)`
- [ ] 1.3 Add `Subcategory` with `category = FK(Category, on_delete=PROTECT)` and `unique_together = (category, name)`
- [ ] 1.4 `python manage.py makemigrations cashflow` and review the generated migration

## 2. Serializers

- [ ] 2.1 `StatusSerializer` and `TypeSerializer` (id, name)
- [ ] 2.2 `CategorySerializer` (id, name, `type`, read-only `type_name`)
- [ ] 2.3 `SubcategorySerializer` (id, name, `category`, read-only `category_name`)

## 3. ViewSets and routes

- [ ] 3.1 `StatusViewSet` and `TypeViewSet` (`ModelViewSet`)
- [ ] 3.2 `CategoryViewSet` with `get_queryset` filtering on `?type=` (invalid/non-int → empty or 400, not 500)
- [ ] 3.3 `SubcategoryViewSet` with `get_queryset` filtering on `?category=`
- [ ] 3.4 Override `destroy`/`perform_destroy` to catch `ProtectedError` and return HTTP 409 naming the blocking children
- [ ] 3.5 Register `statuses`, `types`, `categories`, `subcategories` on the router in `cashflow/urls.py`

## 4. Admin

- [ ] 4.1 Register `Status` and `Type` admins (list_display, search)
- [ ] 4.2 `CategoryAdmin` with `list_filter`/`list_display` by type
- [ ] 4.3 `SubcategoryInline` under `CategoryAdmin`; register `Subcategory` admin

## 5. Tests and verification

- [ ] 5.1 Test uniqueness: duplicate status/type name rejected; duplicate category name allowed under a different type; same for subcategory
- [ ] 5.2 Test PROTECT: deleting a category with subcategories returns 409; deleting a childless subcategory succeeds
- [ ] 5.3 Test hierarchy reads: `?type=` and `?category=` return only matching rows
- [ ] 5.4 Run `manage.py migrate`, `pytest`, and `ruff check`/`ruff format --check`
- [ ] 5.5 Manually confirm all four dictionaries appear in the browsable API root and the admin
