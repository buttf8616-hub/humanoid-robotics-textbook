"""TextChunk model representing a segment of text ready for embedding."""
from pydantic import BaseModel, Field


class TextChunk(BaseModel):
    """A segment of text ready for embedding."""

    content: str = Field(..., description="Chunk text content")
    source_url: str = Field(..., description="URL of source page")
    title: str = Field(..., description="Page title")
    section: str = Field("", description="Section header if applicable")
    chunk_index: int = Field(..., ge=0, description="Position in page (0-indexed)")
    token_count: int = Field(..., ge=0, description="Number of tokens in chunk")
    content_hash: str = Field(..., description="SHA-256 hash for deduplication")
