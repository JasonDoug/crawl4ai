# Crawl4AI Microservices API Usage Guide

This guide provides detailed examples for using the Browser Management and Content Scraping microservices.

## Table of Contents

- [Browser Management Service](#browser-management-service)
  - [Basic Navigation](#basic-navigation)
  - [Session Management](#session-management)
  - [Advanced Navigation](#advanced-navigation)
- [Content Scraping Service](#content-scraping-service)
  - [Basic Scraping](#basic-scraping)
  - [Advanced Extraction](#advanced-extraction)
  - [Custom Extraction Rules](#custom-extraction-rules)

## Browser Management Service

The Browser Management Service runs on port 8001 and provides browser automation capabilities.

### Basic Navigation

**Endpoint:** `POST /api/v1/navigate`

#### Simple Page Load

```bash
curl -X POST http://localhost:8001/api/v1/navigate \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "action": "navigate",
    "timeout": 30
  }'
```

#### Get Page HTML

```bash
curl -X POST http://localhost:8001/api/v1/navigate \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "action": "get_html",
    "timeout": 30
  }'
```

**Response:**
```json
{
  "success": true,
  "url": "https://example.com",
  "html": "<!DOCTYPE html>...",
  "title": "Example Domain",
  "cookies": {},
  "metadata": {
    "viewport": {"width": 1280, "height": 720},
    "url": "https://example.com",
    "title": "Example Domain"
  },
  "duration_ms": 1234.56
}
```

#### Take Screenshot

```bash
curl -X POST http://localhost:8001/api/v1/navigate \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "action": "screenshot",
    "timeout": 30
  }'
```

**Response:**
```json
{
  "success": true,
  "url": "https://example.com",
  "screenshot": "base64-encoded-image-data...",
  "duration_ms": 2345.67
}
```

### Session Management

Sessions allow you to maintain browser context (cookies, localStorage, etc.) across multiple requests.

#### Create a Session

**Endpoint:** `POST /api/v1/sessions`

```bash
curl -X POST http://localhost:8001/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "user_agent": "MyBot/1.0",
    "viewport": {"width": 1920, "height": 1080},
    "locale": "en-US",
    "timezone": "America/New_York"
  }'
```

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Session created successfully"
}
```

#### Navigate with Session

```bash
curl -X POST http://localhost:8001/api/v1/navigate \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/login",
    "action": "get_html",
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "timeout": 30
  }'
```

#### Manage Session Cookies

**Add Cookies:**
```bash
curl -X POST http://localhost:8001/api/v1/sessions/{session_id}/cookies \
  -H "Content-Type: application/json" \
  -d '{
    "cookies": {
      "auth_token": "abc123",
      "user_id": "12345"
    },
    "url": "https://example.com"
  }'
```

**Get Cookies:**
```bash
curl -X GET http://localhost:8001/api/v1/sessions/{session_id}/cookies
```

**Response:**
```json
{
  "cookies": {
    "auth_token": "abc123",
    "user_id": "12345",
    "session": "xyz789"
  }
}
```

#### Close Session

**Endpoint:** `DELETE /api/v1/sessions/{session_id}`

```bash
curl -X DELETE http://localhost:8001/api/v1/sessions/{session_id}
```

### Advanced Navigation

#### Wait for Selector

```bash
curl -X POST http://localhost:8001/api/v1/navigate \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "action": "get_html",
    "wait_for_selector": "#content",
    "timeout": 30
  }'
```

#### Click Element and Get HTML

```bash
curl -X POST http://localhost:8001/api/v1/navigate \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "action": "click",
    "wait_for_selector": "button.load-more",
    "timeout": 30
  }'
```

#### Execute JavaScript

```bash
curl -X POST http://localhost:8001/api/v1/navigate \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "action": "execute_js",
    "javascript": "return document.title",
    "timeout": 30
  }'
```

**Response:**
```json
{
  "success": true,
  "url": "https://example.com",
  "html": "<!DOCTYPE html>...",
  "javascript_result": "Example Domain",
  "duration_ms": 1500.00
}
```

#### Scroll Page

```bash
curl -X POST http://localhost:8001/api/v1/navigate \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/long-page",
    "action": "scroll",
    "wait_time": 2.0,
    "timeout": 30
  }'
```

#### Custom Headers and User Agent

```bash
curl -X POST http://localhost:8001/api/v1/navigate \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://api.example.com/data",
    "action": "get_html",
    "user_agent": "MyBot/1.0 (+https://example.com/bot)",
    "headers": {
      "Authorization": "Bearer token123",
      "Accept-Language": "en-US"
    },
    "timeout": 30
  }'
