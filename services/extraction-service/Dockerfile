FROM python:3.11-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./
COPY shared ./shared
COPY services/extraction-service ./services/extraction-service

RUN uv sync --frozen --no-dev --package extraction-service

EXPOSE 8006

CMD ["uv", "run", "--package", "extraction-service", "python", "-m", "extraction_service.main"]
