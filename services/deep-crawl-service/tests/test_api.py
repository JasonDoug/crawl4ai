"""Tests for deep crawl service API."""

import pytest
from fastapi.testclient import TestClient
from deep_crawl_service.main import app


class TestDeepCrawlAPI:
    """Test deep crawl service API endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "deep-crawl-service"

    def test_deep_crawl_request_validation(self, client):
        """Test request validation."""
        # Missing required field
        response = client.post("/crawl", json={})
        assert response.status_code == 422

        # Invalid strategy
        response = client.post(
            "/crawl",
            json={
                "start_url": "https://example.com",
                "strategy": "invalid",
            },
        )
        assert response.status_code == 422

        # Invalid max_depth (too high)
        response = client.post(
            "/crawl",
            json={
                "start_url": "https://example.com",
                "max_depth": 100,
            },
        )
        assert response.status_code == 422

        # Invalid max_pages (too low)
        response = client.post(
            "/crawl",
            json={
                "start_url": "https://example.com",
                "max_pages": 0,
            },
        )
        assert response.status_code == 422

    def test_deep_crawl_valid_request_structure(self, client):
        """Test that valid request structure is accepted (will fail without services)."""
        request_data = {
            "start_url": "https://example.com",
            "strategy": "bfs",
            "max_depth": 2,
            "max_pages": 10,
            "include_external": False,
        }

        # This will fail because browser/scraping services aren't running
        # but we're testing that the request structure is valid
        response = client.post("/crawl", json=request_data)

        # Expect 500 (service unavailable) not 422 (validation error)
        assert response.status_code == 500

    def test_deep_crawl_with_filters(self, client):
        """Test deep crawl with URL filters."""
        request_data = {
            "start_url": "https://example.com",
            "strategy": "bfs",
            "max_depth": 2,
            "max_pages": 10,
            "url_pattern": r"/blog/",
            "exclude_patterns": [r"/admin/", r"/private/"],
        }

        # Will fail without services but validates request structure
        response = client.post("/crawl", json=request_data)
        assert response.status_code == 500

    def test_deep_crawl_dfs_strategy(self, client):
        """Test DFS strategy request."""
        request_data = {
            "start_url": "https://example.com",
            "strategy": "dfs",
            "max_depth": 3,
            "max_pages": 20,
        }

        response = client.post("/crawl", json=request_data)
        assert response.status_code == 500

    def test_deep_crawl_best_first_strategy(self, client):
        """Test best-first strategy request."""
        request_data = {
            "start_url": "https://example.com",
            "strategy": "best_first",
            "max_depth": 2,
            "max_pages": 15,
            "score_threshold": 0.5,
        }

        response = client.post("/crawl", json=request_data)
        assert response.status_code == 500
