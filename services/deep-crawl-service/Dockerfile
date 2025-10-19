FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.5.0 /uv /usr/local/bin/uv

# Copy workspace files
COPY pyproject.toml uv.lock ./
COPY shared ./shared
COPY services/deep-crawl-service ./services/deep-crawl-service

# Install dependencies
RUN uv sync --frozen --no-dev --package deep-crawl-service

# Expose port
EXPOSE 8005

# Run the service
CMD ["uv", "run", "--package", "deep-crawl-service", "python", "-m", "deep_crawl_service.main"]
