"""Extraction implementations for CSS, XPath, and Regex."""

import re
from typing import List, Optional, Dict
from bs4 import BeautifulSoup
from lxml import html, etree

from shared.schemas.extraction_schemas import ExtractionResult


class CSSExtractor:
    """Extract data using CSS selectors."""

    @staticmethod
    def extract(
        html_content: str,
        selector: str,
        extract_text: bool = True,
        extract_html: bool = False,
        extract_attributes: Optional[List[str]] = None,
    ) -> List[ExtractionResult]:
        """Extract elements using CSS selector.

        Args:
            html_content: HTML content to parse.
            selector: CSS selector.
            extract_text: Extract text content.
            extract_html: Extract raw HTML.
            extract_attributes: List of attributes to extract.

        Returns:
            List of extraction results.
        """
        soup = BeautifulSoup(html_content, "lxml")
        elements = soup.select(selector)

        results = []
        for element in elements:
            result = ExtractionResult()

            if extract_text:
                result.text = element.get_text(strip=True)

            if extract_html:
                result.html = str(element)

            if extract_attributes:
                result.attributes = {
                    attr: element.get(attr)
                    for attr in extract_attributes
                    if element.get(attr) is not None
                }

            results.append(result)

        return results


class XPathExtractor:
    """Extract data using XPath expressions."""

    @staticmethod
    def extract(
        html_content: str,
        xpath: str,
        extract_text: bool = True,
        extract_html: bool = False,
        extract_attributes: Optional[List[str]] = None,
    ) -> List[ExtractionResult]:
        """Extract elements using XPath.

        Args:
            html_content: HTML content to parse.
            xpath: XPath expression.
            extract_text: Extract text content.
            extract_html: Extract raw HTML.
            extract_attributes: List of attributes to extract.

        Returns:
            List of extraction results.
        """
        try:
            tree = html.fromstring(html_content)
            elements = tree.xpath(xpath)

            results = []
            for element in elements:
                result = ExtractionResult()

                # Handle scalar values (text, numbers, booleans)
                if isinstance(element, (str, int, float, bool)):
                    result.text = str(element)
                    results.append(result)
                    continue

                # Handle element nodes
                if extract_text:
                    result.text = element.text_content().strip()

                if extract_html:
                    result.html = etree.tostring(
                        element, encoding="unicode", method="html"
                    )

                if extract_attributes:
                    result.attributes = {
                        attr: element.get(attr)
                        for attr in extract_attributes
                        if element.get(attr) is not None
                    }

                results.append(result)

            return results

        except Exception as e:
            raise ValueError(f"Invalid XPath expression: {str(e)}")


class RegexExtractor:
    """Extract data using regular expressions."""

    @staticmethod
    def extract(
        text: str,
        pattern: str,
        group: Optional[int] = None,
        flags: int = 0,
    ) -> List[ExtractionResult]:
        """Extract matches using regex.

        Args:
            text: Text content to search.
            pattern: Regex pattern.
            group: Capture group to extract (None for full match).
            flags: Regex flags.

        Returns:
            List of extraction results.
        """
        try:
            matches = re.finditer(pattern, text, flags=flags)

            results = []
            for match in matches:
                result = ExtractionResult()

                if group is not None:
                    # Extract specific group
                    result.text = match.group(group)
                else:
                    # Extract full match
                    result.text = match.group(0)

                results.append(result)

            return results

        except Exception as e:
            raise ValueError(f"Invalid regex pattern: {str(e)}")
