## Why

The ТЗ's expected deliverables explicitly include a clear run instruction ("Инструкция по запуску проекта": how to install dependencies, set up the database, and start the service), and "Документация" is a scored evaluation criterion. The current `README.md` is a one-line stub. Reviewers must be able to clone the repo and get a working, populated instance quickly.

## What Changes

- Rewrite `README.md` with a complete getting-started guide:
  - **Install dependencies** — `uv sync` (Python 3.14, per `.python-version`/`pyproject.toml`).
  - **Set up the database** — `manage.py migrate`; create an admin user (`createsuperuser`); load demo data.
  - **Run the service** — `manage.py runserver`, with the URLs of the главная страница, the reference-management page, the DRF browsable API, and the Django admin.
  - Overview of the domain model and the API endpoints; how to run tests/linters.
- Add **seed/demo data** so a fresh clone isn't empty: a fixtures file or a management command populating the example dictionaries from the ТЗ (statuses Бизнес/Личное/Налог; types Пополнение/Списание; categories Инфраструктура{VPS, Proxy}, Маркетинг{Farpost, Avito}) and a few sample records.
- Add a **containerized run** path: a `Dockerfile` (and optionally `docker-compose.yml`) plus documented `docker build`/`docker run` (or `compose up`) instructions that migrate, seed, and serve the app, as an alternative to the local `uv` workflow.
- Add a placeholder section for interface screenshots / demo link (optional deliverable).

## Capabilities

### New Capabilities
- `project-docs`: Getting-started documentation (install, DB setup, run, endpoints), a containerized run path (Dockerfile / compose), and reproducible seed/demo data for the example dictionaries and sample records.

### Modified Capabilities
<!-- None. -->

## Impact

- `README.md` — full rewrite.
- New fixtures file or seed management command in the `cashflow` app.
- New `Dockerfile` (+ optional `docker-compose.yml`, `.dockerignore`) at the repo root.
- Depends on: the app and its models existing, so this lands after `reference-catalog` and `cash-flow-records` (ideally last, once the frontend URLs are known).
- No production code behavior change beyond the seed command.
