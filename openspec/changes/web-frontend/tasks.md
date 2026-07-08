## 1. Shell and routing

- [ ] 1.1 Add `base.html` (Bootstrap 5, nav to Records / Reference); vendor Bootstrap + a CSRF/fetch helper as static files
- [ ] 1.2 Add frontend views (`TemplateView`/thin views) and routes at project root: `''`, `records/new`, `records/<int:pk>/edit`, `reference`
- [ ] 1.3 Ensure the CSRF cookie is set and an `X-CSRFToken` fetch helper is available to all pages

## 2. Home page (records table + filters)

- [ ] 2.1 Template with the 7-column table and filter controls (date period, status, type, category, subcategory)
- [ ] 2.2 JS: load `/api/records/` with filter params, render rows, handle pagination
- [ ] 2.3 JS: populate filter dropdowns from the catalog endpoints; clear-filters resets the table
- [ ] 2.4 Row edit (navigate to form) and delete (confirm → DELETE → remove row)

## 3. Record create/edit form

- [ ] 3.1 Template with all fields (date, status, type, category, subcategory, amount, comment)
- [ ] 3.2 Cascading selects: type→categories and category→subcategories via `?type=`/`?category=`; reset stale child on parent change; ignore stale responses
- [ ] 3.3 Edit mode: fetch the record and pre-select type/category/subcategory
- [ ] 3.4 Client validation: required amount/type/category/subcategory, positive amount, hierarchy consistency — block submit and flag fields
- [ ] 3.5 Submit create/update; map DRF field errors and 409s back to inputs; on success return to the table

## 4. Reference management page

- [ ] 4.1 Template: one section per dictionary (status/type/category/subcategory) with list + add/edit/delete
- [ ] 4.2 JS: CRUD each dictionary over `/api/...`; parent selectors for category (type) and subcategory (category)
- [ ] 4.3 Surface blocked-deletion (409) as a dismissible alert

## 5. Verification

- [ ] 5.1 Smoke tests: each route returns 200 and renders its shell
- [ ] 5.2 Manual walkthrough: create → filter → edit → delete a record; verify cascading + client validation
- [ ] 5.3 Manual walkthrough: add/edit/delete catalog entries incl. a blocked delete
- [ ] 5.4 Run `ruff check`/`ruff format --check` on any Python added
