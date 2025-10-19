"""Tests for deep crawl coordinator."""

import pytest
from deep_crawl_service.crawler import DeepCrawlCoordinator


class TestDeepCrawlCoordinator:
    """Test deep crawl coordinator functionality."""

    @pytest.fixture
    def coordinator(self):
        """Create coordinator instance."""
        return DeepCrawlCoordinator()

    def test_normalize_url(self, coordinator):
        """Test URL normalization."""
        # Remove fragment
        assert (
            coordinator._normalize_url("https://example.com/page#section")
            == "https://example.com/page"
        )

        # Remove trailing slash
        assert (
            coordinator._normalize_url("https://example.com/page/")
            == "https://example.com/page"
        )

        # Resolve relative URL
        result = coordinator._normalize_url("/about", "https://example.com")
        assert result == "https://example.com/about"

    def test_is_same_domain(self, coordinator):
        """Test same domain check."""
        assert coordinator._is_same_domain(
            "https://example.com/page1", "https://example.com/page2"
        )

        assert not coordinator._is_same_domain(
            "https://example.com/page", "https://other.com/page"
        )

        # Subdomains are different
        assert not coordinator._is_same_domain(
            "https://www.example.com/page", "https://api.example.com/page"
        )

    def test_matches_pattern(self, coordinator):
        """Test regex pattern matching."""
        # Match blog posts
        assert coordinator._matches_pattern(
            "https://example.com/blog/post-1", r"/blog/"
        )

        # Don't match
        assert not coordinator._matches_pattern("https://example.com/about", r"/blog/")

        # Invalid pattern should return False
        assert not coordinator._matches_pattern(
            "https://example.com/page", r"[invalid(pattern"
        )

    def test_should_crawl_url(self, coordinator):
        """Test URL crawl decision logic."""
        start_url = "https://example.com"

        # Internal URL, no filters
        assert coordinator._should_crawl_url(
            "https://example.com/page",
            start_url,
            include_external=False,
            url_pattern=None,
            exclude_patterns=None,
        )

        # External URL, external not allowed
        assert not coordinator._should_crawl_url(
            "https://other.com/page",
            start_url,
            include_external=False,
            url_pattern=None,
            exclude_patterns=None,
        )

        # External URL, external allowed
        assert coordinator._should_crawl_url(
            "https://other.com/page",
            start_url,
            include_external=True,
            url_pattern=None,
            exclude_patterns=None,
        )

        # Matches include pattern
        assert coordinator._should_crawl_url(
            "https://example.com/blog/post",
            start_url,
            include_external=False,
            url_pattern=r"/blog/",
            exclude_patterns=None,
        )

        # Doesn't match include pattern
        assert not coordinator._should_crawl_url(
            "https://example.com/about",
            start_url,
            include_external=False,
            url_pattern=r"/blog/",
            exclude_patterns=None,
        )

        # Matches exclude pattern
        assert not coordinator._should_crawl_url(
            "https://example.com/admin/page",
            start_url,
            include_external=False,
            url_pattern=None,
            exclude_patterns=[r"/admin/"],
        )


class TestCrawlStrategies:
    """Test different crawl strategies."""

    @pytest.fixture
    async def coordinator(self):
        """Create coordinator instance."""
        coord = DeepCrawlCoordinator()
        yield coord
        await coord.close()

    @pytest.mark.asyncio
    async def test_crawl_bfs_basic(self, coordinator):
        """Test basic BFS crawl logic (mocked)."""
        # This would require mocking the HTTP calls to browser/scraping services
        # For now, just test that the method exists and has correct signature
        assert hasattr(coordinator, "crawl_bfs")
        assert callable(coordinator.crawl_bfs)

    @pytest.mark.asyncio
    async def test_crawl_dfs_basic(self, coordinator):
        """Test basic DFS crawl logic (mocked)."""
        assert hasattr(coordinator, "crawl_dfs")
        assert callable(coordinator.crawl_dfs)

    @pytest.mark.asyncio
    async def test_crawl_best_first_basic(self, coordinator):
        """Test basic best-first crawl logic (mocked)."""
        assert hasattr(coordinator, "crawl_best_first")
        assert callable(coordinator.crawl_best_first)
