.PHONY: format lint type-check validate test makemigrations migrate

RUN_CMD := uv run

format: 
	$(RUN_CMD) ruff format .

lint:
	$(RUN_CMD) ruff check .

type-check:
	$(RUN_CMD) mypy .

validate: format lint type-check

test:
	$(RUN_CMD) pytest --cov=.

makemigrations:
	$(RUN_CMD) cash_flow_service/manage.py makemigrations ${MSG}

migrate:
	$(RUN_CMD) cash_flow_service/manage.py migrate
