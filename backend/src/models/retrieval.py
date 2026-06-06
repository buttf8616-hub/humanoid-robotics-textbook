"""Pydantic models for retrieval pipeline."""
from typing import Optional

from pydantic import BaseModel, Field


class SearchQuery(BaseModel):
    """Search query with optional filters."""

    query: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Search query text",
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Number of results to return",
    )
    url_filter: Optional[str] = Field(
        default=None,
        description="Filter by exact URL match",
    )
    section_filter: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Filter by section name (substring)",
    )


class RetrievalResult(BaseModel):
    """Single retrieval result with metadata."""

    content: str = Field(..., description="Chunk text content")
    url: str = Field(..., description="Source URL")
    title: str = Field(..., description="Page title")
    section: str = Field(..., description="Section header")
    chunk_index: int = Field(..., description="Position in page")
    score: float = Field(..., description="Relevance score")


class SearchResponse(BaseModel):
    """Search response with results and metadata."""

    results: list[RetrievalResult] = Field(..., description="Matching chunks")
    total_count: int = Field(..., description="Number of results")
    latency_ms: float = Field(..., description="Processing time in ms")
    filters_applied: dict = Field(
        default_factory=dict,
        description="Active filters",
    )
