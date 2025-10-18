"""Tests for content scraper functionality."""

import pytest
from content_scraping_service.scraper import ContentScraper, ExtractionRule


@pytest.fixture
def scraper():
    """Create a content scraper instance."""
    return ContentScraper()


@pytest.fixture
def sample_html():
    """Sample HTML for testing."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Test Page</title>
        <meta name="description" content="Test description">
        <meta property="og:title" content="Test OG Title">
    </head>
    <body>
        <h1>Main Heading</h1>
        <h2>Subheading 1</h2>
        <p>This is a test paragraph with <a href="/link1">a link</a>.</p>
        <p>Another paragraph with <a href="https://example.com">external link</a>.</p>

        <img src="/image1.jpg" alt="Test Image 1">
        <img src="https://example.com/image2.jpg" alt="Test Image 2">

        <table>
            <thead>
                <tr><th>Name</th><th>Age</th></tr>
            </thead>
            <tbody>
                <tr><td>Alice</td><td>30</td></tr>
                <tr><td>Bob</td><td>25</td></tr>
            </tbody>
        </table>

        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": "Test Article"
        }
        </script>
    </body>
    </html>
    """


def test_extract_text(scraper, sample_html):
    """Test text extraction."""
    result = scraper.scrape(sample_html, clean_text=True)

    assert "text" in result
    assert "Main Heading" in result["text"]
    assert "test paragraph" in result["text"]


def test_extract_headings(scraper, sample_html):
    """Test heading extraction."""
    result = scraper.scrape(sample_html)

    assert "headings" in result
    assert len(result["headings"]) == 2
    assert result["headings"][0]["level"] == 1
    assert result["headings"][0]["text"] == "Main Heading"
    assert result["headings"][1]["level"] == 2
    assert result["headings"][1]["text"] == "Subheading 1"


def test_extract_links(scraper, sample_html):
    """Test link extraction."""
    result = scraper.scrape(
        sample_html, extract_links=True, base_url="https://example.com"
    )

    assert "links" in result
    assert len(result["links"]) >= 2
    assert any("link1" in link for link in result["links"])


def test_extract_images(scraper, sample_html):
    """Test image extraction."""
    result = scraper.scrape(
        sample_html, extract_images=True, base_url="https://example.com"
    )

    assert "images" in result
    assert len(result["images"]) == 2
    assert result["images"][0]["alt"] == "Test Image 1"


def test_extract_metadata(scraper, sample_html):
    """Test metadata extraction."""
    result = scraper.scrape(sample_html, extract_metadata=True)

    assert "metadata" in result
    assert result["metadata"]["title"] == "Test Page"
    assert result["metadata"]["description"] == "Test description"
    assert result["metadata"]["og:title"] == "Test OG Title"
    assert result["metadata"]["language"] == "en"


def test_extract_tables(scraper, sample_html):
    """Test table extraction."""
    result = scraper.scrape(sample_html, extract_tables=True)

    assert "tables" in result
    assert len(result["tables"]) == 1

    table = result["tables"][0]
    assert table["headers"] == ["Name", "Age"]
    assert len(table["rows"]) == 2
    assert table["rows"][0] == ["Alice", "30"]
    assert table["rows"][1] == ["Bob", "25"]


def test_extract_structured_data(scraper, sample_html):
    """Test structured data extraction."""
    result = scraper.scrape(sample_html, extract_structured_data=True)

    assert "structured_data" in result
    assert len(result["structured_data"]) >= 1

    json_ld = next(
        (item for item in result["structured_data"] if item["type"] == "json-ld"), None
    )
    assert json_ld is not None
    assert json_ld["data"]["@type"] == "Article"


def test_custom_extraction_rules(scraper, sample_html):
    """Test custom extraction rules."""
    rules = [
        ExtractionRule(
            name="all_paragraphs",
            selector=".//p",
            multiple=True,
        ),
        ExtractionRule(
            name="first_heading",
            selector=".//h1",
            multiple=False,
        ),
    ]

    result = scraper.scrape(sample_html, custom_rules=rules)

    assert "custom" in result
    assert "all_paragraphs" in result["custom"]
    assert len(result["custom"]["all_paragraphs"]) >= 2
    assert result["custom"]["first_heading"] == "Main Heading"


def test_error_handling(scraper):
    """Test error handling with invalid HTML."""
    invalid_html = "<html><body><unclosed tag"

    # Should not raise exception, but include error in result
    result = scraper.scrape(invalid_html)
    assert "text" in result or "error" in result


def test_empty_html(scraper):
    """Test handling of empty HTML."""
    result = scraper.scrape("")

    assert "text" in result
    assert result["text"] == ""


def test_url_resolution(scraper):
    """Test relative URL resolution."""
    html = '<html><body><a href="/test">Link</a></body></html>'

    result = scraper.scrape(html, extract_links=True, base_url="https://example.com")

    assert result["links"][0] == "https://example.com/test"
