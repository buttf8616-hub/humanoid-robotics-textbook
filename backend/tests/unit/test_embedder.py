"""Unit tests for embedder service."""
import pytest
from unittest.mock import MagicMock, patch

from src.services.embedder import EmbedderService
from src.models import TextChunk


class TestEmbedderService:
    """Tests for EmbedderService."""

    @pytest.fixture
    def embedder(self):
        """Create an EmbedderService instance with mocked client."""
        with patch("src.services.embedder.cohere") as mock_cohere:
            mock_client = MagicMock()
            mock_cohere.Client.return_value = mock_client
            service = EmbedderService(api_key="test-key")
            service._client = mock_client
            return service

    @pytest.fixture
    def sample_chunks(self):
        """Create sample text chunks."""
        return [
            TextChunk(
                content="Physical AI represents the integration of AI.",
                source_url="https://example.com/intro",
                title="Introduction",
                section="Overview",
                chunk_index=0,
                token_count=10,
                content_hash="abc123",
            ),
            TextChunk(
                content="Embodied intelligence is a key principle.",
                source_url="https://example.com/intro",
                title="Introduction",
                section="Key Concepts",
                chunk_index=1,
                token_count=8,
                content_hash="def456",
            ),
        ]

    def test_embed_chunks_returns_vectors(self, embedder, sample_chunks):
        """Test that embedding returns vectors for each chunk."""
        # Mock Cohere response
        mock_response = MagicMock()
        mock_response.embeddings = [[0.1] * 1024, [0.2] * 1024]
        embedder._client.embed.return_value = mock_response

        result = embedder.embed(sample_chunks)

        assert len(result) == 2
        assert len(result[0]) == 1024
        assert len(result[1]) == 1024

    def test_embed_chunks_batching(self, embedder):
        """Test that large lists are batched correctly."""
        # Create many chunks
        chunks = [
            TextChunk(
                content=f"Chunk {i}",
                source_url="https://example.com/page",
                title="Test",
                section="",
                chunk_index=i,
                token_count=5,
                content_hash=f"hash{i}",
            )
            for i in range(200)  # More than batch size
        ]

        mock_response = MagicMock()
        mock_response.embeddings = [[0.1] * 1024] * 96  # One batch worth
        embedder._client.embed.return_value = mock_response

        # Should make multiple API calls
        result = embedder.embed(chunks)

        # Client should be called multiple times for batching
        assert embedder._client.embed.call_count >= 2

    def test_embed_empty_list(self, embedder):
        """Test handling of empty chunk list."""
        result = embedder.embed([])
        assert result == []

    def test_embed_uses_correct_model(self, embedder, sample_chunks):
        """Test that correct embedding model is used."""
        mock_response = MagicMock()
        mock_response.embeddings = [[0.1] * 1024, [0.2] * 1024]
        embedder._client.embed.return_value = mock_response

        embedder.embed(sample_chunks)

        # Check that embed was called with correct model
        call_kwargs = embedder._client.embed.call_args[1]
        assert call_kwargs["model"] == "embed-english-v3.0"
        assert call_kwargs["input_type"] == "search_document"

    def test_embed_query_returns_vector(self, embedder):
        """Test that embed_query returns a vector for a search query."""
        mock_response = MagicMock()
        mock_response.embeddings = [[0.5] * 1024]
        embedder._client.embed.return_value = mock_response

        result = embedder.embed_query("What is embodied intelligence?")

        assert len(result) == 1024
        assert result[0] == 0.5

    def test_embed_query_uses_search_query_input_type(self, embedder):
        """Test that embed_query uses input_type='search_query' for asymmetric search."""
        mock_response = MagicMock()
        mock_response.embeddings = [[0.5] * 1024]
        embedder._client.embed.return_value = mock_response

        embedder.embed_query("ROS 2 architecture")

        call_kwargs = embedder._client.embed.call_args[1]
        assert call_kwargs["input_type"] == "search_query"
        assert call_kwargs["model"] == "embed-english-v3.0"

    def test_embed_query_raises_on_empty_query(self, embedder):
        """Test that embed_query raises ValueError for empty query."""
        with pytest.raises(ValueError, match="Query must not be empty"):
            embedder.embed_query("")

        with pytest.raises(ValueError, match="Query must not be empty"):
            embedder.embed_query("   ")

    def test_embed_query_single_text(self, embedder):
        """Test that embed_query sends single text to API."""
        mock_response = MagicMock()
        mock_response.embeddings = [[0.1] * 1024]
        embedder._client.embed.return_value = mock_response

        embedder.embed_query("sensor fusion")

        call_kwargs = embedder._client.embed.call_args[1]
        assert call_kwargs["texts"] == ["sensor fusion"]
