"""FastAPI application for markdown generation service."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from shared.schemas.markdown_schemas import (
    MarkdownGenerationRequest,
    MarkdownGenerationResponse,
    HealthResponse,
)
from .generator import MarkdownGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# Global markdown generator instance
markdown_generator: MarkdownGenerator = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    global markdown_generator

    logger.info("Starting markdown generation service...")

    # Initialize markdown generator
    markdown_generator = MarkdownGenerator()

    logger.info("Markdown generation service started successfully")

    yield

    logger.info("Shutting down markdown generation service...")


# Create FastAPI app
app = FastAPI(
    title="Markdown Generation Service",
    description="Microservice for generating markdown from HTML content",
    version="0.1.0",
    lifespan=lifespan,
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
    return HealthResponse(status="healthy", service="markdown-service")


@app.post("/generate", response_model=MarkdownGenerationResponse)
async def generate_markdown(
    request: MarkdownGenerationRequest,
) -> MarkdownGenerationResponse:
    """Generate markdown from HTML content.

    Args:
        request: Markdown generation request.

    Returns:
        MarkdownGenerationResponse with generated markdown.

    Raises:
        HTTPException: If markdown generation fails.
    """
    try:
        logger.info(f"Generating markdown for {len(request.html)} bytes of HTML")

        # Generate markdown
        result = markdown_generator.generate_markdown(
            input_html=request.html,
            base_url=request.base_url,
            html2text_options=request.html2text_options,
            citations=request.citations,
            content_filter=None,  # Content filtering will be handled separately
        )

        logger.info("Markdown generation completed successfully")

        return MarkdownGenerationResponse(
            raw_markdown=result.raw_markdown,
            markdown_with_citations=result.markdown_with_citations,
            references_markdown=result.references_markdown,
            fit_markdown=result.fit_markdown,
            fit_html=result.fit_html,
        )

    except Exception as e:
        logger.exception("Error generating markdown")
        raise HTTPException(
            status_code=500, detail=f"Failed to generate markdown: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "markdown_service.main:app",
        host="0.0.0.0",
        port=8004,
        reload=True,
    )
