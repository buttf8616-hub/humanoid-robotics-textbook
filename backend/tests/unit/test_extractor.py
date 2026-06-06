"""Unit tests for extractor service."""
import pytest

from src.services.extractor import ExtractorService


class TestExtractorService:
    """Tests for ExtractorService."""

    @pytest.fixture
    def extractor(self):
        """Create an ExtractorService instance."""
        return ExtractorService()

    def test_extract_removes_navigation(self, extractor, sample_html):
        """Test that navigation elements are removed."""
        result = extractor.extract(sample_html)

        assert "Navigation content" not in result.extracted_text
        assert "Footer content" not in result.extracted_text

    def test_extract_preserves_content(self, extractor, sample_html):
        """Test that main content is preserved."""
        result = extractor.extract(sample_html)

        assert "Physical AI represents" in result.extracted_text
        assert "fundamental concepts" in result.extracted_text

    def test_extract_no_html_tags(self, extractor, sample_html):
        """Test that no HTML tags remain in output."""
        result = extractor.extract(sample_html)

        assert "<" not in result.extracted_text
        assert ">" not in result.extracted_text

    def test_extract_sections(self, extractor, sample_html):
        """Test that sections are extracted with headers."""
        result = extractor.extract(sample_html)

        assert len(result.sections) >= 1
        # Check that headers are captured
        headers = [s.header for s in result.sections]
        assert any("Physical AI" in h for h in headers) or any("Key Concepts" in h for h in headers)

    def test_extract_title(self, extractor, sample_html):
        """Test that page title is extracted."""
        result = extractor.extract(sample_html)

        # Title should be from h1 or title tag
        assert result.title != ""

    def test_extract_empty_html(self, extractor):
        """Test handling of empty HTML."""
        result = extractor.extract("<html><body></body></html>")

        assert result.extracted_text == "" or result.extracted_text.strip() == ""

    def test_extract_malformed_html(self, extractor):
        """Test handling of malformed HTML."""
        malformed = "<html><body><p>Unclosed paragraph<div>Mixed tags</body>"
        result = extractor.extract(malformed)

        # Should not raise, should return some content
        assert result is not None
