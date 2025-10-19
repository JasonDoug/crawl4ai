"""FastAPI application for URL discovery service."""

import logging
import re
from urllib.parse import urljoin, urlparse
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from bs4 import BeautifulSoup

from shared.schemas.url_discovery_schemas import (
    URLDiscoveryRequest,
    URLDiscoveryResponse,
    URLInfo,
    HealthResponse,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="URL Discovery Service",
    description="Microservice for discovering and filtering URLs from HTML",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def is_same_domain(url1: str, url2: str) -> bool:
    """Check if two URLs are from the same domain."""
    try:
        domain1 = urlparse(url1).netloc
        domain2 = urlparse(url2).netloc
        return domain1 == domain2
    except Exception:
        return False


def matches_pattern(url: str, pattern: str) -> bool:
    """Check if URL matches regex pattern."""
    try:
        return bool(re.search(pattern, url))
    except Exception as e:
        logger.warning(f"Invalid regex pattern: {pattern}, error: {e}")
        return False


def should_include_url(
    url: str,
    base_url: str,
    is_external: bool,
    include_external: bool,
    url_pattern: str = None,
    exclude_patterns: List[str] = None,
) -> bool:
    """Determine if a URL should be included."""
    # Check external filter
    if is_external and not include_external:
        return False

    # Check exclusion patterns
    if exclude_patterns:
        for pattern in exclude_patterns:
            if matches_pattern(url, pattern):
                return False

    # Check inclusion pattern
    if url_pattern:
        return matches_pattern(url, url_pattern)

    return True


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="healthy", service="url-discovery-service")


@app.post("/discover", response_model=URLDiscoveryResponse)
async def discover_urls(request: URLDiscoveryRequest) -> URLDiscoveryResponse:
    """Discover and filter URLs from HTML content.

    Args:
        request: URL discovery request.

    Returns:
        URLDiscoveryResponse with discovered URLs.

    Raises:
        HTTPException: If discovery fails.
    """
    try:
        logger.info(f"Discovering URLs from HTML (base: {request.base_url})")

        soup = BeautifulSoup(request.html, "lxml")
        links = soup.find_all("a", href=True)

        internal_urls = []
        external_urls = []

        for link in links:
            href = link.get("href", "").strip()
            if not href or href.startswith(("#", "javascript:", "mailto:")):
                continue

            # Resolve relative URLs
            absolute_url = urljoin(request.base_url, href)

            # Remove fragment
            absolute_url = absolute_url.split("#")[0]

            # Determine if external
            is_external = not is_same_domain(absolute_url, request.base_url)

            # Check if should include
            if not should_include_url(
                absolute_url,
                request.base_url,
                is_external,
                request.include_external,
                request.url_pattern,
                request.exclude_patterns,
            ):
                continue

            # Create URL info
            url_info = URLInfo(
                href=absolute_url,
                text=link.get_text(strip=True) or None,
                title=link.get("title") or None,
                is_external=is_external,
            )

            if is_external:
                external_urls.append(url_info)
            else:
                internal_urls.append(url_info)

        logger.info(
            f"Discovered {len(internal_urls)} internal, "
            f"{len(external_urls)} external URLs"
        )

        return URLDiscoveryResponse(
            internal=internal_urls,
            external=external_urls,
            total_count=len(internal_urls) + len(external_urls),
            internal_count=len(internal_urls),
            external_count=len(external_urls),
        )

    except Exception as e:
        logger.exception("Error in URL discovery")
        raise HTTPException(status_code=500, detail=f"URL discovery failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "url_discovery_service.main:app",
        host="0.0.0.0",
        port=8007,
        reload=True,
    )
