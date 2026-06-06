"""Text chunking service for preparing content for embedding."""
import hashlib
import logging
from typing import Optional

import tiktoken

from src.config import settings
from src.models import TextChunk

logger = logging.getLogger(__name__)


class ChunkerService:
    """Service for chunking text into embedding-ready segments."""

    def __init__(
        self,
        max_tokens: Optional[int] = None,
        overlap_tokens: Optional[int] = None,
        min_tokens: Optional[int] = None,
    ):
        """Initialize the chunker.

        Args:
            max_tokens: Maximum tokens per chunk. Defaults to settings.
            overlap_tokens: Overlap between chunks. Defaults to settings.
            min_tokens: Minimum tokens for final chunk. Defaults to settings.
        """
        self.max_tokens = max_tokens or settings.chunk_max_tokens
        self.overlap_tokens = overlap_tokens or settings.chunk_overlap_tokens
        self.min_tokens = min_tokens or settings.chunk_min_tokens

        # Use cl100k_base tokenizer (same as GPT-4, similar to Cohere)
        self._tokenizer = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """Count tokens in text.

        Args:
            text: Text to count tokens for.

        Returns:
            Number of tokens.
        """
        return len(self._tokenizer.encode(text))

    def generate_hash(self, content: str) -> str:
        """Generate SHA-256 hash of content.

        Args:
            content: Content to hash.

        Returns:
            Hex digest of hash.
        """
        return hashlib.sha256(content.encode()).hexdigest()

    def chunk(
        self,
        text: str,
        source_url: str,
        title: str,
        section: str = "",
    ) -> list[TextChunk]:
        """Chunk text into segments.

        Args:
            text: Text to chunk.
            source_url: Source URL for metadata.
            title: Page title for metadata.
            section: Section header for metadata.

        Returns:
            List of TextChunk objects.
        """
        if not text or not text.strip():
            return []

        text = text.strip()
        tokens = self._tokenizer.encode(text)

        # If text fits in one chunk, return as-is
        if len(tokens) <= self.max_tokens:
            return [
                TextChunk(
                    content=text,
                    source_url=source_url,
                    title=title,
                    section=section,
                    chunk_index=0,
                    token_count=len(tokens),
                    content_hash=self.generate_hash(text),
                )
            ]

        # Split into chunks with overlap
        chunks = []
        chunk_index = 0
        start = 0

        while start < len(tokens):
            # Calculate end position
            end = min(start + self.max_tokens, len(tokens))

            # Get chunk tokens and decode back to text
            chunk_tokens = tokens[start:end]
            chunk_text = self._tokenizer.decode(chunk_tokens)

            # Create chunk
            chunk = TextChunk(
                content=chunk_text.strip(),
                source_url=source_url,
                title=title,
                section=section,
                chunk_index=chunk_index,
                token_count=len(chunk_tokens),
                content_hash=self.generate_hash(chunk_text),
            )
            chunks.append(chunk)

            # Move to next position with overlap
            start = end - self.overlap_tokens
            chunk_index += 1

            # Stop once we've consumed all tokens
            if end >= len(tokens):
                break

        # Handle small final chunk by merging with previous
        if len(chunks) > 1 and chunks[-1].token_count < self.min_tokens:
            # Merge last two chunks
            last = chunks.pop()
            prev = chunks.pop()

            merged_text = prev.content + " " + last.content
            merged_tokens = self.count_tokens(merged_text)

            # If merged chunk is too big, keep them separate
            if merged_tokens > self.max_tokens * 1.2:  # Allow 20% overflow for merging
                chunks.append(prev)
                chunks.append(last)
            else:
                merged = TextChunk(
                    content=merged_text,
                    source_url=source_url,
                    title=title,
                    section=section,
                    chunk_index=prev.chunk_index,
                    token_count=merged_tokens,
                    content_hash=self.generate_hash(merged_text),
                )
                chunks.append(merged)

        # Re-index chunks
        for i, chunk in enumerate(chunks):
            chunk.chunk_index = i

        logger.debug(f"Created {len(chunks)} chunks from text with {len(tokens)} tokens")
        return chunks

    def chunk_page(self, text: str, source_url: str, title: str, sections: list) -> list[TextChunk]:
        """Chunk a page, respecting section boundaries.

        Args:
            text: Full page text.
            source_url: Source URL.
            title: Page title.
            sections: List of Section objects.

        Returns:
            List of TextChunk objects.
        """
        all_chunks = []

        if sections:
            # Chunk each section separately to preserve structure
            for section in sections:
                section_chunks = self.chunk(
                    text=section.content,
                    source_url=source_url,
                    title=title,
                    section=section.header,
                )
                all_chunks.extend(section_chunks)
        else:
            # No sections, chunk the whole text
            all_chunks = self.chunk(
                text=text,
                source_url=source_url,
                title=title,
            )

        # Re-index all chunks
        for i, chunk in enumerate(all_chunks):
            chunk.chunk_index = i

        return all_chunks
