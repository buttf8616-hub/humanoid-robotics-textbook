"""Integration tests for retrieval API endpoint."""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_retriever():
    """Mock the RetrieverService for API tests."""
    with patch("src.api.routes.RetrieverService") as mock_cls:
        mock_service = MagicMock()
        mock_cls.return_value = mock_service
        yield mock_service


class TestSearchEndpoint:
    """Tests for POST /api/v1/search endpoint."""

    def test_search_returns_200_with_results(self, client, mock_retriever):
        """Test successful search returns 200 with results."""
        from src.models import SearchResponse, RetrievalResult

        mock_response = SearchResponse(
            results=[
                RetrievalResult(
                    content="Embodied intelligence refers to...",
                    url="https://example.com/chapter-1",
                    title="Introduction to Physical AI",
                    section="Core Concepts",
                    chunk_index=0,
                    score=0.89,
                )
            ],
            total_count=1,
            latency_ms=150.5,
            filters_applied={},
        )
        mock_retriever.retrieve = AsyncMock(return_value=mock_response)

        response = client.post(
            "/api/v1/search",
            json={"query": "What is embodied intelligence?"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 1
        assert len(data["results"]) == 1
        assert data["results"][0]["content"] == "Embodied intelligence refers to..."

    def test_search_returns_422_for_empty_query(self, client):
        """Test that empty query returns 422 validation error (Pydantic)."""
        response = client.post(
            "/api/v1/search",
            json={"query": ""},
        )

        # Pydantic min_length=1 validation returns 422
        assert response.status_code == 422

    def test_search_returns_400_for_whitespace_query(self, client):
        """Test that whitespace-only query returns 400."""
        response = client.post(
            "/api/v1/search",
            json={"query": "   "},
        )

        assert response.status_code == 400

    def test_search_accepts_top_k_parameter(self, client, mock_retriever):
        """Test that search accepts top_k parameter."""
        from src.models import SearchResponse

        mock_response = SearchResponse(
            results=[],
            total_count=0,
            latency_ms=100,
            filters_applied={},
        )
        mock_retriever.retrieve = AsyncMock(return_value=mock_response)

        response = client.post(
            "/api/v1/search",
            json={"query": "test", "top_k": 10},
        )

        assert response.status_code == 200

    def test_search_returns_400_for_invalid_top_k(self, client):
        """Test that invalid top_k returns 400."""
        # top_k below minimum
        response = client.post(
            "/api/v1/search",
            json={"query": "test", "top_k": 0},
        )
        assert response.status_code == 400 or response.status_code == 422

        # top_k above maximum
        response = client.post(
            "/api/v1/search",
            json={"query": "test", "top_k": 100},
        )
        assert response.status_code == 400 or response.status_code == 422

    def test_search_accepts_url_filter(self, client, mock_retriever):
        """Test that search accepts url_filter parameter."""
        from src.models import SearchResponse

        mock_response = SearchResponse(
            results=[],
            total_count=0,
            latency_ms=100,
            filters_applied={"url_filter": "https://example.com"},
        )
        mock_retriever.retrieve = AsyncMock(return_value=mock_response)

        response = client.post(
            "/api/v1/search",
            json={
                "query": "test",
                "url_filter": "https://example.com",
            },
        )

        assert response.status_code == 200

    def test_search_accepts_section_filter(self, client, mock_retriever):
        """Test that search accepts section_filter parameter."""
        from src.models import SearchResponse

        mock_response = SearchResponse(
            results=[],
            total_count=0,
            latency_ms=100,
            filters_applied={"section_filter": "Introduction"},
        )
        mock_retriever.retrieve = AsyncMock(return_value=mock_response)

        response = client.post(
            "/api/v1/search",
            json={
                "query": "test",
                "section_filter": "Introduction",
            },
        )

        assert response.status_code == 200

    def test_search_with_combined_filters(self, client, mock_retriever):
        """Test that search accepts both URL and section filters together."""
        from src.models import SearchResponse, RetrievalResult

        mock_response = SearchResponse(
            results=[
                RetrievalResult(
                    content="Filtered content",
                    url="https://example.com/specific-page",
                    title="Specific Page",
                    section="Introduction",
                    chunk_index=0,
                    score=0.92,
                )
            ],
            total_count=1,
            latency_ms=120,
            filters_applied={
                "url_filter": "https://example.com/specific-page",
                "section_filter": "Introduction",
            },
        )
        mock_retriever.retrieve = AsyncMock(return_value=mock_response)

        response = client.post(
            "/api/v1/search",
            json={
                "query": "test",
                "url_filter": "https://example.com/specific-page",
                "section_filter": "Introduction",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 1
        assert data["filters_applied"]["url_filter"] == "https://example.com/specific-page"
        assert data["filters_applied"]["section_filter"] == "Introduction"

        # Verify retriever was called with both filters
        mock_retriever.retrieve.assert_called_once()
        call_kwargs = mock_retriever.retrieve.call_args[1]
        assert call_kwargs["url_filter"] == "https://example.com/specific-page"
        assert call_kwargs["section_filter"] == "Introduction"

    def test_search_returns_latency_in_response(self, client, mock_retriever):
        """Test that search response includes latency_ms."""
        from src.models import SearchResponse

        mock_response = SearchResponse(
            results=[],
            total_count=0,
            latency_ms=234.5,
            filters_applied={},
        )
        mock_retriever.retrieve = AsyncMock(return_value=mock_response)

        response = client.post(
            "/api/v1/search",
            json={"query": "test"},
        )

        data = response.json()
        assert "latency_ms" in data
        assert data["latency_ms"] == 234.5

    def test_search_returns_503_on_embedding_error(self, client, mock_retriever):
        """Test that embedding service error returns 503."""
        from cohere.core.api_error import ApiError as CohereApiError
        mock_retriever.retrieve = AsyncMock(
            side_effect=CohereApiError(status_code=500, body={"message": "API error"})
        )

        response = client.post(
            "/api/v1/search",
            json={"query": "test"},
        )

        assert response.status_code == 503

    def test_search_returns_503_on_storage_error(self, client, mock_retriever):
        """Test that storage service error returns 503."""
        mock_retriever.retrieve = AsyncMock(
            side_effect=Exception("Qdrant connection failed")
        )

        response = client.post(
            "/api/v1/search",
            json={"query": "test"},
        )

        assert response.status_code == 503

    def test_search_response_includes_metadata(self, client, mock_retriever):
        """Test that results include all required metadata fields."""
        from src.models import SearchResponse, RetrievalResult

        mock_response = SearchResponse(
            results=[
                RetrievalResult(
                    content="Test content",
                    url="https://example.com/page",
                    title="Test Title",
                    section="Test Section",
                    chunk_index=5,
                    score=0.85,
                )
            ],
            total_count=1,
            latency_ms=100,
            filters_applied={},
        )
        mock_retriever.retrieve = AsyncMock(return_value=mock_response)

        response = client.post(
            "/api/v1/search",
            json={"query": "test"},
        )

        result = response.json()["results"][0]
        assert "content" in result
        assert "url" in result
        assert "title" in result
        assert "section" in result
        assert "chunk_index" in result
        assert "score" in result


class TestTopKVariations:
    """Tests for User Story 2: Configurable Top-K Retrieval."""

    def test_search_with_top_k_3(self, client, mock_retriever):
        """Test search with top_k=3 returns correct number of results."""
        from src.models import SearchResponse, RetrievalResult

        mock_results = [
            RetrievalResult(
                content=f"Content {i}",
                url=f"https://example.com/page-{i}",
                title=f"Title {i}",
                section="Section",
                chunk_index=i,
                score=0.9 - i * 0.1,
            )
            for i in range(3)
        ]
        mock_response = SearchResponse(
            results=mock_results,
            total_count=3,
            latency_ms=100,
            filters_applied={},
        )
        mock_retriever.retrieve = AsyncMock(return_value=mock_response)

        response = client.post(
            "/api/v1/search",
            json={"query": "test", "top_k": 3},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 3
        assert len(data["results"]) == 3

    def test_search_with_top_k_20(self, client, mock_retriever):
        """Test search with top_k=20 returns up to 20 results."""
        from src.models import SearchResponse, RetrievalResult

        mock_results = [
            RetrievalResult(
                content=f"Content {i}",
                url=f"https://example.com/page-{i}",
                title=f"Title {i}",
                section="Section",
                chunk_index=i,
                score=0.95 - i * 0.01,
            )
            for i in range(20)
        ]
        mock_response = SearchResponse(
            results=mock_results,
            total_count=20,
            latency_ms=150,
            filters_applied={},
        )
        mock_retriever.retrieve = AsyncMock(return_value=mock_response)

        response = client.post(
            "/api/v1/search",
            json={"query": "test", "top_k": 20},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 20
        assert len(data["results"]) == 20

    def test_search_with_top_k_50_max(self, client, mock_retriever):
        """Test search with top_k=50 (maximum allowed)."""
        from src.models import SearchResponse

        mock_response = SearchResponse(
            results=[],
            total_count=0,
            latency_ms=200,
            filters_applied={},
        )
        mock_retriever.retrieve = AsyncMock(return_value=mock_response)

        response = client.post(
            "/api/v1/search",
            json={"query": "test", "top_k": 50},
        )

        assert response.status_code == 200

    def test_search_with_top_k_51_exceeds_max(self, client):
        """Test search with top_k=51 exceeds maximum and returns error."""
        response = client.post(
            "/api/v1/search",
            json={"query": "test", "top_k": 51},
        )

        # Pydantic validation returns 422 for out-of-bounds
        assert response.status_code == 422

    def test_search_empty_results_no_matches(self, client, mock_retriever):
        """Test search returns empty results when no matches found (T030)."""
        from src.models import SearchResponse

        mock_response = SearchResponse(
            results=[],
            total_count=0,
            latency_ms=50,
            filters_applied={},
        )
        mock_retriever.retrieve = AsyncMock(return_value=mock_response)

        response = client.post(
            "/api/v1/search",
            json={"query": "xyznonexistentquery123"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 0
        assert data["results"] == []
        assert "latency_ms" in data

    def test_search_passes_top_k_to_retriever(self, client, mock_retriever):
        """Test that top_k parameter is correctly passed to retriever."""
        from src.models import SearchResponse

        mock_response = SearchResponse(
            results=[],
            total_count=0,
            latency_ms=100,
            filters_applied={},
        )
        mock_retriever.retrieve = AsyncMock(return_value=mock_response)

        client.post(
            "/api/v1/search",
            json={"query": "test", "top_k": 15},
        )

        # Verify the retriever was called with correct top_k
        mock_retriever.retrieve.assert_called_once()
        call_kwargs = mock_retriever.retrieve.call_args[1]
        assert call_kwargs["top_k"] == 15
