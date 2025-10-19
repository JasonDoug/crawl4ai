"""Deep crawl coordinator implementation."""

import asyncio
import re
import time
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse, urljoin
from collections import deque
import logging

import httpx

from shared.schemas.deep_crawl_schemas import (
    CrawlStrategy,
    CrawlResultItem,
    DeepCrawlStats,
)

logger = logging.getLogger(__name__)


class DeepCrawlCoordinator:
    """Coordinates deep crawling by orchestrating browser and scraping services."""

    def __init__(
        self,
        browser_service_url: str = "http://browser-service:8000",
        scraping_service_url: str = "http://content-scraping-service:8002",
    ):
        """Initialize deep crawl coordinator.

        Args:
            browser_service_url: URL of the browser service.
            scraping_service_url: URL of the content scraping service.
        """
        self.browser_service_url = browser_service_url
        self.scraping_service_url = scraping_service_url
        self.http_client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        """Close HTTP client."""
        await self.http_client.aclose()

    def _normalize_url(self, url: str, base_url: str = "") -> str:
        """Normalize URL for comparison.

        Args:
            url: URL to normalize.
            base_url: Base URL for resolving relative URLs.

        Returns:
            Normalized URL.
        """
        # Resolve relative URLs
        if base_url and not url.startswith(("http://", "https://")):
            url = urljoin(base_url, url)

        # Remove fragment
        url = url.split("#")[0]

        # Remove trailing slash
        if url.endswith("/"):
            url = url[:-1]

        return url

    def _is_same_domain(self, url1: str, url2: str) -> bool:
        """Check if two URLs are from the same domain.

        Args:
            url1: First URL.
            url2: Second URL.

        Returns:
            True if same domain, False otherwise.
        """
        try:
            domain1 = urlparse(url1).netloc
            domain2 = urlparse(url2).netloc
            return domain1 == domain2
        except Exception:
            return False

    def _matches_pattern(self, url: str, pattern: str) -> bool:
        """Check if URL matches regex pattern.

        Args:
            url: URL to check.
            pattern: Regex pattern.

        Returns:
            True if matches, False otherwise.
        """
        try:
            return bool(re.search(pattern, url))
        except Exception as e:
            logger.warning(f"Invalid regex pattern: {pattern}, error: {e}")
            return False

    def _should_crawl_url(
        self,
        url: str,
        start_url: str,
        include_external: bool,
        url_pattern: Optional[str],
        exclude_patterns: Optional[List[str]],
    ) -> bool:
        """Determine if a URL should be crawled.

        Args:
            url: URL to check.
            start_url: Starting URL of the crawl.
            include_external: Whether to include external links.
            url_pattern: Optional inclusion pattern.
            exclude_patterns: Optional exclusion patterns.

        Returns:
            True if URL should be crawled, False otherwise.
        """
        # Check if external
        if not include_external and not self._is_same_domain(url, start_url):
            return False

        # Check exclusion patterns
        if exclude_patterns:
            for pattern in exclude_patterns:
                if self._matches_pattern(url, pattern):
                    return False

        # Check inclusion pattern
        if url_pattern:
            return self._matches_pattern(url, url_pattern)

        return True

    async def _crawl_page(
        self,
        url: str,
        browser_config: Optional[Dict] = None,
        scraping_config: Optional[Dict] = None,
    ) -> CrawlResultItem:
        """Crawl a single page.

        Args:
            url: URL to crawl.
            browser_config: Browser configuration.
            scraping_config: Scraping configuration.

        Returns:
            CrawlResultItem with the result.
        """
        try:
            # Step 1: Navigate to URL using browser service
            payload = {**(browser_config or {}), "url": url}
            browser_response = await self.http_client.post(
                f"{self.browser_service_url}/navigate",
                json=payload,
            )
            browser_response.raise_for_status()
            browser_data = browser_response.json()

            if not browser_data.get("success"):
                return CrawlResultItem(
                    url=url,
                    depth=0,
                    success=False,
                    error=browser_data.get("error", "Browser navigation failed"),
                )

            html = browser_data.get("html", "")

            # Step 2: Scrape content
            scrape_payload = {**(scraping_config or {}), "html": html, "url": url}
            scrape_response = await self.http_client.post(
                f"{self.scraping_service_url}/scrape",
                json=scrape_payload,
            )
            scrape_response.raise_for_status()
            scrape_data = scrape_response.json()

            return CrawlResultItem(
                url=url,
                depth=0,  # Will be set by caller
                success=True,
                status_code=browser_data.get("status_code"),
                title=scrape_data.get("title"),
                html=html
                if scraping_config and scraping_config.get("include_html")
                else None,
                markdown=scrape_data.get("markdown"),
                links=scrape_data.get("links"),
                metadata=scrape_data.get("metadata"),
            )

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error crawling {url}: {e}")
            return CrawlResultItem(
                url=url,
                depth=0,
                success=False,
                status_code=e.response.status_code if e.response else None,
                error=f"HTTP {e.response.status_code}" if e.response else str(e),
            )
        except Exception as e:
            logger.exception(f"Error crawling {url}")
            return CrawlResultItem(
                url=url,
                depth=0,
                success=False,
                error=str(e),
            )

    async def crawl_bfs(
        self,
        start_url: str,
        max_depth: int,
        max_pages: int,
        include_external: bool,
        url_pattern: Optional[str],
        exclude_patterns: Optional[List[str]],
        browser_config: Optional[Dict],
        scraping_config: Optional[Dict],
    ) -> Tuple[List[CrawlResultItem], DeepCrawlStats]:
        """Perform breadth-first search crawl.

        Args:
            start_url: Starting URL.
            max_depth: Maximum crawl depth.
            max_pages: Maximum pages to crawl.
            include_external: Include external links.
            url_pattern: URL pattern filter.
            exclude_patterns: URL exclusion patterns.
            browser_config: Browser configuration.
            scraping_config: Scraping configuration.

        Returns:
            Tuple of (results list, stats).
        """
        start_time = time.time()
        visited: Set[str] = set()
        queue: deque = deque([(start_url, None, 0)])  # (url, parent, depth)
        results: List[CrawlResultItem] = []
        stats = DeepCrawlStats()

        while queue and len(results) < max_pages:
            url, parent_url, depth = queue.popleft()

            # Normalize URL
            normalized_url = self._normalize_url(url, start_url)

            # Skip if already visited
            if normalized_url in visited:
                continue

            visited.add(normalized_url)
            stats.total_urls += 1

            # Skip if depth exceeded
            if depth > max_depth:
                stats.skipped_urls += 1
                continue

            # Crawl the page
            result = await self._crawl_page(
                normalized_url,
                browser_config,
                scraping_config,
            )
            result.depth = depth
            result.parent_url = parent_url
            results.append(result)

            if result.success:
                stats.crawled_urls += 1
                stats.max_depth_reached = max(stats.max_depth_reached, depth)

                # Extract links if within depth limit
                if depth < max_depth and result.links:
                    internal_links = result.links.get("internal", [])
                    external_links = (
                        result.links.get("external", []) if include_external else []
                    )

                    for link in internal_links + external_links:
                        link_url = link.get("href")
                        if not link_url:
                            continue

                        link_url = self._normalize_url(link_url, normalized_url)

                        if link_url in visited:
                            continue

                        if self._should_crawl_url(
                            link_url,
                            start_url,
                            include_external,
                            url_pattern,
                            exclude_patterns,
                        ):
                            queue.append((link_url, normalized_url, depth + 1))
                        else:
                            stats.skipped_urls += 1
            else:
                stats.failed_urls += 1

        stats.duration_seconds = time.time() - start_time
        return results, stats

    async def crawl_dfs(
        self,
        start_url: str,
        max_depth: int,
        max_pages: int,
        include_external: bool,
        url_pattern: Optional[str],
        exclude_patterns: Optional[List[str]],
        browser_config: Optional[Dict],
        scraping_config: Optional[Dict],
    ) -> Tuple[List[CrawlResultItem], DeepCrawlStats]:
        """Perform depth-first search crawl.

        Similar to BFS but uses a stack (LIFO) instead of queue.
        """
        start_time = time.time()
        visited: Set[str] = set()
        stack: List = [(start_url, None, 0)]  # (url, parent, depth)
        results: List[CrawlResultItem] = []
        stats = DeepCrawlStats()

        while stack and len(results) < max_pages:
            url, parent_url, depth = stack.pop()  # LIFO

            normalized_url = self._normalize_url(url, start_url)

            if normalized_url in visited:
                continue

            visited.add(normalized_url)
            stats.total_urls += 1

            if depth > max_depth:
                stats.skipped_urls += 1
                continue

            result = await self._crawl_page(
                normalized_url,
                browser_config,
                scraping_config,
            )
            result.depth = depth
            result.parent_url = parent_url
            results.append(result)

            if result.success:
                stats.crawled_urls += 1
                stats.max_depth_reached = max(stats.max_depth_reached, depth)

                if depth < max_depth and result.links:
                    internal_links = result.links.get("internal", [])
                    external_links = (
                        result.links.get("external", []) if include_external else []
                    )

                    # Add in reverse order so first discovered is processed next
                    for link in reversed(internal_links + external_links):
                        link_url = link.get("href")
                        if not link_url:
                            continue

                        link_url = self._normalize_url(link_url, normalized_url)

                        if link_url in visited:
                            continue

                        if self._should_crawl_url(
                            link_url,
                            start_url,
                            include_external,
                            url_pattern,
                            exclude_patterns,
                        ):
                            stack.append((link_url, normalized_url, depth + 1))
                        else:
                            stats.skipped_urls += 1
            else:
                stats.failed_urls += 1

        stats.duration_seconds = time.time() - start_time
        return results, stats

    async def crawl_best_first(
        self,
        start_url: str,
        max_depth: int,
        max_pages: int,
        include_external: bool,
        url_pattern: Optional[str],
        exclude_patterns: Optional[List[str]],
        score_threshold: float,
        browser_config: Optional[Dict],
        scraping_config: Optional[Dict],
    ) -> Tuple[List[CrawlResultItem], DeepCrawlStats]:
        """Perform best-first search crawl with URL scoring.

        For simplicity, uses a basic scoring heuristic based on URL depth.
        In production, this could use ML-based scoring.
        """
        # For now, fall back to BFS since we don't have a scorer
        # In production, this would use priority queue with URL scores
        logger.info("Best-first crawl not fully implemented, using BFS")
        return await self.crawl_bfs(
            start_url,
            max_depth,
            max_pages,
            include_external,
            url_pattern,
            exclude_patterns,
            browser_config,
            scraping_config,
        )
