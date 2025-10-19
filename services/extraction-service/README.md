# Extraction Service

Microservice for extracting data from HTML using CSS selectors, XPath, and regular expressions.

## Features

- **CSS Selectors**: Extract elements using CSS selectors
- **XPath**: Extract elements using XPath expressions  
- **Regex**: Extract patterns using regular expressions
- Extract text, HTML, and attributes
- Multiple extraction results per request

## API Endpoints

### Health Check
```
GET /health
```

### CSS Extraction
```
POST /extract/css
```

**Request:**
```json
{
  "html": "<div class='item'>Content</div>",
  "selector": ".item",
  "extract_text": true,
  "extract_html": false,
  "extract_attributes": ["class", "id"]
}
```

### XPath Extraction
```
POST /extract/xpath
```

**Request:**
```json
{
  "html": "<div class='item'>Content</div>",
  "xpath": "//div[@class='item']",
  "extract_text": true,
  "extract_html": false,
  "extract_attributes": ["class"]
}
```

### Regex Extraction
```
POST /extract/regex
```

**Request:**
```json
{
  "text": "Email: test@example.com",
  "pattern": "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}",
  "group": 0
}
```

## Running the Service

```bash
docker compose -f docker-compose.workspace.yml up extraction-service
```

Service runs on port **8006**.

## Dependencies

- BeautifulSoup4: CSS selector parsing
- lxml: XPath evaluation
