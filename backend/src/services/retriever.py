"""Retriever service for semantic search orchestration."""
import logging
import time
from typing import Optional

from src.config import settings
from src.models import RetrievalResult, SearchResponse
from src.services.embedder import EmbedderService
from src.services.storage import StorageService

logger = logging.getLogger(__name__)


class RetrieverService:
    """Service for orchestrating semantic search over book content."""

    def __init__(
        self,
        embedder: Optional[EmbedderService] = None,
        storage: Optional[StorageService] = None,
    ):
        """Initialize the retriever service.

        Args:
            embedder: Optional EmbedderService instance. Creates new if not provided.
            storage: Optional StorageService instance. Creates new if not provided.
        """
        self.embedder = embedder or EmbedderService()
        self.storage = storage or StorageService()

    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        url_filter: Optional[str] = None,
        section_filter: Optional[str] = None,
    ) -> SearchResponse:
        """Retrieve relevant chunks for a search query.

        Orchestrates the full retrieval pipeline:
        1. Validate parameters
        2. Embed the query using Cohere
        3. Search Qdrant for similar vectors
        4. Format and return results with metadata

        Args:
            query: The natural language search query.
            top_k: Number of results to return. Default 5, max 50.
            url_filter: Optional exact URL filter.
            section_filter: Optional section name substring filter.

        Returns:
            SearchResponse with results, count, latency, and filters.

        Raises:
            ValueError: If query is empty or top_k is out of bounds.
        """
        start_time = time.perf_counter()

        # Validate parameters
        if not query or not query.strip():
            raise ValueError("Query must not be empty")

        if top_k < 1 or top_k > settings.retrieval_max_top_k:
            raise ValueError(
                f"top_k must be between 1 and {settings.retrieval_max_top_k}"
            )

        logger.info(
            f"Retrieval request: query='{query[:50]}...', top_k={top_k}, "
            f"url_filter={url_filter}, section_filter={section_filter}"
        )

        # Embed the query
        query_vector = self.embedder.embed_query(query)

        # Search for similar vectors
        search_results = self.storage.search(
            query_vector=query_vector,
            top_k=top_k,
            url_filter=url_filter,
            section_filter=section_filter,
        )

        # Map results to RetrievalResult objects
        results = [
            RetrievalResult(
                content=r["content"],
                url=r["url"],
                title=r["title"],
                section=r["section"],
                chunk_index=r["chunk_index"],
                score=r["score"],
            )
            for r in search_results
        ]

        # Calculate latency
        latency_ms = (time.perf_counter() - start_time) * 1000

        # Build filters_applied dict
        filters_applied = {}
        if url_filter:
            filters_applied["url_filter"] = url_filter
        if section_filter:
            filters_applied["section_filter"] = section_filter

        logger.info(
            f"Retrieval complete: {len(results)} results in {latency_ms:.2f}ms"
        )

        return SearchResponse(
            results=results,
            total_count=len(results),
            latency_ms=latency_ms,
            filters_applied=filters_applied,
        )
