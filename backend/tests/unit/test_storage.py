"""Unit tests for storage service."""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock

from src.services.storage import StorageService
from src.models import TextChunk


class TestStorageService:
    """Tests for StorageService."""

    @pytest.fixture
    def storage(self):
        """Create a StorageService instance with mocked client."""
        with patch("src.services.storage.QdrantClient") as mock_qdrant:
            mock_client = MagicMock()
            mock_qdrant.return_value = mock_client
            service = StorageService(
                url="https://test.qdrant.io",
                api_key="test-key",
                collection_name="test-collection",
            )
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

    @pytest.fixture
    def sample_vectors(self):
        """Create sample embedding vectors."""
        return [[0.1] * 1024, [0.2] * 1024]

    def test_create_collection(self, storage):
        """Test collection creation."""
        storage._client.collection_exists.return_value = False

        storage.ensure_collection()

        storage._client.create_collection.assert_called_once()

    def test_skip_create_if_exists(self, storage):
        """Test that collection creation is skipped if exists."""
        storage._client.collection_exists.return_value = True

        storage.ensure_collection()

        storage._client.create_collection.assert_not_called()

    def test_upsert_vectors(self, storage, sample_chunks, sample_vectors):
        """Test upserting vectors."""
        storage.upsert(sample_chunks, sample_vectors)

        storage._client.upsert.assert_called_once()
        call_kwargs = storage._client.upsert.call_args[1]
        assert call_kwargs["collection_name"] == "test-collection"
        assert len(call_kwargs["points"]) == 2

    def test_upsert_uses_content_hash_as_id(self, storage, sample_chunks, sample_vectors):
        """Test that content_hash is used as point ID."""
        storage.upsert(sample_chunks, sample_vectors)

        call_kwargs = storage._client.upsert.call_args[1]
        points = call_kwargs["points"]

        # IDs should be content hashes
        ids = [p.id for p in points]
        assert "abc123" in ids
        assert "def456" in ids

    def test_upsert_includes_metadata(self, storage, sample_chunks, sample_vectors):
        """Test that metadata is included in payload."""
        storage.upsert(sample_chunks, sample_vectors)

        call_kwargs = storage._client.upsert.call_args[1]
        points = call_kwargs["points"]

        for point in points:
            assert "url" in point.payload
            assert "title" in point.payload
            assert "section" in point.payload
            assert "chunk_index" in point.payload
            assert "content" in point.payload
            assert "content_hash" in point.payload

    def test_get_collection_stats(self, storage):
        """Test getting collection statistics."""
        mock_info = MagicMock()
        mock_info.vectors_count = 100
        mock_info.points_count = 100
        storage._client.get_collection.return_value = mock_info

        stats = storage.get_stats()

        assert stats["vector_count"] == 100

    def test_get_chunks_by_url(self, storage):
        """Test retrieving chunks for a specific URL."""
        mock_result = [
            MagicMock(
                id="abc123",
                payload={
                    "url": "https://example.com/intro",
                    "title": "Introduction",
                    "section": "Overview",
                    "chunk_index": 0,
                    "content": "Test content",
                    "content_hash": "abc123",
                },
            )
        ]
        storage._client.scroll.return_value = (mock_result, None)

        chunks = storage.get_chunks_by_url("https://example.com/intro")

        assert len(chunks) == 1
        assert chunks[0]["url"] == "https://example.com/intro"

    def test_deduplication_on_reingestion(self, storage, sample_chunks, sample_vectors):
        """Test that re-ingestion updates existing vectors (no duplicates)."""
        # First upsert
        storage.upsert(sample_chunks, sample_vectors)

        # Second upsert with same hashes
        storage.upsert(sample_chunks, sample_vectors)

        # Should use upsert which handles deduplication
        assert storage._client.upsert.call_count == 2
