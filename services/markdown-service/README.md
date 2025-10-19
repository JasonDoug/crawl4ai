# Markdown Generation Service

Microservice for generating markdown from HTML content with citation support.

## Features

- Convert HTML to clean markdown
- Convert inline links to numbered citations with references section
- Customizable HTML2Text options
- Code block preservation
- Relative URL resolution

## API Endpoints

### Health Check
```http
GET /health
```

Returns service health status.

### Generate Markdown
```http
POST /generate
```

Generate markdown from HTML content.

**Request Body:**
```json
{
  "html": "<h1>Title</h1><p>Content with <a href='https://example.com'>link</a></p>",
  "base_url": "https://example.com",
  "citations": true,
  "html2text_options": {
    "body_width": 0,
    "ignore_emphasis": false
  }
}
```

**Response:**
```json
{
  "raw_markdown": "# Title\n\nContent with [link](https://example.com)",
  "markdown_with_citations": "# Title\n\nContent with link[1]",
  "references_markdown": "## References\n\n1. https://example.com",
  "fit_markdown": "",
  "fit_html": ""
}
```

## Running the Service

### With Docker Compose
```bash
docker compose -f docker-compose.workspace.yml up markdown-service
```

### Standalone
```bash
cd services/markdown-service
uv run python -m markdown_service.main
```

The service will be available at `http://localhost:8004`.

## Testing

```bash
cd services/markdown-service
uv run pytest
```

## Configuration

Environment variables:
- `LOG_LEVEL`: Logging level (default: INFO)

HTML2Text options can be passed per request via `html2text_options`:
- `body_width`: Text wrapping width (0 to disable)
- `ignore_emphasis`: Ignore emphasis tags
- `ignore_links`: Ignore links
- `ignore_images`: Ignore images
- `single_line_break`: Use single line breaks
- `mark_code`: Mark code blocks
- And more...

## Dependencies

- FastAPI: Web framework
- Pydantic: Data validation
- html2text: HTML to markdown conversion (from crawl4ai)
