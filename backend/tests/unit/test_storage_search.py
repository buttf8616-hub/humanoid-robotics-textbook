"""Unit tests for storage service search functionality."""
import pytest
from unittest.mock import MagicMock, patch

from src.services.storage import StorageService


class TestStorageSearch:
    """Tests for StorageService search method."""

    @pytest.fixture
    def storage(self):
        """Create a StorageService instance with mocked client."""
        with patch("src.services.storage.QdrantClient") as mock_qdrant:
            mock_client = MagicMock()
            mock_qdrant.return_value = mock_client
            service = StorageService(
                url="http://test:6333",
                api_key="test-key",
                collection_name="test-collection",
            )
            service._client = mock_client
            return service

    @pytest.fixture
    def mock_search_results(self):
        """Create mock search results."""
        result1 = MagicMock()
        result1.score = 0.89
        result1.payload = {
            "content": "Embodied intelligence refers to...",
            "url": "https://example.com/chapter-1",
            "title": "Introduction to Physical AI",
            "section": "Core Concepts",
            "chunk_index": 0,
        }

        result2 = MagicMock()
        result2.score = 0.75
        result2.payload = {
            "content": "Physical AI systems demonstrate...",
            "url": "https://example.com/chapter-2",
            "title": "Embodied Intelligence",
            "section": "Overview",
            "chunk_index": 1,
        }

        return [result1, result2]

    def test_search_returns_results_with_scores(self, storage, mock_search_results):
        """Test that search returns results with relevance scores."""
        storage._client.search.return_value = mock_search_results
        query_vector = [0.1] * 1024

        results = storage.search(query_vector, top_k=5)

        assert len(results) == 2
        assert results[0]["score"] == 0.89
        assert results[1]["score"] == 0.75

    def test_search_returns_metadata(self, storage, mock_search_results):
        """Test that search returns chunk metadata."""
        storage._client.search.return_value = mock_search_results
        query_vector = [0.1] * 1024

        results = storage.search(query_vector, top_k=5)

        assert results[0]["content"] == "Embodied intelligence refers to..."
        assert results[0]["url"] == "https://example.com/chapter-1"
        assert results[0]["title"] == "Introduction to Physical AI"
        assert results[0]["section"] == "Core Concepts"
        assert results[0]["chunk_index"] == 0

    def test_search_respects_top_k(self, storage, mock_search_results):
        """Test that search passes top_k to Qdrant."""
        storage._client.search.return_value = mock_search_results
        query_vector = [0.1] * 1024

        storage.search(query_vector, top_k=10)

        call_kwargs = storage._client.search.call_args[1]
        assert call_kwargs["limit"] == 10

    def test_search_with_url_filter(self, storage, mock_search_results):
        """Test search with URL filter applies MatchValue condition."""
        storage._client.search.return_value = mock_search_results
        query_vector = [0.1] * 1024

        storage.search(
            query_vector,
            top_k=5,
            url_filter="https://example.com/chapter-1",
        )

        call_kwargs = storage._client.search.call_args[1]
        assert call_kwargs["query_filter"] is not None
        # Verify filter structure
        filter_obj = call_kwargs["query_filter"]
        assert len(filter_obj.must) == 1
        assert filter_obj.must[0].key == "url"

    def test_search_with_section_filter(self, storage, mock_search_results):
        """Test search with section filter applies MatchText condition."""
        storage._client.search.return_value = mock_search_results
        query_vector = [0.1] * 1024

        storage.search(
            query_vector,
            top_k=5,
            section_filter="Introduction",
        )

        call_kwargs = storage._client.search.call_args[1]
        assert call_kwargs["query_filter"] is not None
        filter_obj = call_kwargs["query_filter"]
        assert len(filter_obj.must) == 1
        assert filter_obj.must[0].key == "section"

    def test_search_with_combined_filters(self, storage, mock_search_results):
        """Test search with both URL and section filters."""
        storage._client.search.return_value = mock_search_results
        query_vector = [0.1] * 1024

        storage.search(
            query_vector,
            top_k=5,
            url_filter="https://example.com/chapter-1",
            section_filter="Core Concepts",
        )

        call_kwargs = storage._client.search.call_args[1]
        filter_obj = call_kwargs["query_filter"]
        assert len(filter_obj.must) == 2

    def test_search_without_filters(self, storage, mock_search_results):
        """Test search without filters passes None for query_filter."""
        storage._client.search.return_value = mock_search_results
        query_vector = [0.1] * 1024

        storage.search(query_vector, top_k=5)

        call_kwargs = storage._client.search.call_args[1]
        assert call_kwargs["query_filter"] is None

    def test_search_empty_results(self, storage):
        """Test search handles empty results gracefully."""
        storage._client.search.return_value = []
        query_vector = [0.1] * 1024

        results = storage.search(query_vector, top_k=5)

        assert results == []

    def test_search_uses_correct_collection(self, storage, mock_search_results):
        """Test search queries the correct collection."""
        storage._client.search.return_value = mock_search_results
        query_vector = [0.1] * 1024

        storage.search(query_vector, top_k=5)

        call_kwargs = storage._client.search.call_args[1]
        assert call_kwargs["collection_name"] == "test-collection"

    def test_search_requests_payload(self, storage, mock_search_results):
        """Test search requests payload with results."""
        storage._client.search.return_value = mock_search_results
        query_vector = [0.1] * 1024

        storage.search(query_vector, top_k=5)

        call_kwargs = storage._client.search.call_args[1]
        assert call_kwargs["with_payload"] is True

    def test_search_handles_missing_payload_fields(self, storage):
        """Test search handles results with missing payload fields."""
        result = MagicMock()
        result.score = 0.5
        result.payload = {"content": "Some text"}  # Missing other fields

        storage._client.search.return_value = [result]
        query_vector = [0.1] * 1024

        results = storage.search(query_vector, top_k=5)

        assert len(results) == 1
        assert results[0]["content"] == "Some text"
        assert results[0]["url"] == ""
        assert results[0]["title"] == ""
        assert results[0]["section"] == ""
        assert results[0]["chunk_index"] == 0
