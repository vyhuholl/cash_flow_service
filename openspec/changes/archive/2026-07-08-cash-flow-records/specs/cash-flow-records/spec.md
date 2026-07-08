## ADDED Requirements

### Requirement: Cash-flow record entity
The system SHALL provide a `CashFlowRecord` entity (запись ДДС) with the fields: `created_date` (date), `status` (→ Status, optional), `type` (→ Type), `category` (→ Category), `subcategory` (→ Subcategory), `amount` (decimal, rubles), and `comment` (free-form text, optional).

#### Scenario: Record persists all fields
- **WHEN** a record is created with a date, type, category, subcategory, amount, and optional status/comment
- **THEN** all fields are stored and returned on retrieval, with amount rendered as a fixed-precision string

### Requirement: Create, retrieve, update, and delete records
The system SHALL expose a REST API under `/api/records/` to create, retrieve, fully update (edit any field of any record), and delete any record.

#### Scenario: Full CRUD lifecycle
- **WHEN** a client POSTs a record, GETs it, PUT/PATCHes any field, then DELETEs it
- **THEN** each operation succeeds and returns the standard DRF status code

#### Scenario: Any record is editable and deletable
- **WHEN** a client edits or deletes an existing record
- **THEN** the change is applied regardless of the record's age or values

### Requirement: Date defaults to today but is editable
The `created_date` field SHALL default to the current date when omitted, and SHALL be overridable by the client on create or update.

#### Scenario: Date auto-filled
- **WHEN** a record is created without `created_date`
- **THEN** it is stored with today's date

#### Scenario: Date overridden manually
- **WHEN** a record is created or updated with an explicit `created_date` (e.g. 01.01.2025)
- **THEN** that date is stored instead of today

### Requirement: Required fields
The system SHALL require `amount`, `type`, `category`, and `subcategory` on every record. `status`, `created_date`, and `comment` are optional (date defaults to today; comment may be blank).

#### Scenario: Missing required field rejected
- **WHEN** a client submits a record without amount, type, category, or subcategory
- **THEN** the system rejects it with a field-level validation error for each missing field

#### Scenario: Optional fields may be omitted
- **WHEN** a client submits a valid record without status or comment
- **THEN** the record is created successfully

### Requirement: Amount must be positive
The `amount` SHALL be a positive decimal amount in rubles.

#### Scenario: Non-positive amount rejected
- **WHEN** a client submits a record with amount ≤ 0
- **THEN** the system rejects it with a validation error

### Requirement: Category must belong to the selected type
The system SHALL reject a record whose `category` does not belong to its `type`.

#### Scenario: Mismatched category rejected
- **WHEN** a client submits a record whose category's parent type differs from the record's type
- **THEN** the system rejects it with a validation error naming the conflict

#### Scenario: Consistent category accepted
- **WHEN** the record's category belongs to the record's type
- **THEN** validation passes for that constraint

### Requirement: Subcategory must belong to the selected category
The system SHALL reject a record whose `subcategory` does not belong to its `category`.

#### Scenario: Mismatched subcategory rejected
- **WHEN** a client submits a record whose subcategory's parent category differs from the record's category
- **THEN** the system rejects it with a validation error naming the conflict

#### Scenario: Consistent subcategory accepted
- **WHEN** the record's subcategory belongs to the record's category
- **THEN** validation passes for that constraint

### Requirement: Records protect referenced catalog rows
The system SHALL prevent deletion of a Status, Type, Category, or Subcategory that is still referenced by a record, so records cannot be orphaned.

#### Scenario: Referenced dictionary row cannot be deleted
- **WHEN** a client attempts to delete a catalog row still referenced by at least one record
- **THEN** the deletion is rejected with an error

### Requirement: Admin management of records
The system SHALL register `CashFlowRecord` in the Django admin with the reference foreign keys, a useful list display, and date-based navigation.

#### Scenario: Records manageable in admin
- **WHEN** a staff user opens the admin
- **THEN** records are listable, filterable by the reference fields, and editable
