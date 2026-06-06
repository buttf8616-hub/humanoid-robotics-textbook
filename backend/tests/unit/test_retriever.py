"""Unit tests for retriever service."""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock

from src.services.retriever import RetrieverService
from src.models import SearchResponse, RetrievalResult


class TestRetrieverService:
    """Tests for RetrieverService."""

    @pytest.fixture
    def retriever(self):
        """Create a RetrieverService with mocked dependencies."""
        with patch("src.services.retriever.EmbedderService") as mock_embedder_cls, \
             patch("src.services.retriever.StorageService") as mock_storage_cls:
            mock_embedder = MagicMock()
            mock_storage = MagicMock()
            mock_embedder_cls.return_value = mock_embedder
            mock_storage_cls.return_value = mock_storage

            service = RetrieverService()
            service.embedder = mock_embedder
            service.storage = mock_storage
            return service

    @pytest.fixture
    def mock_search_results(self):
        """Create mock search results from storage."""
        return [
            {
                "score": 0.89,
                "content": "Embodied intelligence refers to...",
                "url": "https://example.com/chapter-1",
                "title": "Introduction to Physical AI",
                "section": "Core Concepts",
                "chunk_index": 0,
            },
            {
                "score": 0.75,
                "content": "Physical AI systems demonstrate...",
                "url": "https://example.com/chapter-2",
                "title": "Embodied Intelligence",
                "section": "Overview",
                "chunk_index": 1,
            },
        ]

    @pytest.mark.asyncio
    async def test_retrieve_returns_search_response(self, retriever, mock_search_results):
        """Test that retrieve returns a SearchResponse object."""
        retriever.embedder.embed_query.return_value = [0.1] * 1024
        retriever.storage.search.return_value = mock_search_results

        response = await retriever.retrieve("What is embodied intelligence?")

        assert isinstance(response, SearchResponse)
        assert response.total_count == 2
        assert len(response.results) == 2

    @pytest.mark.asyncio
    async def test_retrieve_calls_embed_query(self, retriever, mock_search_results):
        """Test that retrieve calls embedder with the query."""
        retriever.embedder.embed_query.return_value = [0.1] * 1024
        retriever.storage.search.return_value = mock_search_results

        await retriever.retrieve("What is embodied intelligence?")

        retriever.embedder.embed_query.assert_called_once_with("What is embodied intelligence?")

    @pytest.mark.asyncio
    async def test_retrieve_calls_storage_search(self, retriever, mock_search_results):
        """Test that retrieve calls storage search with embedding."""
        query_vector = [0.1] * 1024
        retriever.embedder.embed_query.return_value = query_vector
        retriever.storage.search.return_value = mock_search_results

        await retriever.retrieve("test query", top_k=10)

        retriever.storage.search.assert_called_once()
        call_kwargs = retriever.storage.search.call_args[1]
        assert call_kwargs["query_vector"] == query_vector
        assert call_kwargs["top_k"] == 10

    @pytest.mark.asyncio
    async def test_retrieve_includes_latency(self, retriever, mock_search_results):
        """Test that retrieve measures and returns latency."""
        retriever.embedder.embed_query.return_value = [0.1] * 1024
        retriever.storage.search.return_value = mock_search_results

        response = await retriever.retrieve("test query")

        assert response.latency_ms > 0

    @pytest.mark.asyncio
    async def test_retrieve_maps_results_correctly(self, retriever, mock_search_results):
        """Test that search results are mapped to RetrievalResult objects."""
        retriever.embedder.embed_query.return_value = [0.1] * 1024
        retriever.storage.search.return_value = mock_search_results

        response = await retriever.retrieve("test query")

        assert response.results[0].content == "Embodied intelligence refers to..."
        assert response.results[0].url == "https://example.com/chapter-1"
        assert response.results[0].title == "Introduction to Physical AI"
        assert response.results[0].section == "Core Concepts"
        assert response.results[0].chunk_index == 0
        assert response.results[0].score == 0.89

    @pytest.mark.asyncio
    async def test_retrieve_passes_filters(self, retriever, mock_search_results):
        """Test that retrieve passes filters to storage search."""
        retriever.embedder.embed_query.return_value = [0.1] * 1024
        retriever.storage.search.return_value = mock_search_results

        await retriever.retrieve(
            "test query",
            url_filter="https://example.com/chapter-1",
            section_filter="Core Concepts",
        )

        call_kwargs = retriever.storage.search.call_args[1]
        assert call_kwargs["url_filter"] == "https://example.com/chapter-1"
        assert call_kwargs["section_filter"] == "Core Concepts"

    @pytest.mark.asyncio
    async def test_retrieve_includes_filters_applied(self, retriever, mock_search_results):
        """Test that response includes applied filters."""
        retriever.embedder.embed_query.return_value = [0.1] * 1024
        retriever.storage.search.return_value = mock_search_results

        response = await retriever.retrieve(
            "test query",
            url_filter="https://example.com",
        )

        assert response.filters_applied["url_filter"] == "https://example.com"

    @pytest.mark.asyncio
    async def test_retrieve_empty_results(self, retriever):
        """Test retrieve handles empty results gracefully."""
        retriever.embedder.embed_query.return_value = [0.1] * 1024
        retriever.storage.search.return_value = []

        response = await retriever.retrieve("obscure query")

        assert response.total_count == 0
        assert response.results == []

    @pytest.mark.asyncio
    async def test_retrieve_default_top_k(self, retriever, mock_search_results):
        """Test that retrieve uses default top_k of 5."""
        retriever.embedder.embed_query.return_value = [0.1] * 1024
        retriever.storage.search.return_value = mock_search_results

        await retriever.retrieve("test query")

        call_kwargs = retriever.storage.search.call_args[1]
        assert call_kwargs["top_k"] == 5

    @pytest.mark.asyncio
    async def test_retrieve_validates_top_k_bounds(self, retriever, mock_search_results):
        """Test that retrieve validates top_k within bounds."""
        retriever.embedder.embed_query.return_value = [0.1] * 1024
        retriever.storage.search.return_value = mock_search_results

        # Test top_k below minimum
        with pytest.raises(ValueError):
            await retriever.retrieve("test", top_k=0)

        # Test top_k above maximum
        with pytest.raises(ValueError):
            await retriever.retrieve("test", top_k=100)
