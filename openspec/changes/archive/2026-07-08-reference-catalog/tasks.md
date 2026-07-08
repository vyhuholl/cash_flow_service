## 1. Models

- [x] 1.1 Add `Status` and `Type` models (unique `name`, `__str__`, ordering) in `cashflow/models.py`
- [x] 1.2 Add `Category` with `type = FK(Type, on_delete=PROTECT)` and `unique_together = (type, name)`
- [x] 1.3 Add `Subcategory` with `category = FK(Category, on_delete=PROTECT)` and `unique_together = (category, name)`
- [x] 1.4 `make makemigrations cashflow` and review the generated migration

## 2. Serializers

- [x] 2.1 `StatusSerializer` and `TypeSerializer` (id, name)
- [x] 2.2 `CategorySerializer` (id, name, `type`, read-only `type_name`)
- [x] 2.3 `SubcategorySerializer` (id, name, `category`, read-only `category_name`)

## 3. ViewSets and routes

- [x] 3.1 `StatusViewSet` and `TypeViewSet` (`ModelViewSet`)
- [x] 3.2 `CategoryViewSet` with `get_queryset` filtering on `?type=` (invalid/non-int → empty or 400, not 500)
- [x] 3.3 `SubcategoryViewSet` with `get_queryset` filtering on `?category=`
- [x] 3.4 Override `destroy`/`perform_destroy` to catch `ProtectedError` and return HTTP 409 naming the blocking children
- [x] 3.5 Register `statuses`, `types`, `categories`, `subcategories` on the router in `cashflow/urls.py`

## 4. Admin

- [x] 4.1 Register `Status` and `Type` admins (list_display, search)
- [x] 4.2 `CategoryAdmin` with `list_filter`/`list_display` by type
- [x] 4.3 `SubcategoryInline` under `CategoryAdmin`; register `Subcategory` admin

## 5. Tests and verification

- [x] 5.1 Test uniqueness: duplicate status/type name rejected; duplicate category name allowed under a different type; same for subcategory
- [x] 5.2 Test PROTECT: deleting a category with subcategories returns 409; deleting a childless subcategory succeeds
- [x] 5.3 Test hierarchy reads: `?type=` and `?category=` return only matching rows
- [x] 5.4 Run `make migrate`, `make test`, and `make validate`
- [x] 5.5 Manually confirm all four dictionaries appear in the browsable API root and the admin