```

### Service Status

**Endpoint:** `GET /api/v1/status`

```bash
curl http://localhost:8001/api/v1/status
```

**Response:**
```json
{
  "status": "running",
  "active_pages": 2,
  "active_sessions": 5,
  "version": "0.1.0"
}
```

## Content Scraping Service

The Content Scraping Service runs on port 8002 and provides HTML content extraction.

### Basic Scraping

**Endpoint:** `POST /api/v1/scrape`

#### Extract Text Only

```bash
curl -X POST http://localhost:8002/api/v1/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "html": "<html><body><h1>Hello</h1><p>World</p></body></html>",
    "clean_text": true
  }'
```

**Response:**
```json
{
  "success": true,
  "text": "Hello World",
  "headings": [
    {"level": 1, "text": "Hello", "id": null}
  ],
  "links": [],
  "images": [],
  "media": [],
  "tables": [],
  "structured_data": [],
  "metadata": {},
  "duration_ms": 12.34
}
```

#### Extract Everything

```bash
curl -X POST http://localhost:8002/api/v1/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "html": "...",
    "extract_links": true,
    "extract_images": true,
    "extract_media": true,
    "extract_metadata": true,
    "extract_tables": true,
    "extract_structured_data": true,
    "base_url": "https://example.com",
    "clean_text": true
  }'
```

### Advanced Extraction

#### Extract Links with Base URL

```bash
curl -X POST http://localhost:8002/api/v1/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "html": "<html><body><a href=\"/page\">Link</a></body></html>",
    "extract_links": true,
    "base_url": "https://example.com"
  }'
```

**Response:**
```json
{
  "success": true,
  "text": "Link",
  "links": ["https://example.com/page"],
  "duration_ms": 8.90
}
```

#### Extract Images with Metadata

```bash
curl -X POST http://localhost:8002/api/v1/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "html": "<img src=\"/photo.jpg\" alt=\"A photo\" title=\"My Photo\">",
    "extract_images": true,
    "base_url": "https://example.com"
  }'
```

**Response:**
```json
{
  "success": true,
  "images": [
    {
      "src": "https://example.com/photo.jpg",
      "alt": "A photo",
      "title": "My Photo"
    }
  ],
  "duration_ms": 10.23
}
```

#### Extract Table Data

```bash
curl -X POST http://localhost:8002/api/v1/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "html": "<table><thead><tr><th>Name</th><th>Age</th></tr></thead><tbody><tr><td>Alice</td><td>30</td></tr><tr><td>Bob</td><td>25</td></tr></tbody></table>",
    "extract_tables": true
  }'
```

**Response:**
```json
{
  "success": true,
  "tables": [
    {
      "index": 0,
      "headers": ["Name", "Age"],
      "rows": [
        ["Alice", "30"],
        ["Bob", "25"]
      ]
    }
  ],
  "duration_ms": 15.67
}
```

#### Extract Structured Data (JSON-LD)

```bash
curl -X POST http://localhost:8002/api/v1/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "html": "<script type=\"application/ld+json\">{\"@type\":\"Article\",\"headline\":\"Test\"}</script>",
    "extract_structured_data": true
  }'
```

**Response:**
```json
{
  "success": true,
  "structured_data": [
    {
      "type": "json-ld",
      "data": {
        "@type": "Article",
        "headline": "Test"
      }
    }
  ],
  "duration_ms": 18.45
}
```

#### Extract Metadata

```bash
curl -X POST http://localhost:8002/api/v1/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "html": "<html lang=\"en\"><head><title>My Page</title><meta name=\"description\" content=\"A description\"><meta property=\"og:title\" content=\"OG Title\"><link rel=\"canonical\" href=\"https://example.com/page\"></head></html>",
    "extract_metadata": true
  }'
