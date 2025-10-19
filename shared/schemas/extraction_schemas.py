"""Schemas for extraction service."""

from typing import Dict, Any, Optional, List
from enum import Enum
from pydantic import BaseModel, Field


class ExtractionType(str, Enum):
    """Extraction strategy types."""

    CSS = "css"
    XPATH = "xpath"
    REGEX = "regex"


class CSSExtractionRequest(BaseModel):
    """Request for CSS selector extraction."""

    html: str = Field(..., description="HTML content to extract from")
    selector: str = Field(..., description="CSS selector")
    extract_text: bool = Field(default=True, description="Extract text content")
    extract_html: bool = Field(default=False, description="Extract raw HTML")
    extract_attributes: Optional[List[str]] = Field(
        default=None, description="List of attributes to extract"
    )


class XPathExtractionRequest(BaseModel):
    """Request for XPath extraction."""

    html: str = Field(..., description="HTML content to extract from")
    xpath: str = Field(..., description="XPath expression")
    extract_text: bool = Field(default=True, description="Extract text content")
    extract_html: bool = Field(default=False, description="Extract raw HTML")
    extract_attributes: Optional[List[str]] = Field(
        default=None, description="List of attributes to extract"
    )


class RegexExtractionRequest(BaseModel):
    """Request for regex extraction."""

    text: str = Field(..., description="Text content to extract from")
    pattern: str = Field(..., description="Regex pattern")
    group: Optional[int] = Field(
        default=None, description="Capture group to extract (None for all matches)"
    )
    flags: Optional[int] = Field(
        default=0, description="Regex flags (e.g., re.IGNORECASE)"
    )


class ExtractionResult(BaseModel):
    """Single extraction result."""

    text: Optional[str] = Field(default=None, description="Extracted text")
    html: Optional[str] = Field(default=None, description="Extracted HTML")
    attributes: Optional[Dict[str, str]] = Field(
        default=None, description="Extracted attributes"
    )


class ExtractionResponse(BaseModel):
    """Response from extraction."""

    results: List[ExtractionResult] = Field(
        ..., description="List of extraction results"
    )
    count: int = Field(..., description="Number of results")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(default="healthy")
    service: str = Field(default="extraction-service")
