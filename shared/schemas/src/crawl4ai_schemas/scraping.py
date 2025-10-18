"""Content scraping service API schemas."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ExtractionRuleSchema(BaseModel):
    """Custom extraction rule."""

    name: str = Field(description="Name of the extracted field")
    selector: str = Field(description="CSS or XPath selector")
    attribute: Optional[str] = Field(
        default=None, description="Attribute to extract (None for text)"
    )
    multiple: bool = Field(default=False, description="Extract multiple elements")


class ScrapingRequest(BaseModel):
    """Request to content scraping service."""

    html: str = Field(description="HTML content to scrape")
    extract_links: bool = Field(default=False, description="Extract all links")
    extract_images: bool = Field(default=False, description="Extract all images")
    extract_media: bool = Field(default=False, description="Extract media elements")
    extract_metadata: bool = Field(default=False, description="Extract page metadata")
    extract_tables: bool = Field(default=False, description="Extract table data")
    extract_structured_data: bool = Field(
        default=False, description="Extract JSON-LD and schema.org data"
    )
    custom_rules: Optional[List[ExtractionRuleSchema]] = Field(
        default=None, description="Custom extraction rules"
    )
    base_url: Optional[str] = Field(
        default=None, description="Base URL for relative links"
    )
    clean_text: bool = Field(default=True, description="Clean extracted text")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class ScrapingResponse(BaseModel):
    """Response from content scraping service."""

    success: bool = Field(description="Whether scraping was successful")
    text: Optional[str] = Field(default=None, description="Extracted plain text")
    headings: List[Dict[str, Any]] = Field(
        default_factory=list, description="Extracted headings structure"
    )
    links: List[str] = Field(default_factory=list, description="Extracted links")
    images: List[Dict[str, str]] = Field(
        default_factory=list, description="Extracted images with metadata"
    )
    media: List[Dict[str, str]] = Field(
        default_factory=list, description="Extracted media elements"
    )
    tables: List[Dict[str, Any]] = Field(
        default_factory=list, description="Extracted tables with headers and rows"
    )
    structured_data: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Extracted structured data (JSON-LD, Microdata)",
    )
    custom: Optional[Dict[str, Any]] = Field(
        default=None, description="Custom extracted data"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Page metadata")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    duration_ms: float = Field(description="Processing duration in milliseconds")
