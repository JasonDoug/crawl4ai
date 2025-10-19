# URL Discovery Service

Microservice for discovering and filtering URLs from HTML content.

## Features

- Extract all links from HTML
- Resolve relative URLs to absolute
- Categorize as internal/external
- Filter by regex patterns (include/exclude)
- Extract link text and title attributes

## API Endpoints

### Health Check
```
GET /health
```

### Discover URLs
```
POST /discover
```

**Request:**
```json
{
  "html": "<a href='/page'>Link</a>",
  "base_url": "https://example.com",
  "include_external": false,
  "url_pattern": "/blog/.*",
  "exclude_patterns": ["/admin/.*", ".*\\.pdf$"]
}
```

**Response:**
```json
{
  "internal": [
    {
      "href": "https://example.com/page",
      "text": "Link",
      "title": null,
      "is_external": false
    }
  ],
  "external": [],
  "total_count": 1,
  "internal_count": 1,
  "external_count": 0
}
```

## Running the Service

```bash
docker compose -f docker-compose.workspace.yml up url-discovery-service
```

Service runs on port **8007**.

## Use Cases

- Deep crawling link discovery
- Sitemap generation
- Link validation
- External link tracking