```

**Response:**
```json
{
  "success": true,
  "metadata": {
    "title": "My Page",
    "description": "A description",
    "og:title": "OG Title",
    "canonical": "https://example.com/page",
    "language": "en"
  },
  "duration_ms": 9.12
}
```

### Custom Extraction Rules

Define custom CSS or XPath selectors to extract specific content.

#### Extract Specific Elements

```bash
curl -X POST http://localhost:8002/api/v1/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "html": "<div class=\"price\">$19.99</div><div class=\"stock\">In Stock</div>",
    "custom_rules": [
      {
        "name": "price",
        "selector": ".price",
        "multiple": false
      },
      {
        "name": "stock_status",
        "selector": ".stock",
        "multiple": false
      }
    ]
  }'
```

**Response:**
```json
{
  "success": true,
  "custom": {
    "price": "$19.99",
    "stock_status": "In Stock"
  },
  "duration_ms": 11.23
}
```

#### Extract Multiple Items

```bash
curl -X POST http://localhost:8002/api/v1/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "html": "<ul><li class=\"item\">Item 1</li><li class=\"item\">Item 2</li></ul>",
    "custom_rules": [
      {
        "name": "all_items",
        "selector": ".item",
        "multiple": true
      }
    ]
  }'
```

**Response:**
```json
{
  "success": true,
  "custom": {
    "all_items": ["Item 1", "Item 2"]
  },
  "duration_ms": 10.45
}
```

#### Extract Attributes

```bash
curl -X POST http://localhost:8002/api/v1/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "html": "<a href=\"/product/123\" class=\"product-link\" data-id=\"123\">Product</a>",
    "custom_rules": [
      {
        "name": "product_url",
        "selector": ".product-link",
        "attribute": "href",
        "multiple": false
      },
      {
        "name": "product_id",
        "selector": ".product-link",
        "attribute": "data-id",
        "multiple": false
      }
    ],
    "base_url": "https://example.com"
  }'
```

**Response:**
```json
{
  "success": true,
  "custom": {
    "product_url": "https://example.com/product/123",
    "product_id": "123"
  },
  "duration_ms": 13.56
}
```

#### XPath Selectors

```bash
curl -X POST http://localhost:8002/api/v1/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "html": "<div><span>Value 1</span><span>Value 2</span></div>",
    "custom_rules": [
      {
        "name": "spans",
        "selector": ".//span",
        "multiple": true
      }
    ]
  }'
```

**Response:**
```json
{
  "success": true,
  "custom": {
    "spans": ["Value 1", "Value 2"]
  },
  "duration_ms": 9.78
}
```

## Complete Workflow Example

Here's a complete example combining both services to scrape a webpage:

```python
import requests

# 1. Create a browser session
session_response = requests.post(
    "http://localhost:8001/api/v1/sessions",
    json={
        "user_agent": "MyBot/1.0",
        "viewport": {"width": 1920, "height": 1080}
    }
)
session_id = session_response.json()["session_id"]

# 2. Navigate to a page
nav_response = requests.post(
    "http://localhost:8001/api/v1/navigate",
    json={
        "url": "https://example.com/products",
        "action": "get_html",
        "session_id": session_id,
        "wait_for_selector": ".product-list",
        "timeout": 30
    }
)
html = nav_response.json()["html"]

# 3. Scrape the content
scrape_response = requests.post(
    "http://localhost:8002/api/v1/scrape",
    json={
        "html": html,
        "extract_links": True,
        "extract_images": True,
        "extract_tables": True,
        "custom_rules": [
            {
                "name": "product_names",
                "selector": ".product-name",
                "multiple": True
            },
            {
                "name": "prices",
                "selector": ".product-price",
                "multiple": True
            }
        ],
        "base_url": "https://example.com"
    }
)

data = scrape_response.json()
print(f"Found {len(data['custom']['product_names'])} products")

# 4. Clean up session
requests.delete(f"http://localhost:8001/api/v1/sessions/{session_id}")
```

## Error Handling

Both services return error information in the response:

```json
{
  "success": false,
  "error": "Navigation timeout: https://example.com",
  "duration_ms": 30000.00
}
```

Always check the `success` field before processing response data.

## Service Health Checks

**Browser Service:**
```bash
curl http://localhost:8001/health
```

**Content Scraping Service:**
```bash
curl http://localhost:8002/health
```

Both return:
```json
{
  "status": "healthy",
  "service": "browser-service" 
}
```
