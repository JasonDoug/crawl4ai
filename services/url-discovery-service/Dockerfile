FROM python:3.11-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.5.0 /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./
COPY shared ./shared
COPY services/url-discovery-service ./services/url-discovery-service

RUN uv sync --frozen --no-dev --package url-discovery-service

EXPOSE 8007

CMD ["uv", "run", "--package", "url-discovery-service", "python", "-m", "url_discovery_service.main"]
