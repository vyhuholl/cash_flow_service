## 1. Seed data

- [ ] 1.1 Add `cashflow/management/commands/seed_demo.py` using `get_or_create` for statuses, types, categories, subcategories (ТЗ examples)
- [ ] 1.2 Seed a few sample records spanning types/categories and dates
- [ ] 1.3 Make it idempotent (safe to re-run, no duplicates) and print a short summary

## 2. Containerization

- [ ] 2.1 Add a `Dockerfile` (`python:3.14-slim` + `uv sync --frozen`, copy project)
- [ ] 2.2 Add an entrypoint that runs `migrate` → `seed_demo` → serves the app on an exposed port
- [ ] 2.3 Add `.dockerignore` (`.venv`, caches, `db.sqlite3`)
- [ ] 2.4 (Optional) Add `docker-compose.yml` with a volume for `db.sqlite3` so data persists

## 3. README

- [ ] 3.1 Install section: `uv sync`, Python 3.14, note the nested `cash_flow_service/` working dir
- [ ] 3.2 Database section: `migrate`, `createsuperuser`, `seed_demo`
- [ ] 3.3 Run section (local `runserver` + Docker) with URLs for home, `/reference`, `/api/`, `/admin/`
- [ ] 3.4 Overview: domain model, `/api/` endpoints, and `pytest`/`ruff` commands
- [ ] 3.5 Add a screenshots / demo-link placeholder section

## 4. Verification

- [ ] 4.1 On a clean checkout, run the local path end-to-end and confirm a populated home page
- [ ] 4.2 Build and run the container; confirm migrate+seed+serve and a reachable home page (data persists across restarts with the volume)
- [ ] 4.3 Re-run `seed_demo` and confirm no duplicates
- [ ] 4.4 Run `pytest` and `ruff check`/`ruff format --check`
