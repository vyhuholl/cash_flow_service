# records-web-ui Specification

## Purpose
TBD - created by archiving change web-frontend. Update Purpose after archive.
## Requirements
### Requirement: Records table on the home page
The system SHALL serve a home page (`/`) rendering a table of ДДС records with the columns date, status, type, category, subcategory, amount, and comment, populated from the records list API.

#### Scenario: Home page lists records
- **WHEN** a user opens `/`
- **THEN** a table of records is shown with all seven columns and paginated navigation

### Requirement: Filter controls on the home page
The home page SHALL provide filter controls for date period, status, type, category, and subcategory that drive the records list API and update the table.

#### Scenario: Applying a filter narrows the table
- **WHEN** a user sets any combination of the date-period, status, type, category, or subcategory controls and applies them
- **THEN** the table re-loads showing only matching records

#### Scenario: Clearing filters restores all
- **WHEN** a user clears the filters
- **THEN** the table shows all records again

### Requirement: Row edit and delete actions
Each row SHALL offer edit and delete actions; delete SHALL require confirmation.

#### Scenario: Delete a record from the table
- **WHEN** a user triggers delete on a row and confirms
- **THEN** the record is deleted via the API and the row disappears

#### Scenario: Edit navigates to the form
- **WHEN** a user triggers edit on a row
- **THEN** the create/edit form opens pre-filled with that record

### Requirement: Create/edit record form
The system SHALL serve a form (`/records/new` and `/records/<id>/edit`) for all record fields — date, status, type, category, subcategory, amount, comment — backed by the record API for create and update.

#### Scenario: Create a record
- **WHEN** a user fills the form with valid data and submits on `/records/new`
- **THEN** a record is created via the API and the user returns to the table showing it

#### Scenario: Edit a record
- **WHEN** a user changes fields on `/records/<id>/edit` and submits
- **THEN** the record is updated via the API

### Requirement: Cascading dependent selects
On the record form, choosing a Type SHALL filter the Category options to that type, and choosing a Category SHALL filter the Subcategory options to that category, using the catalog's hierarchy-scoped reads. Changing a parent selection SHALL reset any now-invalid child selection.

#### Scenario: Category options follow the chosen type
- **WHEN** a user selects a type
- **THEN** the category select offers only categories of that type

#### Scenario: Subcategory options follow the chosen category
- **WHEN** a user selects a category
- **THEN** the subcategory select offers only subcategories of that category

#### Scenario: Parent change resets stale child
- **WHEN** a user changes the type (or category) after a child was chosen
- **THEN** the now-invalid category (or subcategory) selection is cleared

### Requirement: Client-side validation mirrors server rules
The form SHALL validate on the client before submit: `amount`, `type`, `category`, and `subcategory` required, amount positive, and the chosen category/subcategory consistent with their parents — so an invalid combination cannot be submitted. Server-side (DRF) validation errors SHALL still be surfaced inline.

#### Scenario: Invalid form blocked on the client
- **WHEN** a user tries to submit with a missing required field, a non-positive amount, or an inconsistent hierarchy selection
- **THEN** submission is blocked and the offending fields are flagged

#### Scenario: Server error surfaced inline
- **WHEN** the API rejects a submission with a validation error
- **THEN** the error is displayed next to the relevant field

