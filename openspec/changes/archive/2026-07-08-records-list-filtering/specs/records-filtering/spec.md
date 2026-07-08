## ADDED Requirements

### Requirement: Filter records by date period
The records list endpoint SHALL support filtering by a date period over `created_date`, via inclusive `date_from` and `date_to` bounds that may be supplied independently or together.

#### Scenario: Bounded period
- **WHEN** a client requests the list with `date_from` and `date_to`
- **THEN** only records whose `created_date` falls within that inclusive range are returned

#### Scenario: Open-ended bound
- **WHEN** a client supplies only `date_from` (or only `date_to`)
- **THEN** records on or after `date_from` (or on or before `date_to`) are returned

### Requirement: Filter records by classification
The records list endpoint SHALL support exact-match filters by `status`, `type`, `category`, and `subcategory` (by id).

#### Scenario: Single classification filter
- **WHEN** a client filters by a specific type id
- **THEN** only records of that type are returned

#### Scenario: Filter by subcategory
- **WHEN** a client filters by a specific subcategory id
- **THEN** only records with that subcategory are returned

### Requirement: Filters compose and default to all
The endpoint SHALL combine any subset of the supported filters with AND semantics, and SHALL return all records when no filter is supplied.

#### Scenario: Combined filters
- **WHEN** a client supplies a date period and a status and a category together
- **THEN** only records matching all of those conditions are returned

#### Scenario: No filter returns everything
- **WHEN** a client requests the list with no filter parameters
- **THEN** all records are returned (subject to pagination)

### Requirement: Deterministic ordering and pagination
The endpoint SHALL return records in a deterministic default order (newest `created_date` first) and SHALL paginate results.

#### Scenario: Newest first
- **WHEN** a client lists records spanning several dates
- **THEN** results are ordered by `created_date` descending by default

#### Scenario: Paginated response
- **WHEN** the result set exceeds one page
- **THEN** the response is paginated with navigation to further pages

### Requirement: Table-ready rows
Each row returned by the list endpoint SHALL carry the columns named in the ТЗ — date, status, type, category, subcategory, amount, comment — with the reference fields resolved to human-readable labels so a client can render the table without extra lookups.

#### Scenario: Row carries resolved labels
- **WHEN** a client reads a row from the list
- **THEN** it includes the display name of the status, type, category, and subcategory (not only their ids), plus date, amount, and comment
