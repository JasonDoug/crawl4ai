"""Schemas for markdown generation service."""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class MarkdownGenerationRequest(BaseModel):
    """Request for markdown generation."""

    html: str = Field(..., description="HTML content to convert to markdown")
    base_url: str = Field(
        default="", description="Base URL for resolving relative links"
    )
    html2text_options: Optional[Dict[str, Any]] = Field(
        default=None, description="HTML2Text configuration options"
    )
    citations: bool = Field(
        default=True, description="Whether to generate citations from links"
    )
    content_filter_config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Configuration for content filtering (if fit markdown is needed)",
    )


class MarkdownGenerationResponse(BaseModel):
    """Response from markdown generation."""

    raw_markdown: str = Field(..., description="Raw markdown without citations")
    markdown_with_citations: str = Field(
        ..., description="Markdown with links converted to numbered citations"
    )
    references_markdown: str = Field(
        ..., description="References section with numbered URLs"
    )
    fit_markdown: str = Field(
        default="", description="Filtered markdown (only relevant content)"
    )
    fit_html: str = Field(
        default="", description="Filtered HTML used to generate fit markdown"
    )


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(default="healthy")
    service: str = Field(default="markdown-service")
