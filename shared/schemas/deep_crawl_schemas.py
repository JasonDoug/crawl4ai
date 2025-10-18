"""Schemas for deep crawling service."""

from typing import Dict, Any, Optional, List
from enum import Enum
from pydantic import BaseModel, Field


class CrawlStrategy(str, Enum):
    """Deep crawl strategy types."""

    BFS = "bfs"  # Breadth-First Search
    DFS = "dfs"  # Depth-First Search
    BEST_FIRST = "best_first"  # Best-First (priority-based)


class DeepCrawlRequest(BaseModel):
    """Request for deep crawling."""

    start_url: str = Field(..., description="Starting URL for the crawl")
    strategy: CrawlStrategy = Field(
        default=CrawlStrategy.BFS, description="Crawl strategy to use"
    )
    max_depth: int = Field(default=3, ge=1, le=10, description="Maximum depth to crawl")
    max_pages: int = Field(
        default=100, ge=1, le=1000, description="Maximum number of pages to crawl"
    )
    include_external: bool = Field(
        default=False, description="Whether to include external links"
    )
    url_pattern: Optional[str] = Field(
        default=None, description="Regex pattern for filtering URLs"
    )
    exclude_patterns: Optional[List[str]] = Field(
        default=None, description="List of regex patterns to exclude"
    )
    score_threshold: Optional[float] = Field(
        default=None, description="Minimum score threshold for URLs (best-first only)"
    )
    browser_config: Optional[Dict[str, Any]] = Field(
        default=None, description="Configuration for browser service"
    )
    scraping_config: Optional[Dict[str, Any]] = Field(
        default=None, description="Configuration for content scraping"
    )


class CrawlResultItem(BaseModel):
    """Single crawl result item."""

    url: str = Field(..., description="URL that was crawled")
    depth: int = Field(..., description="Depth level of this URL")
    parent_url: Optional[str] = Field(
        default=None, description="Parent URL that led to this URL"
    )
    success: bool = Field(..., description="Whether the crawl succeeded")
    status_code: Optional[int] = Field(default=None, description="HTTP status code")
    title: Optional[str] = Field(default=None, description="Page title")
    html: Optional[str] = Field(default=None, description="HTML content")
    markdown: Optional[str] = Field(default=None, description="Markdown content")
    links: Optional[Dict[str, List[Dict[str, str]]]] = Field(
        default=None, description="Extracted links (internal/external)"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional metadata"
    )
    error: Optional[str] = Field(
        default=None, description="Error message if crawl failed"
    )


class DeepCrawlResponse(BaseModel):
    """Response from deep crawling."""

    results: List[CrawlResultItem] = Field(..., description="List of crawl results")
    stats: Dict[str, Any] = Field(..., description="Crawl statistics")


class DeepCrawlStats(BaseModel):
    """Statistics for a deep crawl operation."""

    total_urls: int = Field(default=0, description="Total URLs discovered")
    crawled_urls: int = Field(default=0, description="URLs successfully crawled")
    failed_urls: int = Field(default=0, description="URLs that failed")
    skipped_urls: int = Field(default=0, description="URLs skipped by filters")
    max_depth_reached: int = Field(default=0, description="Maximum depth reached")
    duration_seconds: float = Field(default=0.0, description="Total crawl duration")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(default="healthy")
    service: str = Field(default="deep-crawl-service")
