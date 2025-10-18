"""Content scraping service API endpoints."""

import time
from fastapi import APIRouter, HTTPException
from crawl4ai_schemas import ScrapingRequest, ScrapingResponse

from .scraper import ContentScraper, ExtractionRule

router = APIRouter(tags=["scraping"])
scraper = ContentScraper()


@router.post("/scrape", response_model=ScrapingResponse)
async def scrape(request: ScrapingRequest) -> ScrapingResponse:
    """Scrape content from HTML.

    Args:
        request: Scraping request with HTML and options

    Returns:
        Scraping response with extracted content

    Raises:
        HTTPException: If scraping fails
    """
    start_time = time.time()

    try:
        # Convert schema rules to scraper rules
        custom_rules = None
        if request.custom_rules:
            custom_rules = [
                ExtractionRule(
                    name=rule.name,
                    selector=rule.selector,
                    attribute=rule.attribute,
                    multiple=rule.multiple,
                )
                for rule in request.custom_rules
            ]

        result = scraper.scrape(
            html=request.html,
            extract_links=request.extract_links,
            extract_images=request.extract_images,
            extract_media=request.extract_media,
            extract_metadata=request.extract_metadata,
            extract_tables=request.extract_tables,
            extract_structured_data=request.extract_structured_data,
            custom_rules=custom_rules,
            base_url=request.base_url,
            clean_text=request.clean_text,
        )

        duration_ms = (time.time() - start_time) * 1000

        return ScrapingResponse(
            success="error" not in result,
            text=result.get("text"),
            headings=result.get("headings", []),
            links=result.get("links", []),
            images=result.get("images", []),
            media=result.get("media", []),
            tables=result.get("tables", []),
            structured_data=result.get("structured_data", []),
            custom=result.get("custom"),
            metadata=result.get("metadata", {}),
            error=result.get("error"),
            duration_ms=duration_ms,
        )

    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        return ScrapingResponse(
            success=False,
            error=str(e),
            duration_ms=duration_ms,
        )


@router.get("/status")
async def status():
    """Get scraping service status.

    Returns:
        Service status information
    """
    return {
        "status": "running",
        "version": "0.1.0",
    }
