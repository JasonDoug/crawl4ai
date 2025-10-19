"""Schemas for content filtering service."""

from typing import List, Optional
from pydantic import BaseModel, Field


class ContentFilterRequest(BaseModel):
    """Request for content filtering."""

    html: str = Field(..., description="HTML content to filter")
    query: Optional[str] = Field(
        default=None, description="Query for relevance-based filtering (BM25)"
    )
    min_word_count: int = Field(
        default=10, ge=1, description="Minimum word count for text blocks"
    )
    exclude_tags: Optional[List[str]] = Field(
        default=None, description="HTML tags to exclude (e.g., ['script', 'style'])"
    )
    keep_only_tags: Optional[List[str]] = Field(
        default=None, description="Keep only these HTML tags (e.g., ['p', 'h1', 'h2'])"
    )


class FilteredBlock(BaseModel):
    """A filtered content block."""

    text: str = Field(..., description="Text content of the block")
    html: Optional[str] = Field(default=None, description="HTML content of the block")
    score: Optional[float] = Field(
        default=None, description="Relevance score (if query provided)"
    )
    word_count: int = Field(..., description="Number of words in the block")


class ContentFilterResponse(BaseModel):
    """Response from content filtering."""

    blocks: List[FilteredBlock] = Field(..., description="Filtered content blocks")
    total_blocks: int = Field(..., description="Total number of blocks")
    total_words: int = Field(..., description="Total word count")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(default="healthy")
    service: str = Field(default="content-filter-service")
