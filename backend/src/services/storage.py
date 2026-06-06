"""Qdrant storage service for vector operations."""
import logging
import uuid
from datetime import datetime
from typing import Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models

from src.config import settings
from src.models import TextChunk

logger = logging.getLogger(__name__)


class StorageService:
    """Service for storing and retrieving vectors from Qdrant."""

    def __init__(
        self,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        collection_name: Optional[str] = None,
    ):
        """Initialize the storage service.

        Args:
            url: Qdrant server URL. Defaults to settings.
            api_key: Qdrant API key. Defaults to settings.
            collection_name: Collection name. Defaults to settings.
        """
        self.url = url or settings.qdrant_url
        self.api_key = api_key or settings.qdrant_api_key
        self.collection_name = collection_name or settings.qdrant_collection_name
        self._client: Optional[QdrantClient] = None

    def _get_client(self) -> QdrantClient:
        """Get or create the Qdrant client."""
        if self._client is None:
            self._client = QdrantClient(
                url=self.url,
                api_key=self.api_key,
            )
        return self._client

    def ensure_collection(self) -> None:
        """Create collection if it doesn't exist."""
        client = self._get_client()

        if not client.collection_exists(self.collection_name):
            client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=settings.embedding_dimension,
                    distance=models.Distance.COSINE,
                ),
            )
            logger.info(f"Created collection: {self.collection_name}")
        else:
            logger.debug(f"Collection exists: {self.collection_name}")

    def upsert(self, chunks: list[TextChunk], vectors: list[list[float]]) -> int:
        """Upsert vectors with metadata.

        Uses content_hash as point ID for automatic deduplication.

        Args:
            chunks: List of TextChunk objects.
            vectors: List of embedding vectors.

        Returns:
            Number of points upserted.
        """
        if not chunks or not vectors:
            return 0

        if len(chunks) != len(vectors):
            raise ValueError(f"Chunks ({len(chunks)}) and vectors ({len(vectors)}) must have same length")

        client = self._get_client()

        points = []
        for chunk, vector in zip(chunks, vectors):
            # Qdrant IDs must be uint64 or UUID; derive a deterministic UUID from the SHA-256 hash
            point_id = str(uuid.UUID(hex=chunk.content_hash[:32]))
            point = models.PointStruct(
                id=point_id,  # Use hash-derived UUID for deduplication
                vector=vector,
                payload={
                    "url": chunk.source_url,
                    "title": chunk.title,
                    "section": chunk.section,
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content,
                    "content_hash": chunk.content_hash,
                    "ingested_at": datetime.utcnow().isoformat(),
                },
            )
            points.append(point)

        try:
            client.upsert(
                collection_name=self.collection_name,
                points=points,
            )
        except Exception as exc:
            logger.error(f"Qdrant upsert failed: {exc}")
            raise

        logger.info(f"Upserted {len(points)} vectors")
        return len(points)

    def get_stats(self) -> dict:
        """Get collection statistics.

        Returns:
            Dict with collection stats.
        """
        client = self._get_client()

        try:
            info = client.get_collection(self.collection_name)
            # Newer qdrant-client versions expose counts under different attributes
            count = (
                getattr(info, "points_count", None)
                or getattr(info, "vectors_count", None)
                or 0
            )
            return {
                "collection_name": self.collection_name,
                "vector_count": count,
                "points_count": count,
                "status": "ready",
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {
                "collection_name": self.collection_name,
                "vector_count": 0,
                "points_count": 0,
                "status": "error",
                "error": str(e),
            }

    def get_chunks_by_url(self, url: str, limit: int = 100) -> list[dict]:
        """Get all chunks for a specific URL.

        Args:
            url: URL to filter by.
            limit: Maximum chunks to return.

        Returns:
            List of chunk payloads.
        """
        client = self._get_client()

        try:
            results, _ = client.scroll(
                collection_name=self.collection_name,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="url",
                            match=models.MatchValue(value=url),
                        )
                    ]
                ),
                limit=limit,
                with_payload=True,
            )

            return [point.payload for point in results]

        except Exception as e:
            logger.error(f"Failed to get chunks by URL: {e}")
            return []

    def get_unique_urls(self) -> list[str]:
        """Get list of unique URLs in the collection.

        Returns:
            List of unique source URLs.
        """
        client = self._get_client()

        try:
            # Scroll through all points and collect unique URLs
            urls = set()
            offset = None

            while True:
                results, offset = client.scroll(
                    collection_name=self.collection_name,
                    limit=100,
                    offset=offset,
                    with_payload=["url"],
                )

                for point in results:
                    if point.payload and "url" in point.payload:
                        urls.add(point.payload["url"])

                if offset is None:
                    break

            return list(urls)

        except Exception as e:
            logger.error(f"Failed to get unique URLs: {e}")
            return []

    def delete_by_url(self, url: str) -> int:
        """Delete all vectors for a specific URL.

        Args:
            url: URL to delete vectors for.

        Returns:
            Number of deleted points.
        """
        client = self._get_client()

        try:
            result = client.delete(
                collection_name=self.collection_name,
                points_selector=models.FilterSelector(
                    filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="url",
                                match=models.MatchValue(value=url),
                            )
                        ]
                    )
                ),
            )
            logger.info(f"Deleted vectors for URL: {url}")
            return 1  # Qdrant doesn't return count, return success indicator

        except Exception as e:
            logger.error(f"Failed to delete by URL: {e}")
            return 0

    def search(
        self,
        query_vector: list[float],
        top_k: int = 5,
        url_filter: Optional[str] = None,
        section_filter: Optional[str] = None,
    ) -> list[dict]:
        """Search for similar vectors with optional metadata filters.

        Args:
            query_vector: The query embedding vector.
            top_k: Number of results to return.
            url_filter: Filter by exact URL match.
            section_filter: Filter by section name (substring match).

        Returns:
            List of matching chunks with scores and payloads.
        """
        client = self._get_client()

        # Build filter conditions
        must_conditions = []

        if url_filter:
            must_conditions.append(
                models.FieldCondition(
                    key="url",
                    match=models.MatchValue(value=url_filter),
                )
            )

        if section_filter:
            must_conditions.append(
                models.FieldCondition(
                    key="section",
                    match=models.MatchText(text=section_filter),
                )
            )

        search_filter = models.Filter(must=must_conditions) if must_conditions else None

        try:
            response = client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=top_k,
                query_filter=search_filter,
                with_payload=True,
            )
            results = response.points

            logger.info(f"Search returned {len(results)} results")

            return [
                {
                    "score": result.score,
                    "content": (result.payload or {}).get("content", ""),
                    "url": (result.payload or {}).get("url", ""),
                    "title": (result.payload or {}).get("title", ""),
                    "section": (result.payload or {}).get("section", ""),
                    "chunk_index": (result.payload or {}).get("chunk_index", 0),
                }
                for result in results
            ]

        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
