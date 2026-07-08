## ADDED Requirements

### Requirement: Getting-started documentation
The `README.md` SHALL document how to install dependencies, set up the database, and run the service, so a reviewer can go from a fresh clone to a running app.

#### Scenario: Install, migrate, run
- **WHEN** a reviewer follows the README top to bottom on a fresh clone
- **THEN** it covers installing dependencies (`uv sync`, Python 3.14), applying migrations, creating an admin user, seeding demo data, and starting the server — with the exact commands

#### Scenario: Entry-point URLs are listed
- **WHEN** the reviewer reads the run section
- **THEN** it names the URLs for the home page, the reference-management page, the DRF browsable API, and the Django admin

### Requirement: Project and API overview
The README SHALL summarize the domain model and the available API endpoints, and explain how to run the tests and linters.

#### Scenario: Reviewer understands the surface
- **WHEN** the reviewer reads the overview
- **THEN** it describes the Status/Type/Category/Subcategory catalog and the record entity, lists the `/api/` endpoints, and gives the `pytest` and `ruff` commands

### Requirement: Reproducible seed data
The system SHALL provide a reproducible way to load demo data covering the ТЗ examples — statuses (Бизнес, Личное, Налог), types (Пополнение, Списание), categories Инфраструктура (VPS, Proxy) and Маркетинг (Farpost, Avito), and a few sample records — so the app is non-empty on first run.

#### Scenario: Seed populates the catalog and records
- **WHEN** a reviewer runs the documented seed step on an empty database
- **THEN** the example statuses, types, categories, subcategories, and sample records are created

#### Scenario: Seed is safe to re-run
- **WHEN** the seed step is run again
- **THEN** it does not create duplicates or error out

### Requirement: Containerized run path
The repository SHALL provide a `Dockerfile` (and optionally a `docker-compose.yml`) plus documented commands that build and run the app in a container, applying migrations and seed data and serving the web service, as an alternative to the local workflow.

#### Scenario: Run via container
- **WHEN** a reviewer follows the documented `docker build`/`docker run` (or `docker compose up`) steps
- **THEN** the service starts in a container, the database is migrated and seeded, and the home page is reachable on the documented port

### Requirement: Screenshots / demo placeholder
The README SHALL include a section for interface screenshots or a demo link (the optional ТЗ deliverable).

#### Scenario: Placeholder present
- **WHEN** the reviewer reaches the end of the README
- **THEN** a clearly marked screenshots/demo section is present to be filled in
