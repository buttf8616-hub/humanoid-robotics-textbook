"""Embedding service using Cohere API."""
import asyncio
import logging
from typing import Optional

import cohere

from src.config import settings
from src.models import TextChunk

logger = logging.getLogger(__name__)


class EmbedderService:
    """Service for generating embeddings using Cohere."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        batch_size: Optional[int] = None,
    ):
        """Initialize the embedder.

        Args:
            api_key: Cohere API key. Defaults to settings.
            model: Embedding model name. Defaults to settings.
            batch_size: Batch size for API calls. Defaults to settings.
        """
        self.api_key = api_key or settings.cohere_api_key
        self.model = model or settings.embedding_model
        self.batch_size = batch_size or settings.embedding_batch_size
        self._client: Optional[cohere.Client] = None

    def _get_client(self) -> cohere.Client:
        """Get or create the Cohere client."""
        if self._client is None:
            self._client = cohere.Client(self.api_key)
        return self._client

    def embed(self, chunks: list[TextChunk]) -> list[list[float]]:
        """Generate embeddings for text chunks.

        Args:
            chunks: List of TextChunk objects.

        Returns:
            List of embedding vectors (1024 dimensions each).
        """
        if not chunks:
            return []

        client = self._get_client()
        all_embeddings = []

        # Process in batches
        for i in range(0, len(chunks), self.batch_size):
            batch = chunks[i : i + self.batch_size]
            texts = [chunk.content for chunk in batch]

            try:
                response = client.embed(
                    texts=texts,
                    model=self.model,
                    input_type="search_document",
                )
                all_embeddings.extend(response.embeddings)
                logger.debug(f"Generated embeddings for batch {i // self.batch_size + 1}")

            except cohere.CohereAPIError as e:
                logger.error(f"Cohere API error: {e}")
                raise

            except Exception as e:
                logger.error(f"Embedding error: {e}")
                raise

        logger.info(f"Generated {len(all_embeddings)} embeddings")
        return all_embeddings

    async def embed_async(
        self, chunks: list[TextChunk], retry_delay: float = 1.0, max_retries: int = 3
    ) -> list[list[float]]:
        """Generate embeddings asynchronously with retry logic."""
        if not chunks:
            return []

        loop = asyncio.get_event_loop()
        client = self._get_client()
        all_embeddings = []

        for i in range(0, len(chunks), self.batch_size):
            batch = chunks[i : i + self.batch_size]
            texts = [chunk.content for chunk in batch]

            for attempt in range(max_retries):
                try:
                    # Run sync Cohere call in thread pool to avoid blocking the event loop
                    response = await loop.run_in_executor(
                        None,
                        lambda t=texts: client.embed(
                            texts=t,
                            model=self.model,
                            input_type="search_document",
                        ),
                    )
                    all_embeddings.extend(response.embeddings)
                    logger.debug(f"Generated embeddings for batch {i // self.batch_size + 1}")
                    break

                except cohere.CohereAPIError as e:
                    if "rate" in str(e).lower() and attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)
                        logger.warning(f"Rate limited, waiting {wait_time}s")
                        await asyncio.sleep(wait_time)
                    else:
                        raise

        logger.info(f"Generated {len(all_embeddings)} embeddings")
        return all_embeddings

    def embed_query(self, query: str) -> list[float]:
        """Embed a search query using search_query input type.

        Uses input_type="search_query" for asymmetric search optimization.

        Args:
            query: The search query text.

        Returns:
            Embedding vector (1024 dimensions).
        """
        if not query or not query.strip():
            raise ValueError("Query must not be empty")

        client = self._get_client()

        try:
            response = client.embed(
                texts=[query],
                model=self.model,
                input_type="search_query",
            )
            logger.debug(f"Generated query embedding for: {query[:50]}...")
            return response.embeddings[0]

        except cohere.CohereAPIError as e:
            logger.error(f"Cohere API error during query embedding: {e}")
            raise

        except Exception as e:
            logger.error(f"Query embedding error: {e}")
            raise

    async def embed_query_async(
        self, query: str, retry_delay: float = 1.0, max_retries: int = 3
    ) -> list[float]:
        """Embed a search query asynchronously with retry logic."""
        if not query or not query.strip():
            raise ValueError("Query must not be empty")

        loop = asyncio.get_event_loop()
        client = self._get_client()

        for attempt in range(max_retries):
            try:
                response = await loop.run_in_executor(
                    None,
                    lambda q=query: client.embed(
                        texts=[q],
                        model=self.model,
                        input_type="search_query",
                    ),
                )
                logger.debug(f"Generated query embedding for: {query[:50]}...")
                return response.embeddings[0]

            except cohere.CohereAPIError as e:
                if "rate" in str(e).lower() and attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)
                    logger.warning(f"Rate limited on query embedding, waiting {wait_time}s")
                    await asyncio.sleep(wait_time)
                else:
                    raise

        raise RuntimeError("Max retries exceeded for query embedding")
