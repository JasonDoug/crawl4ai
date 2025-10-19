# Deep Crawling Service

Microservice for deep crawling with multiple strategies (BFS, DFS, Best-First).

## Features

- **BFS (Breadth-First Search)**: Crawl level by level
- **DFS (Depth-First Search)**: Crawl depth-first
- **Best-First Search**: Priority-based crawling (basic implementation)
- URL filtering with regex patterns
- External link inclusion/exclusion
- Configurable depth and page limits
- Coordinates with browser and content scraping services

## API Endpoints

### Health Check
```
GET /health
```

Returns service health status.

### Deep Crawl
```
POST /crawl
```

Perform deep crawling with the specified strategy.

**Request Body:**
```json
{
  "start_url": "https://example.com",
  "strategy": "bfs",
  "max_depth": 3,
  "max_pages": 100,
  "include_external": false,
  "url_pattern": "/blog/.*",
  "exclude_patterns": ["/admin/.*", "/private/.*"],
  "score_threshold": 0.5,
  "browser_config": {
    "wait_until": "networkidle"
  },
  "scraping_config": {
    "extract_links": true
  }
}
```

**Response:**
```json
{
  "results": [
    {
      "url": "https://example.com",
      "depth": 0,
      "parent_url": null,
      "success": true,
      "status_code": 200,
      "title": "Example Page",
      "html": "...",
      "markdown": "...",
      "links": {
        "internal": [...],
        "external": [...]
      },
      "metadata": {},
      "error": null
    }
  ],
  "stats": {
    "total_urls": 150,
    "crawled_urls": 100,
    "failed_urls": 5,
    "skipped_urls": 45,
    "max_depth_reached": 3,
    "duration_seconds": 45.2
  }
}
```

## Crawl Strategies

### BFS (Breadth-First Search)
Crawls all pages at depth N before moving to depth N+1. Good for discovering nearby pages.

### DFS (Depth-First Search)
Follows links deeply before backtracking. Good for exploring specific paths.

### Best-First Search
Prioritizes URLs based on scores (currently falls back to BFS, scoring not fully implemented).

## Running the Service

### With Docker Compose
```bash
docker compose -f docker-compose.workspace.yml up deep-crawl-service
```

### Standalone
```bash
cd services/deep-crawl-service
uv run python -m deep_crawl_service.main
```

The service will be available at `http://localhost:8005`.

## Testing

```bash
cd services/deep-crawl-service
uv run pytest
```

## Configuration

Environment variables:
- `LOG_LEVEL`: Logging level (default: INFO)

## Dependencies

This service depends on:
- **Browser Service** (port 8000): For page navigation
- **Content Scraping Service** (port 8002): For HTML extraction

## URL Filtering

### Include Pattern
Use `url_pattern` to only crawl URLs matching a regex:
```json
{
  "url_pattern": "/blog/.*"
}
```

### Exclude Patterns
Use `exclude_patterns` to skip URLs matching any regex:
```json
{
  "exclude_patterns": ["/admin/.*", "/private/.*", ".*\\.pdf$"]
}
```

### External Links
Set `include_external` to `true` to crawl external domains:
```json
{
  "include_external": true
}
```

## Limits

- `max_depth`: 1-10 (default: 3)
- `max_pages`: 1-1000 (default: 100)
