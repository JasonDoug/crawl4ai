"""Content scraper implementation using lxml and BeautifulSoup."""

import logging
import re
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse
from lxml import html as lxml_html, etree
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class ExtractionRule:
    """Rule for extracting specific content."""

    def __init__(
        self,
        name: str,
        selector: str,
        attribute: Optional[str] = None,
        multiple: bool = False,
    ):
        """Initialize extraction rule.

        Args:
            name: Name of the extracted field
            selector: CSS or XPath selector
            attribute: Attribute to extract (None for text content)
            multiple: Whether to extract multiple elements
        """
        self.name = name
        self.selector = selector
        self.attribute = attribute
        self.multiple = multiple


class ContentScraper:
    """Scrapes content from HTML using lxml and BeautifulSoup."""

    def __init__(self):
        """Initialize the content scraper."""
        self._link_patterns: Set[str] = set()
        self._exclude_selectors: List[str] = [
            "script",
            "style",
            "noscript",
            "iframe",
            "svg",
        ]

    def scrape(
        self,
        html: str,
        extract_links: bool = False,
        extract_images: bool = False,
        extract_media: bool = False,
        extract_metadata: bool = False,
        extract_tables: bool = False,
        extract_structured_data: bool = False,
        custom_rules: Optional[List[ExtractionRule]] = None,
        base_url: Optional[str] = None,
        clean_text: bool = True,
    ) -> Dict[str, Any]:
        """Scrape content from HTML.

        Args:
            html: HTML content to scrape
            extract_links: Extract all links
            extract_images: Extract all images
            extract_media: Extract media elements
            extract_metadata: Extract page metadata
            extract_tables: Extract table data
            extract_structured_data: Extract JSON-LD and schema.org data
            custom_rules: Custom extraction rules
            base_url: Base URL for resolving relative URLs
            clean_text: Whether to clean extracted text

        Returns:
            Dictionary with extracted content
        """
        result: Dict[str, Any] = {}

        try:
            # Parse with lxml for performance
            tree = lxml_html.fromstring(html)

            # Extract plain text
            result["text"] = self._extract_text(tree, clean=clean_text)

            # Extract headings structure
            result["headings"] = self._extract_headings(tree)

            # Extract links
            if extract_links:
                result["links"] = self._extract_links(tree, base_url)

            # Extract images
            if extract_images:
                result["images"] = self._extract_images(tree, base_url)

            # Extract media
            if extract_media:
                result["media"] = self._extract_media(tree, base_url)

            # Extract metadata
            if extract_metadata:
                result["metadata"] = self._extract_metadata(tree)

            # Extract tables
            if extract_tables:
                result["tables"] = self._extract_tables(tree)

            # Extract structured data
            if extract_structured_data:
                result["structured_data"] = self._extract_structured_data(tree)

            # Apply custom extraction rules
            if custom_rules:
                result["custom"] = self._apply_custom_rules(
                    tree, custom_rules, base_url
                )

        except Exception as e:
            logger.error(f"Error scraping content: {e}")
            result["error"] = str(e)

        return result

    def _extract_text(self, tree, clean: bool = True) -> str:
        """Extract plain text from HTML tree.

        Args:
            tree: lxml HTML tree
            clean: Whether to clean the text

        Returns:
            Extracted text
        """
        # Clone tree to avoid modifying original
        tree = etree.ElementTree(tree).getroot()

        # Remove unwanted elements
        for selector in self._exclude_selectors:
            for element in tree.xpath(f".//{selector}"):
                parent = element.getparent()
                if parent is not None:
                    parent.remove(element)

        # Get text content
        text = tree.text_content()

        if clean:
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = " ".join(chunk for chunk in chunks if chunk)

            # Remove excessive whitespace
            text = re.sub(r"\s+", " ", text).strip()

        return text

    def _extract_headings(self, tree) -> List[Dict[str, Any]]:
        """Extract heading structure from HTML tree.

        Args:
            tree: lxml HTML tree

        Returns:
            List of headings with level and text
        """
        headings = []

        for level in range(1, 7):  # h1 to h6
            for element in tree.xpath(f".//h{level}"):
                text = element.text_content().strip()
                if text:
                    headings.append(
                        {
                            "level": level,
                            "text": text,
                            "id": element.get("id"),
                        }
                    )

        return headings

    def _extract_links(self, tree, base_url: Optional[str] = None) -> List[str]:
        """Extract all links from HTML tree.

        Args:
            tree: lxml HTML tree
            base_url: Base URL for resolving relative links

        Returns:
            List of absolute URLs
        """
        links = []

        for element in tree.xpath(".//a[@href]"):
            href = element.get("href")
            if href:
                # Resolve relative URLs
                if base_url:
                    href = urljoin(base_url, href)
                links.append(href)

        return list(set(links))  # Remove duplicates

    def _extract_images(
        self, tree, base_url: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """Extract all images from HTML tree.

        Args:
            tree: lxml HTML tree
            base_url: Base URL for resolving relative URLs

        Returns:
            List of image dictionaries with src, alt, etc.
        """
        images = []

        for element in tree.xpath(".//img[@src]"):
            src = element.get("src")
            if src:
                # Resolve relative URLs
                if base_url:
                    src = urljoin(base_url, src)

                images.append(
                    {
                        "src": src,
                        "alt": element.get("alt", ""),
                        "title": element.get("title", ""),
                    }
                )

        return images

    def _extract_media(
        self, tree, base_url: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """Extract media elements (video, audio) from HTML tree.

        Args:
            tree: lxml HTML tree
            base_url: Base URL for resolving relative URLs

        Returns:
            List of media dictionaries
        """
        media = []

        # Extract videos
        for element in tree.xpath(".//video"):
            src = element.get("src") or (element.xpath(".//source/@src") or [None])[0]
            if src:
                if base_url:
                    src = urljoin(base_url, src)
                media.append(
                    {
                        "type": "video",
                        "src": src,
                        "poster": element.get("poster", ""),
                    }
                )

        # Extract audio
        for element in tree.xpath(".//audio"):
            src = element.get("src") or (element.xpath(".//source/@src") or [None])[0]
            if src:
                if base_url:
                    src = urljoin(base_url, src)
                media.append(
                    {
                        "type": "audio",
                        "src": src,
                    }
                )

        return media

    def _extract_metadata(self, tree) -> Dict[str, Any]:
        """Extract page metadata from HTML tree.

        Args:
            tree: lxml HTML tree

        Returns:
            Dictionary with metadata
        """
        metadata = {}

        # Extract title
        title = tree.xpath(".//title/text()")
        if title:
            metadata["title"] = title[0].strip()

        # Extract meta tags
        for element in tree.xpath(".//meta"):
            name = element.get("name") or element.get("property")
            content = element.get("content")
            if name and content:
                metadata[name] = content

        # Extract canonical URL
        canonical = tree.xpath(".//link[@rel='canonical']/@href")
        if canonical:
            metadata["canonical"] = canonical[0]

        # Extract language
        lang = tree.xpath(".//html/@lang")
        if lang:
            metadata["language"] = lang[0]

        return metadata

    def _extract_tables(self, tree) -> List[Dict[str, Any]]:
        """Extract table data from HTML tree.

        Args:
            tree: lxml HTML tree

        Returns:
            List of tables with headers and rows
        """
        tables = []

        for table_idx, table in enumerate(tree.xpath(".//table")):
            table_data = {
                "index": table_idx,
                "headers": [],
                "rows": [],
            }

            # Extract headers
            headers = table.xpath(".//thead//th | .//tr[1]//th")
            if headers:
                table_data["headers"] = [h.text_content().strip() for h in headers]
            else:
                # Try first row as headers
                first_row = table.xpath(".//tr[1]//td")
                if first_row:
                    table_data["headers"] = [
                        cell.text_content().strip() for cell in first_row
                    ]

            # Extract rows
            row_xpath = ".//tbody//tr" if table.xpath(".//tbody") else ".//tr"
            start_idx = 2 if not headers and table_data["headers"] else 1

            for row in table.xpath(f"{row_xpath}[position()>={start_idx}]"):
                cells = row.xpath(".//td | .//th")
                if cells:
                    table_data["rows"].append(
                        [cell.text_content().strip() for cell in cells]
                    )

            if table_data["rows"]:
                tables.append(table_data)

        return tables

    def _extract_structured_data(self, tree) -> List[Dict[str, Any]]:
        """Extract structured data (JSON-LD, Microdata) from HTML tree.

        Args:
            tree: lxml HTML tree

        Returns:
            List of structured data objects
        """
        import json

        structured_data = []

        # Extract JSON-LD
        for script in tree.xpath(".//script[@type='application/ld+json']"):
            try:
                data = json.loads(script.text_content())
                structured_data.append(
                    {
                        "type": "json-ld",
                        "data": data,
                    }
                )
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON-LD: {e}")

        # Extract microdata (schema.org)
        for item in tree.xpath(".//*[@itemscope]"):
            item_data = {
                "type": "microdata",
                "itemtype": item.get("itemtype"),
                "properties": {},
            }

            for prop in item.xpath(".//*[@itemprop]"):
                prop_name = prop.get("itemprop")
                prop_value = prop.get("content") or prop.text_content().strip()
                item_data["properties"][prop_name] = prop_value

            if item_data["properties"]:
                structured_data.append(item_data)

        return structured_data

    def _apply_custom_rules(
        self,
        tree,
        rules: List[ExtractionRule],
        base_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Apply custom extraction rules to HTML tree.

        Args:
            tree: lxml HTML tree
            rules: List of extraction rules
            base_url: Base URL for resolving relative URLs

        Returns:
            Dictionary with custom extracted data
        """
        result = {}

        for rule in rules:
            try:
                # Use XPath selector
                if rule.selector.startswith("//") or rule.selector.startswith(".//"):
                    elements = tree.xpath(rule.selector)
                else:
                    # Convert CSS selector to XPath
                    from lxml.cssselect import CSSSelector

                    selector = CSSSelector(rule.selector)
                    elements = selector(tree)

                if not elements:
                    result[rule.name] = [] if rule.multiple else None
                    continue

                # Extract values
                values = []
                for element in elements:
                    if rule.attribute:
                        value = element.get(rule.attribute)
                        # Resolve URLs if needed
                        if base_url and rule.attribute in ["href", "src"]:
                            value = urljoin(base_url, value) if value else None
                    else:
                        value = element.text_content().strip()

                    if value:
                        values.append(value)

                # Return single value or list
                if rule.multiple:
                    result[rule.name] = values
                else:
                    result[rule.name] = values[0] if values else None

            except Exception as e:
                logger.error(f"Error applying rule '{rule.name}': {e}")
                result[rule.name] = [] if rule.multiple else None

        return result
