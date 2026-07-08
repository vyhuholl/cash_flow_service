## Context

The ТЗ's deliverables include a clear run instruction and score "Документация" explicitly; the current `README.md` is a one-line stub. Reviewers need to clone and get a working, populated instance fast, ideally with a containerized option (a `Dockerfile` is being introduced). This change lands last, once the app, models, API, frontend, and their URLs exist, so the docs describe the real surface.

## Goals / Non-Goals

**Goals:**
- A complete README: install (`uv`), DB setup (migrate, superuser, seed), run, entry-point URLs, model/API overview, tests/linters.
- Reproducible, idempotent seed data matching the ТЗ examples.
- A container path (Dockerfile + optional compose) that migrates, seeds, and serves.
- A screenshots/demo placeholder.

**Non-Goals:**
- Production deployment/orchestration (K8s, CI/CD, TLS) — out of scope.
- New product features — this change is docs + seed + container packaging only.

## Decisions

- **Seed via a management command `seed_demo` (idempotent), not a raw fixture.** `get_or_create` on each dictionary/record makes re-runs safe and lets it build the Type→Category→Subcategory FKs in order; documented as `python manage.py seed_demo`. *Alternative:* a `loaddata` JSON fixture — brittle with hard-coded PKs and not idempotent; rejected.
- **`Dockerfile` on `python:3.14-slim` using `uv`.** Copy `pyproject.toml`/`uv.lock`, `uv sync --frozen`, copy the project; an entrypoint runs `migrate` → `seed_demo` → server. Expose the app port. *Alternative:* full `python:3.14` image — larger for no benefit.
- **Serve with `runserver` in the container for the test task** (simple, matches "run the service"), noting gunicorn as the production step. Keeping SQLite means the DB file lives in the image/volume; document a volume mount so data persists across runs. *Alternative:* bundle Postgres via compose — offered as the optional `docker-compose.yml` but not required, since the ТЗ permits SQLite.
- **`.dockerignore`** excludes `.venv`, caches, `db.sqlite3`, and the PDF to keep the build context small.
- **Vendored Bootstrap/static** (decided in `web-frontend`) means the container needs no external network at runtime — call this out so the Docker run works offline.
- **README is bilingual-friendly**: commands in English, oriented to the Russian-domain reviewer; note the nested `cash_flow_service/` working directory for `manage.py`.

## Risks / Trade-offs

- **SQLite in a container is ephemeral** → document a named volume (or bind mount) for `db.sqlite3` so seeded data survives `docker run` restarts.
- **`runserver` is not for production** → explicitly labelled; acceptable for a review/demo.
- **Seed idempotency depends on stable natural keys** → key `get_or_create` on `name` (+ parent) so re-runs match existing rows.
- **Docs drift from code** → write the README last and verify every command against the actual app before finishing.

## Migration Plan

1. Add `cashflow/management/commands/seed_demo.py` (idempotent; catalog + sample records).
2. Add `Dockerfile`, `.dockerignore`, and optionally `docker-compose.yml`; add an entrypoint that migrates + seeds + serves.
3. Rewrite `README.md`: install, DB setup + seed, local run, Docker run, URLs, model/API overview, tests/linters, screenshots/demo placeholder.
4. Verify end-to-end on a clean checkout: local path and container path both reach a populated home page; run `pytest`/`ruff`.

Rollback: revert `README.md` and remove the seed command, Dockerfile, and compose/ignore files.

## Open Questions

- Include a `docker-compose.yml` with Postgres, or keep SQLite-only? Default to SQLite + an optional compose file; revisit only if the reviewer wants Postgres.
