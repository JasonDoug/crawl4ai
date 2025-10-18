"""FastAPI application for deep crawling service."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from shared.schemas.deep_crawl_schemas import (
    DeepCrawlRequest,
    DeepCrawlResponse,
    CrawlStrategy,
    HealthResponse,
)
from .crawler import DeepCrawlCoordinator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# Global coordinator instance
coordinator: DeepCrawlCoordinator = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    global coordinator

    logger.info("Starting deep crawl service...")

    # Initialize coordinator
    coordinator = DeepCrawlCoordinator()

    logger.info("Deep crawl service started successfully")

    yield

    logger.info("Shutting down deep crawl service...")
    await coordinator.close()


# Create FastAPI app
app = FastAPI(
    title="Deep Crawling Service",
    description="Microservice for deep crawling with BFS/DFS/Best-First strategies",
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
    return HealthResponse(status="healthy", service="deep-crawl-service")


@app.post("/crawl", response_model=DeepCrawlResponse)
async def deep_crawl(request: DeepCrawlRequest) -> DeepCrawlResponse:
    """Perform deep crawling with the specified strategy.

    Args:
        request: Deep crawl request.

    Returns:
        DeepCrawlResponse with results and statistics.

    Raises:
        HTTPException: If crawl fails.
    """
    try:
        logger.info(
            f"Starting {request.strategy} crawl from {request.start_url} "
            f"(max_depth={request.max_depth}, max_pages={request.max_pages})"
        )

        # Select crawl strategy
        if request.strategy == CrawlStrategy.BFS:
            results, stats = await coordinator.crawl_bfs(
                start_url=request.start_url,
                max_depth=request.max_depth,
                max_pages=request.max_pages,
                include_external=request.include_external,
                url_pattern=request.url_pattern,
                exclude_patterns=request.exclude_patterns,
                browser_config=request.browser_config,
                scraping_config=request.scraping_config,
            )
        elif request.strategy == CrawlStrategy.DFS:
            results, stats = await coordinator.crawl_dfs(
                start_url=request.start_url,
                max_depth=request.max_depth,
                max_pages=request.max_pages,
                include_external=request.include_external,
                url_pattern=request.url_pattern,
                exclude_patterns=request.exclude_patterns,
                browser_config=request.browser_config,
                scraping_config=request.scraping_config,
            )
        elif request.strategy == CrawlStrategy.BEST_FIRST:
            results, stats = await coordinator.crawl_best_first(
                start_url=request.start_url,
                max_depth=request.max_depth,
                max_pages=request.max_pages,
                include_external=request.include_external,
                url_pattern=request.url_pattern,
                exclude_patterns=request.exclude_patterns,
                score_threshold=request.score_threshold or 0.0,
                browser_config=request.browser_config,
                scraping_config=request.scraping_config,
            )
        else:
            raise HTTPException(
                status_code=400, detail=f"Unknown strategy: {request.strategy}"
            )

        logger.info(
            f"Crawl completed: {stats.crawled_urls} pages crawled, "
            f"{stats.failed_urls} failed, {stats.skipped_urls} skipped "
            f"in {stats.duration_seconds:.2f}s"
        )

        return DeepCrawlResponse(
            results=results,
            stats=stats.model_dump(),
        )

    except Exception as e:
        logger.exception("Error during deep crawl")
        raise HTTPException(status_code=500, detail=f"Deep crawl failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "deep_crawl_service.main:app",
        host="0.0.0.0",
        port=8005,
        reload=True,
    )
