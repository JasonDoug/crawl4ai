FROM python:3.11-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.5.0 /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./
COPY shared ./shared
COPY services/content-filter-service ./services/content-filter-service

RUN uv sync --frozen --no-dev --package content-filter-service

EXPOSE 8008

CMD ["uv", "run", "--package", "content-filter-service", "python", "-m", "content_filter_service.main"]
