#!/bin/sh
set -e

# Django project directory (nested, as copied in Dockerfile)
PROJECT_DIR="/app/cash_flow_service"

cd "$PROJECT_DIR"

echo "Running database migrations..."
uv run manage.py migrate --noinput

echo "Collecting static files..."
uv run manage.py collectstatic --noinput --clear

echo "Seeding demo data..."
uv run manage.py seed_demo

echo "Starting Gunicorn..."
exec uv run gunicorn cash_flow_service.wsgi:application --bind 0.0.0.0:8000
