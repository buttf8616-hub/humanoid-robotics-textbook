"""Text extraction service for HTML pages — pure lxml for C-speed parsing."""
import logging
import re
from typing import Optional

from lxml import etree
from lxml import html as lxml_html

from src.models import BookPage, Section

logger = logging.getLogger(__name__)

# Strip Docusaurus JSON data blobs BEFORE parsing (can be 100s of KB each)
_JSON_SCRIPT_RE = re.compile(
    r'<script\b[^>]*\btype=["\']application/json["\'][^>]*>.*?</script>',
    re.DOTALL | re.IGNORECASE,
)

_HEADER_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
_TEXT_TAGS = {"p", "li", "td", "th", "pre", "blockquote"}

# Tags whose entire subtree we remove (no content value)
_REMOVE_TAGS = {"script", "style", "noscript", "nav", "header",
                "footer", "aside", "form", "svg", "figure"}

# CSS class substrings that indicate non-content elements
_REMOVE_CLASSES = {
    "navbar", "sidebar", "menu", "pagination", "breadcrumb",
    "table-of-contents", "toc", "footer", "theme-doc-sidebar",
    "theme-navbar", "announcementBar",
}

# Content XPath selectors tried in order (most specific first)
_CONTENT_XPATHS = [
    '//article[contains(@class,"markdown")]',
    '//article',
    '//main',
    '//*[contains(@class,"markdown")]',
    '//*[contains(@class,"content")]',
    '//body',
]


class ExtractorService:
    """Service for extracting clean text from HTML pages using lxml."""

    def extract(self, html: str, url: str = "") -> BookPage:
        """Extract clean text and sections from HTML."""
        # Pre-strip large JSON blobs to drastically reduce parse work
        html = _JSON_SCRIPT_RE.sub('', html)

        # Parse with lxml's fast C HTML parser
        try:
            doc = lxml_html.fromstring(html)
        except Exception as exc:
            logger.warning("lxml parse failed for %s: %s", url, exc)
            return BookPage(url=url, title="", raw_html=html,
                            extracted_text="", sections=[])

        # Extract title BEFORE we strip anything
        title = self._extract_title(doc)

        # Remove unwanted subtrees (scripts, nav, sidebars, …)
        self._remove_elements(doc)

        # Find main article/content node
        content = self._find_content(doc)

        # Single O(n) pass: extract sections
        sections = self._extract_sections(content)

        # Fast text dump
        extracted_text = self._get_text(content)

        return BookPage(
            url=url,
            title=title,
            raw_html=html,
            extracted_text=extracted_text,
            sections=sections,
        )

    # ------------------------------------------------------------------ #
    # private helpers                                                      #
    # ------------------------------------------------------------------ #

    def _extract_title(self, doc) -> str:
        h1 = doc.find('.//h1')
        if h1 is not None:
            return (h1.text_content() or '').strip()
        og = doc.find('.//meta[@property="og:title"]')
        if og is not None:
            return og.get('content', '').strip()
        title_el = doc.find('.//title')
        if title_el is not None:
            return (title_el.text_content() or '').strip()
        return ''

    def _remove_elements(self, doc) -> None:
        """Remove all elements whose tag or class marks them as non-content."""
        to_remove = []
        for elem in doc.iter():
            tag = getattr(elem, 'tag', None)
            if not isinstance(tag, str):
                continue
            if tag in _REMOVE_TAGS:
                to_remove.append(elem)
                continue
            # Split into individual tokens so "anchorWithStickyNavbar_…" doesn't
            # accidentally match the "navbar" removal rule.
            cls_tokens = set((elem.get('class') or '').lower().split())
            if any(c in cls_tokens for c in _REMOVE_CLASSES):
                to_remove.append(elem)

        for elem in to_remove:
            parent = elem.getparent()
            if parent is not None:
                parent.remove(elem)

    def _find_content(self, doc):
        for xpath in _CONTENT_XPATHS:
            try:
                results = doc.xpath(xpath)
            except Exception:
                continue
            if results:
                return results[0]
        return doc

    def _extract_sections(self, content) -> list[Section]:
        """O(n) single pass — no sibling scanning, no quadratic work."""
        sections: list[Section] = []
        current_header: Optional[str] = None
        current_level: int = 0
        current_parts: list[str] = []

        for elem in content.iter():
            tag = getattr(elem, 'tag', None)
            if not isinstance(tag, str):
                continue

            if tag in _HEADER_TAGS:
                if current_header:
                    sections.append(Section(
                        header=current_header,
                        level=current_level,
                        content=' '.join(current_parts),
                    ))
                current_header = (elem.text_content() or '').strip()
                current_level = int(tag[1])
                current_parts = []

            elif current_header and tag in _TEXT_TAGS:
                text = (elem.text_content() or '').strip()
                if text:
                    current_parts.append(text)

        if current_header:
            sections.append(Section(
                header=current_header,
                level=current_level,
                content=' '.join(current_parts),
            ))

        return sections

    def _get_text(self, content) -> str:
        text = (content.text_content() or '').strip()
        # Collapse runs of whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'[ \t]{2,}', ' ', text)
        return text
