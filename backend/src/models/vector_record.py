"""VectorRecord model representing an embedding stored in Qdrant."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class VectorPayload(BaseModel):
    """Metadata payload stored with each vector in Qdrant."""

    url: str = Field(..., description="Source page URL")
    title: str = Field(..., description="Page title")
    section: str = Field("", description="Section header")
    chunk_index: int = Field(..., description="Chunk position in page")
    content: str = Field(..., description="Chunk text content")
    content_hash: str = Field(..., description="SHA-256 hash of content")
    ingested_at: datetime = Field(default_factory=datetime.utcnow, description="Ingestion timestamp")


class VectorRecord(BaseModel):
    """An embedding stored in Qdrant."""

    id: str = Field(..., description="Point ID (content_hash)")
    vector: list[float] = Field(..., description="1024-dim embedding vector")
    payload: VectorPayload = Field(..., description="Metadata payload")
