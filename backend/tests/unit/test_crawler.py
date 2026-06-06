"""Unit tests for crawler service."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from src.services.crawler import CrawlerService


class TestCrawlerService:
    """Tests for CrawlerService."""

    @pytest.fixture
    def crawler(self):
        """Create a CrawlerService instance."""
        return CrawlerService(base_url="https://example.com")

    def test_parse_sitemap_urls(self, crawler):
        """Test that sitemap XML is parsed correctly."""
        sitemap_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url><loc>https://example.com/docs/intro</loc></url>
            <url><loc>https://example.com/docs/chapter1</loc></url>
            <url><loc>https://example.com/blog/post1</loc></url>
        </urlset>
        """
        urls = crawler.parse_sitemap(sitemap_xml)

        # Should filter to only docs URLs
        assert len(urls) >= 2
        assert "https://example.com/docs/intro" in urls
        assert "https://example.com/docs/chapter1" in urls

    @pytest.mark.asyncio
    async def test_fetch_page_success(self, crawler):
        """Test successful page fetching."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Test content</body></html>"

        with patch.object(crawler, '_client') as mock_client:
            mock_client.get = AsyncMock(return_value=mock_response)

            result = await crawler.fetch_page("https://example.com/docs/intro")

            assert result is not None
            assert "Test content" in result.raw_html

    @pytest.mark.asyncio
    async def test_fetch_page_404_returns_none(self, crawler):
        """Test that 404 errors return None."""
        mock_response = MagicMock()
        mock_response.status_code = 404

        with patch.object(crawler, '_client') as mock_client:
            mock_client.get = AsyncMock(return_value=mock_response)

            result = await crawler.fetch_page("https://example.com/missing")

            assert result is None

    @pytest.mark.asyncio
    async def test_crawl_all_pages(self, crawler):
        """Test crawling all pages from sitemap."""
        sitemap_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url><loc>https://example.com/docs/intro</loc></url>
        </urlset>
        """
        mock_page_response = MagicMock()
        mock_page_response.status_code = 200
        mock_page_response.text = "<html><body>Content</body></html>"

        mock_sitemap_response = MagicMock()
        mock_sitemap_response.status_code = 200
        mock_sitemap_response.text = sitemap_xml

        with patch.object(crawler, '_client') as mock_client:
            mock_client.get = AsyncMock(side_effect=[mock_sitemap_response, mock_page_response])

            pages = await crawler.crawl_all()

            assert len(pages) >= 1
