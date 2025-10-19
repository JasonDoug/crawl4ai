# Content Filtering Service

Microservice for filtering and ranking HTML content using BM25 and pruning strategies.

## Features

- Filter content by word count
- BM25 relevance scoring (query-based)
- Tag-based filtering (include/exclude)
- Extract meaningful text blocks
- Sort by relevance score

## API Endpoints

### Health Check
```
GET /health
```

### Filter Content
```
POST /filter
```

**Request:**
```json
{
  "html": "<p>Short text</p><p>This is a longer paragraph with more content about Python programming.</p>",
  "query": "python programming",
  "min_word_count": 5,
  "exclude_tags": ["script", "style"],
  "keep_only_tags": ["p", "h1", "h2"]
}
```

**Response:**
```json
{
  "blocks": [
    {
      "text": "This is a longer paragraph with more content about Python programming.",
      "html": "<p>This is a longer paragraph...</p>",
      "score": 2.5,
      "word_count": 11
    }
  ],
  "total_blocks": 1,
  "total_words": 11
}
```

## Running the Service

```bash
docker compose -f docker-compose.workspace.yml up content-filter-service
```

Service runs on port **8008**.

## Use Cases

- Extract main content from noisy HTML
- Find relevant text blocks for a query
- Remove boilerplate and navigation
- Generate clean text summaries

## BM25 Scoring

When a `query` is provided, blocks are ranked by BM25 relevance score. Higher scores indicate better matches to the query terms.
