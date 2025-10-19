"""Tests for markdown generator."""

import pytest
from markdown_service.generator import MarkdownGenerator, MarkdownGenerationResult


class TestMarkdownGenerator:
    """Test markdown generator functionality."""

    @pytest.fixture
    def generator(self):
        """Create markdown generator instance."""
        return MarkdownGenerator()

    def test_basic_markdown_generation(self, generator):
        """Test basic HTML to markdown conversion."""
        html = "<h1>Hello World</h1><p>This is a test.</p>"

        result = generator.generate_markdown(html)

        assert isinstance(result, MarkdownGenerationResult)
        assert "Hello World" in result.raw_markdown
        assert "This is a test" in result.raw_markdown

    def test_markdown_with_links(self, generator):
        """Test markdown generation with links."""
        html = '<p>Check out <a href="https://example.com">this link</a>.</p>'

        result = generator.generate_markdown(html, citations=False)

        assert "this link" in result.raw_markdown
        assert "https://example.com" in result.raw_markdown

    def test_citations_generation(self, generator):
        """Test link to citation conversion."""
        html = """
        <p>Visit <a href="https://example.com">example</a> and
        <a href="https://test.com">test</a>.</p>
        """

        result = generator.generate_markdown(html, citations=True)

        # Should have citations
        assert "[1]" in result.markdown_with_citations
        assert "[2]" in result.markdown_with_citations

        # Should have references
        assert "## References" in result.references_markdown
        assert "https://example.com" in result.references_markdown
        assert "https://test.com" in result.references_markdown

    def test_code_block_handling(self, generator):
        """Test code block conversion."""
        html = "<pre><code>def hello():\n    print('world')</code></pre>"

        result = generator.generate_markdown(html)

        assert "```" in result.raw_markdown
        assert "hello()" in result.raw_markdown

    def test_empty_html(self, generator):
        """Test handling of empty HTML."""
        result = generator.generate_markdown("")

        assert result.raw_markdown == ""
        assert result.markdown_with_citations == ""

    def test_relative_url_resolution(self, generator):
        """Test relative URL resolution in citations."""
        html = '<a href="/page">Link</a>'
        base_url = "https://example.com"

        result = generator.generate_markdown(html, base_url=base_url, citations=True)

        assert "https://example.com/page" in result.references_markdown

    def test_duplicate_links(self, generator):
        """Test that duplicate links get same citation number."""
        html = """
        <p><a href="https://example.com">first</a> and
        <a href="https://example.com">second</a></p>
        """

        result = generator.generate_markdown(html, citations=True)

        # Both should reference [1]
        assert result.markdown_with_citations.count("[1]") == 2
        # Only one reference entry
        assert result.references_markdown.count("https://example.com") == 1

    def test_html2text_options(self, generator):
        """Test custom html2text options."""
        html = "<em>emphasis</em>"

        # Default behavior
        result1 = generator.generate_markdown(html)

        # Ignore emphasis
        result2 = generator.generate_markdown(
            html, html2text_options={"ignore_emphasis": True}
        )

        # Results should differ based on options
        assert result1.raw_markdown != result2.raw_markdown

    def test_error_handling(self, generator):
        """Test error handling for invalid input."""
        # Should not raise exception, return error message
        result = generator.generate_markdown(None)

        assert isinstance(result, MarkdownGenerationResult)
        # Should handle gracefully


class TestConvertLinksToCitations:
    """Test link to citation conversion."""

    @pytest.fixture
    def generator(self):
        """Create markdown generator instance."""
        return MarkdownGenerator()

    def test_simple_link_conversion(self, generator):
        """Test simple link conversion."""
        markdown = "[example](https://example.com)"

        md_with_citations, references = generator.convert_links_to_citations(markdown)

        assert "example[1]" in md_with_citations
        assert "1. https://example.com" in references

    def test_multiple_links(self, generator):
        """Test multiple link conversion."""
        markdown = "[first](https://first.com) and [second](https://second.com)"

        md_with_citations, references = generator.convert_links_to_citations(markdown)

        assert "[1]" in md_with_citations
        assert "[2]" in md_with_citations
        assert "1. https://first.com" in references
        assert "2. https://second.com" in references

    def test_anchor_links_preserved(self, generator):
        """Test that anchor links are preserved."""
        markdown = "[section](#section-1)"

        md_with_citations, references = generator.convert_links_to_citations(markdown)

        # Anchor links should be preserved as-is
        assert "[section](#section-1)" in md_with_citations
        # No references for anchor links
        assert references == ""

    def test_no_links(self, generator):
        """Test markdown without links."""
        markdown = "Just plain text"

        md_with_citations, references = generator.convert_links_to_citations(markdown)

        assert md_with_citations == markdown
        assert references == ""
