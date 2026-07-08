FROM ghcr.io/astral-sh/uv:python3.14-alpine

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY . /app

RUN uv sync --frozen --no-dev

CMD ["gunicorn", "cash_flow_service.wsgi:application", "--bind", "0.0.0.0:8000"]
