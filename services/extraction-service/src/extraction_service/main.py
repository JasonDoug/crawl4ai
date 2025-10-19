"""FastAPI application for extraction service."""

import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from shared.schemas.extraction_schemas import (
    CSSExtractionRequest,
    XPathExtractionRequest,
    RegexExtractionRequest,
    ExtractionResponse,
    HealthResponse,
)
from .extractor import CSSExtractor, XPathExtractor, RegexExtractor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Extraction Service",
    description="Microservice for data extraction using CSS/XPath/Regex",
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


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="healthy", service="extraction-service")


@app.post("/extract/css", response_model=ExtractionResponse)
async def extract_css(request: CSSExtractionRequest) -> ExtractionResponse:
    """Extract data using CSS selectors.

    Args:
        request: CSS extraction request.

    Returns:
        ExtractionResponse with results.

    Raises:
        HTTPException: If extraction fails.
    """
    try:
        logger.info(f"Extracting with CSS selector: {request.selector}")

        results = CSSExtractor.extract(
            html_content=request.html,
            selector=request.selector,
            extract_text=request.extract_text,
            extract_html=request.extract_html,
            extract_attributes=request.extract_attributes,
        )

        logger.info(f"Extracted {len(results)} elements")

        return ExtractionResponse(
            results=results,
            count=len(results),
        )

    except Exception as e:
        logger.exception("Error in CSS extraction")
        raise HTTPException(status_code=500, detail=f"CSS extraction failed: {str(e)}")


@app.post("/extract/xpath", response_model=ExtractionResponse)
async def extract_xpath(request: XPathExtractionRequest) -> ExtractionResponse:
    """Extract data using XPath expressions.

    Args:
        request: XPath extraction request.

    Returns:
        ExtractionResponse with results.

    Raises:
        HTTPException: If extraction fails.
    """
    try:
        logger.info(f"Extracting with XPath: {request.xpath}")

        results = XPathExtractor.extract(
            html_content=request.html,
            xpath=request.xpath,
            extract_text=request.extract_text,
            extract_html=request.extract_html,
            extract_attributes=request.extract_attributes,
        )

        logger.info(f"Extracted {len(results)} elements")

        return ExtractionResponse(
            results=results,
            count=len(results),
        )

    except ValueError as e:
        logger.error(f"Invalid XPath: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Error in XPath extraction")
        raise HTTPException(
            status_code=500, detail=f"XPath extraction failed: {str(e)}"
        )


@app.post("/extract/regex", response_model=ExtractionResponse)
async def extract_regex(request: RegexExtractionRequest) -> ExtractionResponse:
    """Extract data using regular expressions.

    Args:
        request: Regex extraction request.

    Returns:
        ExtractionResponse with results.

    Raises:
        HTTPException: If extraction fails.
    """
    try:
        logger.info(f"Extracting with regex pattern: {request.pattern}")

        results = RegexExtractor.extract(
            text=request.text,
            pattern=request.pattern,
            group=request.group,
            flags=request.flags,
        )

        logger.info(f"Extracted {len(results)} matches")

        return ExtractionResponse(
            results=results,
            count=len(results),
        )

    except ValueError as e:
        logger.error(f"Invalid regex: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Error in regex extraction")
        raise HTTPException(
            status_code=500, detail=f"Regex extraction failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "extraction_service.main:app",
        host="0.0.0.0",
        port=8006,
        reload=True,
    )
