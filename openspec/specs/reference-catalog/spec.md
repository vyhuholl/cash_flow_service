# reference-catalog Specification

## Purpose
TBD - created by archiving change reference-catalog. Update Purpose after archive.
## Requirements
### Requirement: Status dictionary
The system SHALL provide a `Status` dictionary (Статус) as a database-backed, runtime-extensible list. Each status SHALL have a human-readable `name` that is unique across all statuses.

#### Scenario: Seeded example values are representable
- **WHEN** the dictionary holds the ТЗ examples Бизнес, Личное, Налог
- **THEN** each is an independent row addressable by id

#### Scenario: List is extensible at runtime
- **WHEN** an operator creates a new status (e.g. "Инвестиции") via the API or admin
- **THEN** it is persisted and immediately usable without code or schema changes

#### Scenario: Names are unique
- **WHEN** an operator creates a status whose name already exists
- **THEN** the system rejects it with a validation error

### Requirement: Type dictionary
The system SHALL provide a `Type` dictionary (Тип) as a database-backed, runtime-extensible list. Each type SHALL have a `name` that is unique across all types. Types are the top of the Type→Category→Subcategory hierarchy.

#### Scenario: Seeded example values are representable
- **WHEN** the dictionary holds the ТЗ examples Пополнение and Списание
- **THEN** each is an independent row addressable by id

#### Scenario: List is extensible at runtime
- **WHEN** an operator creates a new type
- **THEN** it is persisted and immediately usable without code changes

### Requirement: Category belongs to a Type
The system SHALL provide a `Category` dictionary (Категория) where every category MUST reference exactly one parent `Type`. A category name SHALL be unique within its type.

#### Scenario: Category is created under a type
- **WHEN** an operator creates category "Маркетинг" under type "Списание"
- **THEN** the category is persisted with a foreign key to that type

#### Scenario: Category requires a type
- **WHEN** an operator attempts to create a category without a type
- **THEN** the system rejects it with a validation error

#### Scenario: Category name unique within a type
- **WHEN** an operator creates a second category named "Маркетинг" under the same type
- **THEN** the system rejects it; the same name under a different type is allowed

### Requirement: Subcategory belongs to a Category
The system SHALL provide a `Subcategory` dictionary (Подкатегория) where every subcategory MUST reference exactly one parent `Category`. A subcategory name SHALL be unique within its category.

#### Scenario: Subcategory is created under a category
- **WHEN** an operator creates subcategory "Farpost" under category "Маркетинг"
- **THEN** it is persisted with a foreign key to that category, transitively belonging to the category's type

#### Scenario: Subcategory requires a category
- **WHEN** an operator attempts to create a subcategory without a category
- **THEN** the system rejects it with a validation error

#### Scenario: Subcategory name unique within a category
- **WHEN** an operator creates a second "Farpost" under the same category
- **THEN** the system rejects it; the same name under a different category is allowed

### Requirement: CRUD REST API for every dictionary
The system SHALL expose full create/list/retrieve/update/delete REST endpoints for statuses, types, categories, and subcategories under the `/api/` router.

#### Scenario: Manage a dictionary over the API
- **WHEN** a client POSTs, GETs, PUT/PATCHes, and DELETEs against `/api/statuses/`, `/api/types/`, `/api/categories/`, `/api/subcategories/`
- **THEN** each operation performs the corresponding create/read/update/delete and returns standard DRF status codes

### Requirement: Hierarchy-scoped reads for cascading selects
The system SHALL allow categories to be listed filtered by their parent type, and subcategories to be listed filtered by their parent category, so a client can populate dependent dropdowns.

#### Scenario: List categories of a type
- **WHEN** a client requests `GET /api/categories/?type=<type_id>`
- **THEN** only categories belonging to that type are returned

#### Scenario: List subcategories of a category
- **WHEN** a client requests `GET /api/subcategories/?category=<category_id>`
- **THEN** only subcategories belonging to that category are returned

### Requirement: Referential integrity on delete
The system SHALL prevent deletion of a dictionary row that still has children, so the hierarchy cannot be left dangling. Deleting a type with categories, or a category with subcategories, MUST be rejected with a clear error until the children are removed or reassigned.

#### Scenario: Blocked parent deletion
- **WHEN** a client attempts to delete a category that still has subcategories
- **THEN** the system rejects the deletion with an error identifying the blocking children

#### Scenario: Allowed leaf deletion
- **WHEN** a client deletes a subcategory that has no dependents
- **THEN** the deletion succeeds

### Requirement: Admin management of the catalog
The system SHALL register all four dictionaries in the Django admin with the hierarchy visible and editable (e.g. subcategories inline under a category, categories filterable by type), so the catalog can be managed without the API.

#### Scenario: Catalog is manageable in the admin
- **WHEN** a staff user opens the admin
- **THEN** Status, Type, Category, and Subcategory are listed and editable, with each child's parent shown/selectable

