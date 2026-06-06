"""Unit tests for agent tool functions."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from src.agent.tools import retrieve_book_content, RETRIEVE_BOOK_CONTENT_SCHEMA


class TestRetrieveBookContent:
    """Tests for retrieve_book_content tool function."""

    @pytest.mark.asyncio
    async def test_retrieve_calls_search_endpoint(self):
        """Test that retrieve_book_content calls the /search endpoint."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [
                {
                    "content": "Test content",
                    "url": "https://example.com",
                    "title": "Test Title",
                    "section": "Test Section",
                    "chunk_index": 0,
                    "score": 0.9,
                }
            ],
            "total_count": 1,
            "latency_ms": 100,
            "filters_applied": {},
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = await retrieve_book_content("What is embodied intelligence?")

            # Verify the POST call was made
            mock_client.post.assert_called_once()
            call_args = mock_client.post.call_args
            assert "/api/v1/search" in call_args[0][0]
            assert call_args[1]["json"]["query"] == "What is embodied intelligence?"

    @pytest.mark.asyncio
    async def test_retrieve_passes_top_k_parameter(self):
        """Test that top_k parameter is passed to search endpoint."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [],
            "total_count": 0,
            "latency_ms": 50,
            "filters_applied": {},
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            await retrieve_book_content("test query", top_k=10)

            call_args = mock_client.post.call_args
            assert call_args[1]["json"]["top_k"] == 10

    @pytest.mark.asyncio
    async def test_retrieve_passes_url_filter(self):
        """Test that url_filter is passed to search endpoint."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [],
            "total_count": 0,
            "latency_ms": 50,
            "filters_applied": {"url_filter": "https://example.com"},
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            await retrieve_book_content(
                "test query",
                url_filter="https://example.com",
            )

            call_args = mock_client.post.call_args
            assert call_args[1]["json"]["url_filter"] == "https://example.com"

    @pytest.mark.asyncio
    async def test_retrieve_passes_section_filter(self):
        """Test that section_filter is passed to search endpoint."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [],
            "total_count": 0,
            "latency_ms": 50,
            "filters_applied": {"section_filter": "Introduction"},
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            await retrieve_book_content(
                "test query",
                section_filter="Introduction",
            )

            call_args = mock_client.post.call_args
            assert call_args[1]["json"]["section_filter"] == "Introduction"

    @pytest.mark.asyncio
    async def test_retrieve_handles_timeout(self):
        """Test that timeout is handled gracefully."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.post.side_effect = httpx.TimeoutException("Timeout")
            mock_client_class.return_value = mock_client

            result = await retrieve_book_content("test query")

            assert result["total_count"] == 0
            assert result["results"] == []
            assert "error" in result
            assert "timeout" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_retrieve_handles_http_error(self):
        """Test that HTTP errors are handled gracefully."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.post.side_effect = httpx.HTTPError("Service unavailable")
            mock_client_class.return_value = mock_client

            result = await retrieve_book_content("test query")

            assert result["total_count"] == 0
            assert result["results"] == []
            assert "error" in result

    def test_tool_schema_is_valid(self):
        """Test that the tool schema is properly structured."""
        schema = RETRIEVE_BOOK_CONTENT_SCHEMA

        assert schema["type"] == "function"
        assert "function" in schema
        assert schema["function"]["name"] == "retrieve_book_content"
        assert "description" in schema["function"]
        assert "parameters" in schema["function"]
        assert schema["function"]["parameters"]["required"] == ["query"]
