## ADDED Requirements

### Requirement: Reference management page
The system SHALL serve a management page (`/reference`) that lists the statuses, types, categories, and subcategories and supports creating, editing, and deleting each of them over the catalog API.

#### Scenario: View the catalog
- **WHEN** a user opens `/reference`
- **THEN** the four dictionaries are listed with their current entries

#### Scenario: Create and edit an entry
- **WHEN** a user adds a new entry or edits an existing one in any dictionary and saves
- **THEN** the change is persisted via the API and reflected in the list

#### Scenario: Delete an entry
- **WHEN** a user deletes an entry
- **THEN** it is removed via the API

### Requirement: Manage hierarchy links
The management page SHALL let the user set each child's parent — a category's type and a subcategory's category — when creating or editing it.

#### Scenario: Assign a category to a type
- **WHEN** a user creates or edits a category
- **THEN** the user can choose its parent type, and the choice is saved

#### Scenario: Assign a subcategory to a category
- **WHEN** a user creates or edits a subcategory
- **THEN** the user can choose its parent category, and the choice is saved

### Requirement: Blocked-deletion feedback
When the API refuses to delete a catalog entry that still has children or is referenced by records, the page SHALL surface that error to the user rather than failing silently.

#### Scenario: Deleting an in-use entry is explained
- **WHEN** a user attempts to delete a category that still has subcategories (or is used by records) and the API returns a conflict
- **THEN** the page shows a message explaining the entry cannot be deleted while it is in use
