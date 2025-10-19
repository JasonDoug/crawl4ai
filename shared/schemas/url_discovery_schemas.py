"""Schemas for URL discovery and filtering service."""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class URLDiscoveryRequest(BaseModel):
    """Request for URL discovery."""

    html: str = Field(..., description="HTML content to extract URLs from")
    base_url: str = Field(..., description="Base URL for resolving relative links")
    include_external: bool = Field(default=False, description="Include external links")
    url_pattern: Optional[str] = Field(
        default=None, description="Regex pattern for filtering URLs"
    )
    exclude_patterns: Optional[List[str]] = Field(
        default=None, description="List of regex patterns to exclude"
    )


class URLInfo(BaseModel):
    """Information about a discovered URL."""

    href: str = Field(..., description="The URL")
    text: Optional[str] = Field(default=None, description="Link text")
    title: Optional[str] = Field(default=None, description="Link title attribute")
    is_external: bool = Field(..., description="Whether the URL is external")


class URLDiscoveryResponse(BaseModel):
    """Response from URL discovery."""

    internal: List[URLInfo] = Field(..., description="Internal URLs")
    external: List[URLInfo] = Field(..., description="External URLs")
    total_count: int = Field(..., description="Total number of URLs found")
    internal_count: int = Field(..., description="Number of internal URLs")
    external_count: int = Field(..., description="Number of external URLs")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(default="healthy")
    service: str = Field(default="url-discovery-service")
