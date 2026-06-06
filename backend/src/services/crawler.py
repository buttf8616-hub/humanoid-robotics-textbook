"""Web crawler service for fetching book pages."""
import asyncio
import logging
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Optional
from urllib.parse import urljoin, urlparse

import httpx

from src.config import settings
from src.models import BookPage

logger = logging.getLogger(__name__)


class CrawlerService:
    """Service for crawling the deployed Docusaurus book."""

    def __init__(self, base_url: Optional[str] = None):
        """Initialize the crawler.

        Args:
            base_url: Base URL of the deployed book. Defaults to settings.
        """
        self.base_url = base_url or settings.book_base_url
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=30.0,
                follow_redirects=True,
                headers={"User-Agent": "BookIngestionPipeline/1.0"},
            )
        return self._client

    async def close(self):
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def _normalize_url(self, url: str) -> str:
        """Replace the sitemap's host with the configured base_url host.

        Handles mismatches when docusaurus.config.js `url` differs from the
        actual deployment URL (e.g. placeholder values in the sitemap).
        """
        parsed_sitemap = urlparse(url)
        parsed_base = urlparse(self.base_url)
        return parsed_sitemap._replace(
            scheme=parsed_base.scheme,
            netloc=parsed_base.netloc,
        ).geturl()

    def parse_sitemap(self, sitemap_xml: str) -> list[str]:
        """Parse sitemap XML and extract URLs, normalised to base_url host."""
        urls = []
        try:
            root = ET.fromstring(sitemap_xml)
            ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

            for url_elem in root.findall(".//sm:url/sm:loc", ns):
                if url_elem.text:
                    url = self._normalize_url(url_elem.text.strip())
                    if "/docs/" in url or url.endswith("/intro") or "/modules/" in url:
                        urls.append(url)

            if not urls:
                for url_elem in root.findall(".//loc"):
                    if url_elem.text:
                        url = self._normalize_url(url_elem.text.strip())
                        if "/docs/" in url or url.endswith("/intro") or "/modules/" in url:
                            urls.append(url)

        except ET.ParseError as e:
            logger.error(f"Failed to parse sitemap: {e}")

        logger.info(f"Found {len(urls)} doc URLs in sitemap")
        return urls

    async def fetch_sitemap(self) -> list[str]:
        """Fetch and parse the sitemap.

        Returns:
            List of URLs to crawl.
        """
        client = await self._get_client()
        sitemap_url = urljoin(self.base_url, "/sitemap.xml")

        try:
            response = await client.get(sitemap_url)
            if response.status_code == 200:
                return self.parse_sitemap(response.text)
            else:
                logger.warning(f"Sitemap returned {response.status_code}, falling back to known paths")
                return self._get_fallback_urls()
        except httpx.RequestError as e:
            logger.error(f"Failed to fetch sitemap: {e}")
            return self._get_fallback_urls()

    def _get_fallback_urls(self) -> list[str]:
        """Get fallback URLs when sitemap is unavailable."""
        # Known Docusaurus structure for this book
        base = self.base_url.rstrip("/")
        return [
            f"{base}/",
            f"{base}/intro",
        ]

    async def fetch_page(self, url: str, retries: int = 3) -> Optional[BookPage]:
        """Fetch a single page with retry logic.

        Args:
            url: URL to fetch.
            retries: Number of retries on failure.

        Returns:
            BookPage if successful, None otherwise.
        """
        client = await self._get_client()

        for attempt in range(retries):
            try:
                response = await client.get(url)

                if response.status_code == 200:
                    return BookPage(
                        url=url,
                        title="",  # Will be extracted later
                        raw_html=response.text,
                        fetched_at=datetime.utcnow(),
                    )
                elif response.status_code == 404:
                    logger.warning(f"Page not found: {url}")
                    return None
                else:
                    logger.warning(f"Unexpected status {response.status_code} for {url}")

            except httpx.RequestError as e:
                logger.error(f"Request failed for {url} (attempt {attempt + 1}): {e}")

                if attempt < retries - 1:
                    # Exponential backoff
                    await asyncio.sleep(2 ** attempt)

        return None

    async def crawl_all(self) -> list[BookPage]:
        """Crawl all pages from the book.

        Returns:
            List of BookPage objects with raw HTML.
        """
        urls = await self.fetch_sitemap()
        logger.info(f"Starting to crawl {len(urls)} pages")

        pages = []
        for url in urls:
            page = await self.fetch_page(url)
            if page:
                pages.append(page)
                logger.debug(f"Fetched: {url}")

            # Rate limiting - be nice to the server
            await asyncio.sleep(0.5)

        logger.info(f"Successfully crawled {len(pages)} pages")
        return pages
