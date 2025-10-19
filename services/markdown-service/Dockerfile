FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.5.0 /uv /usr/local/bin/uv

# Copy workspace files
COPY pyproject.toml uv.lock ./
COPY shared ./shared
COPY services/markdown-service ./services/markdown-service

# Install dependencies
RUN uv sync --frozen --no-dev --package markdown-service

# Expose port
EXPOSE 8004

# Run the service
CMD ["uv", "run", "--package", "markdown-service", "python", "-m", "markdown_service.main"]
