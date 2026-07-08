## ADDED Requirements

### Requirement: Domain application
The system SHALL provide a single Django application named `cashflow`, registered in `INSTALLED_APPS`, to host all domain models, serializers, views, and admin registrations for later capabilities.

#### Scenario: App is loaded by Django
- **WHEN** `python manage.py check` is run
- **THEN** the command completes with no errors
- **AND** the `cashflow` app is present in the installed applications

#### Scenario: App owns a migrations package
- **WHEN** the project is inspected
- **THEN** `cashflow` has a migrations package so later capabilities can add schema migrations

### Requirement: REST framework enabled with project defaults
The system SHALL enable Django REST Framework and provide project-level configuration under a `REST_FRAMEWORK` setting, including a default pagination class and a default renderer set that includes the browsable API for manual testing.

#### Scenario: DRF is installed and configured
- **WHEN** the project starts
- **THEN** `rest_framework` is present in `INSTALLED_APPS`
- **AND** `REST_FRAMEWORK` defines a default pagination class with a page size
- **AND** the default renderers include both JSON and the browsable API

### Requirement: API mounted under a namespaced root
The system SHALL mount a DRF router under the `/api/` URL prefix, alongside the existing `/admin/` route, so later capabilities register their viewsets onto it without further URLconf edits.

#### Scenario: API root responds
- **WHEN** a client requests `GET /api/`
- **THEN** the DRF router returns HTTP 200 with the API root document (an empty route set until capabilities register viewsets)

#### Scenario: Admin remains available
- **WHEN** a client requests `GET /admin/`
- **THEN** the Django admin login page is served

### Requirement: OpenAPI schema and interactive docs
The system SHALL generate an OpenAPI 3 schema for the API using drf-spectacular and serve interactive documentation, so the API is self-describing as capabilities register their endpoints.

#### Scenario: Schema document is served
- **WHEN** a client requests `GET /api/schema/`
- **THEN** a valid OpenAPI 3 document describing the currently registered endpoints is returned

#### Scenario: Interactive docs render
- **WHEN** a user opens the Swagger UI (and ReDoc) docs endpoint
- **THEN** the interactive API documentation renders, listing operations as capabilities register them (empty until then)

### Requirement: Precise monetary serialization
The system SHALL configure DRF so decimal values are serialized as fixed-precision strings rather than floats, preserving exact ruble amounts across the API.

#### Scenario: Decimal rendered as a precise string
- **WHEN** the API serializes a decimal-valued field
- **THEN** it is rendered as a fixed-precision string (e.g. `"1000.00"`), not a floating-point number

### Requirement: Automated test harness
The system SHALL provide a pytest-django configuration wiring the project settings, so later capabilities can add and run automated tests.

#### Scenario: Test suite runs against the project
- **WHEN** `pytest` is run from the repository root
- **THEN** it resolves the Django settings module, creates a test database, and completes with zero collection errors
