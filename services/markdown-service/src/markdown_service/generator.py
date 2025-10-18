"""Markdown generator implementation."""

import re
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass

# We'll use the html2text library from crawl4ai
# For the microservice, we need to vendor or depend on it
try:
    from crawl4ai.html2text import HTML2Text
except ImportError:
    # Fallback if crawl4ai is not installed
    # In production, this should be a proper dependency
    from html2text import HTML2Text


@dataclass
class MarkdownGenerationResult:
    """Result of markdown generation."""

    raw_markdown: str
    markdown_with_citations: str
    references_markdown: str
    fit_markdown: str
    fit_html: str


class CustomHTML2Text(HTML2Text):
    """Custom HTML to text converter with enhanced code block handling."""

    def __init__(self, *args, handle_code_in_pre=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.inside_pre = False
        self.inside_code = False
        self.inside_link = False
        self.preserve_tags = set()  # Set of tags to preserve
        self.current_preserved_tag = None
        self.preserved_content = []
        self.preserve_depth = 0
        self.handle_code_in_pre = handle_code_in_pre

        # Configuration options
        self.skip_internal_links = False
        self.single_line_break = False
        self.mark_code = False
        self.include_sup_sub = False
        self.body_width = 0
        self.ignore_mailto_links = True
        self.ignore_links = False
        self.escape_backslash = False
        self.escape_dot = False
        self.escape_plus = False
        self.escape_dash = False
        self.escape_snob = False

    def update_params(self, **kwargs):
        """Update parameters and set preserved tags."""
        for key, value in kwargs.items():
            if key == "preserve_tags":
                self.preserve_tags = set(value)
            elif key == "handle_code_in_pre":
                self.handle_code_in_pre = value
            else:
                setattr(self, key, value)

    def handle_tag(self, tag, attrs, start):
        # Handle preserved tags
        if tag in self.preserve_tags:
            if start:
                if self.preserve_depth == 0:
                    self.current_preserved_tag = tag
                    self.preserved_content = []
                    # Format opening tag with attributes
                    attr_str = "".join(
                        f' {k}="{v}"' for k, v in attrs.items() if v is not None
                    )
                    self.preserved_content.append(f"<{tag}{attr_str}>")
                self.preserve_depth += 1
                return
            else:
                self.preserve_depth -= 1
                if self.preserve_depth == 0:
                    self.preserved_content.append(f"</{tag}>")
                    # Output the preserved HTML block with proper spacing
                    preserved_html = "".join(self.preserved_content)
                    self.o("\n" + preserved_html + "\n")
                    self.current_preserved_tag = None
                return

        # If we're inside a preserved tag, collect all content
        if self.preserve_depth > 0:
            if start:
                # Format nested tags with attributes
                attr_str = "".join(
                    f' {k}="{v}"' for k, v in attrs.items() if v is not None
                )
                self.preserved_content.append(f"<{tag}{attr_str}>")
            else:
                self.preserved_content.append(f"</{tag}>")
            return

        # Handle pre tags
        if tag == "pre":
            if start:
                self.o("```\n")  # Markdown code block start
                self.inside_pre = True
            else:
                self.o("\n```\n")  # Markdown code block end
                self.inside_pre = False
        elif tag == "code":
            if self.inside_pre and not self.handle_code_in_pre:
                # Ignore code tags inside pre blocks if handle_code_in_pre is False
                return
            if start:
                if not self.inside_link:
                    self.o("`")  # Only output backtick if not inside a link
                self.inside_code = True
            else:
                if not self.inside_link:
                    self.o("`")  # Only output backtick if not inside a link
                self.inside_code = False

            # If inside a link, let the parent class handle the content
            if self.inside_link:
                super().handle_tag(tag, attrs, start)
        else:
            super().handle_tag(tag, attrs, start)

    def handle_data(self, data, entity_char=False):
        """Override handle_data to capture content within preserved tags."""
        if self.preserve_depth > 0:
            self.preserved_content.append(data)
            return

        if self.inside_pre:
            # Output the raw content for pre blocks, including content inside code tags
            self.o(data)  # Directly output the data as-is (preserve newlines)
            return
        if self.inside_code:
            # Inline code: no newlines allowed
            self.o(data.replace("\n", " "))
            return

        # Default behavior for other tags
        super().handle_data(data, entity_char)


class MarkdownGenerator:
    """Generate markdown from HTML content."""

    def __init__(self, options: Optional[Dict[str, Any]] = None):
        """Initialize markdown generator.

        Args:
            options: HTML2Text options for markdown generation.
        """
        self.options = options or {}

    def convert_links_to_citations(
        self, markdown: str, base_url: str = ""
    ) -> Tuple[str, str]:
        """Convert markdown links to numbered citations.

        Args:
            markdown: Input markdown with inline links.
            base_url: Base URL for resolving relative links.

        Returns:
            Tuple of (markdown with citations, references markdown).
        """
        # Pattern to match markdown links: [text](url)
        link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"

        links = {}
        link_counter = 1

        def replace_link(match):
            nonlocal link_counter
            text = match.group(1)
            url = match.group(2)

            # Resolve relative URLs
            if base_url and not url.startswith(("http://", "https://", "mailto:", "#")):
                url = urljoin(base_url, url)

            # Skip internal anchor links
            if url.startswith("#"):
                return f"[{text}]({url})"

            # Check if we've seen this URL before
            if url not in links:
                links[url] = link_counter
                link_counter += 1

            citation_num = links[url]
            return f"{text}[{citation_num}]"

        # Replace all links with citations
        markdown_with_citations = re.sub(link_pattern, replace_link, markdown)

        # Generate references section
        if links:
            references = ["## References\n"]
            for url, num in sorted(links.items(), key=lambda x: x[1]):
                references.append(f"{num}. {url}")
            references_markdown = "\n".join(references)
        else:
            references_markdown = ""

        return markdown_with_citations, references_markdown

    def generate_markdown(
        self,
        input_html: str,
        base_url: str = "",
        html2text_options: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None,
        content_filter: Optional[Any] = None,
        citations: bool = True,
    ) -> MarkdownGenerationResult:
        """Generate markdown from HTML.

        How it works:
        1. Generate raw markdown from the input HTML.
        2. Convert links to citations.
        3. Generate fit markdown if content filter is provided.
        4. Return MarkdownGenerationResult.

        Args:
            input_html: The HTML content to process.
            base_url: Base URL for URL joins.
            html2text_options: HTML2Text options.
            options: Additional options for markdown generation.
            content_filter: Content filter for generating fit markdown.
            citations: Whether to generate citations.

        Returns:
            MarkdownGenerationResult: Result containing raw markdown, fit markdown,
                                     fit HTML, and references markdown.
        """
        try:
            # Initialize HTML2Text with default options for better conversion
            h = CustomHTML2Text(baseurl=base_url)
            default_options = {
                "body_width": 0,  # Disable text wrapping
                "ignore_emphasis": False,
                "ignore_links": False,
                "ignore_images": False,
                "protect_links": False,
                "single_line_break": True,
                "mark_code": True,
                "escape_snob": False,
            }

            # Update with custom options if provided
            if html2text_options:
                default_options.update(html2text_options)
            elif options:
                default_options.update(options)
            elif self.options:
                default_options.update(self.options)

            h.update_params(**default_options)

            # Ensure we have valid input
            if not input_html:
                input_html = ""
            elif not isinstance(input_html, str):
                input_html = str(input_html)

            # Generate raw markdown
            try:
                raw_markdown = h.handle(input_html)
            except Exception as e:
                raw_markdown = f"Error converting HTML to markdown: {str(e)}"

            raw_markdown = raw_markdown.replace("    ```", "```")

            # Convert links to citations
            markdown_with_citations: str = raw_markdown
            references_markdown: str = ""
            if citations:
                try:
                    (
                        markdown_with_citations,
                        references_markdown,
                    ) = self.convert_links_to_citations(raw_markdown, base_url)
                except Exception as e:
                    markdown_with_citations = raw_markdown
                    references_markdown = f"Error generating citations: {str(e)}"

            # Generate fit markdown if content filter is provided
            fit_markdown: Optional[str] = ""
            filtered_html: Optional[str] = ""
            if content_filter:
                try:
                    filtered_html = content_filter.filter_content(input_html)
                    filtered_html = "\n".join(
                        "<div>{}</div>".format(s) for s in filtered_html
                    )
                    fit_markdown = h.handle(filtered_html)
                except Exception as e:
                    fit_markdown = f"Error generating fit markdown: {str(e)}"
                    filtered_html = ""

            return MarkdownGenerationResult(
                raw_markdown=raw_markdown or "",
                markdown_with_citations=markdown_with_citations or "",
                references_markdown=references_markdown or "",
                fit_markdown=fit_markdown or "",
                fit_html=filtered_html or "",
            )
        except Exception as e:
            # If anything fails, return empty strings with error message
            error_msg = f"Error in markdown generation: {str(e)}"
            return MarkdownGenerationResult(
                raw_markdown=error_msg,
                markdown_with_citations=error_msg,
                references_markdown="",
                fit_markdown="",
                fit_html="",
            )
