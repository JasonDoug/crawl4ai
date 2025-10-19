"""FastAPI application for content filtering service."""

import logging
from typing import List
import math

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from bs4 import BeautifulSoup

from shared.schemas.content_filter_schemas import (
    ContentFilterRequest,
    ContentFilterResponse,
    FilteredBlock,
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
    title="Content Filtering Service",
    description="Microservice for filtering and ranking content with BM25",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def calculate_bm25_score(query_terms: List[str], document_terms: List[str]) -> float:
    """Calculate BM25 score for a document given query terms.

    Simplified BM25 implementation without corpus statistics.

    Args:
        query_terms: List of query terms.
        document_terms: List of document terms.

    Returns:
        BM25 score.
    """
    k1 = 1.5  # Term frequency saturation parameter
    b = 0.75  # Length normalization parameter

    # Count term frequencies
    doc_term_freq = {}
    for term in document_terms:
        doc_term_freq[term] = doc_term_freq.get(term, 0) + 1

    # Average document length (simplified)
    avgdl = len(document_terms)
    doc_len = len(document_terms)

    score = 0.0
    for term in query_terms:
        if term in doc_term_freq:
            tf = doc_term_freq[term]
            # Simplified IDF (assuming single document)
            idf = 1.0
            # BM25 formula
            numerator = tf * (k1 + 1)
            denominator = tf + k1 * (1 - b + b * (doc_len / avgdl))
            score += idf * (numerator / denominator)

    return score


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="healthy", service="content-filter-service")


@app.post("/filter", response_model=ContentFilterResponse)
async def filter_content(request: ContentFilterRequest) -> ContentFilterResponse:
    """Filter and rank HTML content.

    Args:
        request: Content filter request.

    Returns:
        ContentFilterResponse with filtered blocks.

    Raises:
        HTTPException: If filtering fails.
    """
    try:
        logger.info(f"Filtering content (query: {request.query})")

        soup = BeautifulSoup(request.html, "lxml")

        # Remove excluded tags
        if request.exclude_tags:
            for tag in request.exclude_tags:
                for element in soup.find_all(tag):
                    element.decompose()

        # Get text blocks
        if request.keep_only_tags:
            # Only keep specified tags
            elements = []
            for tag in request.keep_only_tags:
                elements.extend(soup.find_all(tag))
        else:
            # Get common content tags
            content_tags = [
                "p",
                "h1",
                "h2",
                "h3",
                "h4",
                "h5",
                "h6",
                "li",
                "div",
                "article",
                "section",
            ]
            elements = soup.find_all(content_tags)

        # Process query for BM25
        query_terms = []
        if request.query:
            query_terms = request.query.lower().split()

        blocks = []
        for element in elements:
            text = element.get_text(strip=True)
            if not text:
                continue

            # Count words
            words = text.split()
            word_count = len(words)

            # Filter by word count
            if word_count < request.min_word_count:
                continue

            # Calculate score if query provided
            score = None
            if query_terms:
                doc_terms = [w.lower() for w in words]
                score = calculate_bm25_score(query_terms, doc_terms)

            block = FilteredBlock(
                text=text,
                html=str(element),
                score=score,
                word_count=word_count,
            )
            blocks.append(block)

        # Sort by score if query provided
        if query_terms:
            blocks.sort(key=lambda x: x.score or 0, reverse=True)

        total_words = sum(block.word_count for block in blocks)

        logger.info(f"Filtered to {len(blocks)} blocks ({total_words} words)")

        return ContentFilterResponse(
            blocks=blocks,
            total_blocks=len(blocks),
            total_words=total_words,
        )

    except Exception as e:
        logger.exception("Error in content filtering")
        raise HTTPException(
            status_code=500, detail=f"Content filtering failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "content_filter_service.main:app",
        host="0.0.0.0",
        port=8008,
        reload=True,
    )
