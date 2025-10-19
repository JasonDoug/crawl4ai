"""Tests for markdown service API."""

import pytest
from fastapi.testclient import TestClient
from markdown_service.main import app


class TestMarkdownAPI:
    """Test markdown service API endpoints."""

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
        assert data["service"] == "markdown-service"

    def test_generate_markdown_basic(self, client):
        """Test basic markdown generation."""
        request_data = {
            "html": "<h1>Test</h1><p>Content</p>",
            "base_url": "",
            "citations": False,
        }

        response = client.post("/generate", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert "raw_markdown" in data
        assert "markdown_with_citations" in data
        assert "references_markdown" in data
        assert "Test" in data["raw_markdown"]
        assert "Content" in data["raw_markdown"]

    def test_generate_markdown_with_citations(self, client):
        """Test markdown generation with citations."""
        request_data = {
            "html": '<p>Visit <a href="https://example.com">example</a></p>',
            "base_url": "",
            "citations": True,
        }

        response = client.post("/generate", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert "[1]" in data["markdown_with_citations"]
        assert "## References" in data["references_markdown"]
        assert "https://example.com" in data["references_markdown"]

    def test_generate_markdown_with_base_url(self, client):
        """Test markdown generation with base URL."""
        request_data = {
            "html": '<a href="/page">Link</a>',
            "base_url": "https://example.com",
            "citations": True,
        }

        response = client.post("/generate", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # URL should be resolved
        assert "https://example.com/page" in data["references_markdown"]

    def test_generate_markdown_with_options(self, client):
        """Test markdown generation with html2text options."""
        request_data = {
            "html": "<em>emphasis</em>",
            "html2text_options": {
                "ignore_emphasis": True,
                "body_width": 0,
            },
            "citations": False,
        }

        response = client.post("/generate", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "raw_markdown" in data

    def test_generate_markdown_empty_html(self, client):
        """Test handling of empty HTML."""
        request_data = {
            "html": "",
            "citations": False,
        }

        response = client.post("/generate", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["raw_markdown"] == ""

    def test_generate_markdown_invalid_request(self, client):
        """Test handling of invalid request."""
        # Missing required field
        request_data = {
            "base_url": "https://example.com",
        }

        response = client.post("/generate", json=request_data)

        # Should return validation error
        assert response.status_code == 422
