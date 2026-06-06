"""Pydantic schemas for API request/response models."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# Request models
class IngestRequest(BaseModel):
    """Request to trigger book ingestion."""

    base_url: str = Field(
        ...,
        description="Base URL of the deployed Docusaurus book",
        examples=["https://buttf8616-hub.github.io/humanoid-robotics-textbook"],
    )
    force: bool = Field(
        default=False,
        description="Force re-ingestion even if content hasn't changed",
    )


# Response models
class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Health status")
    timestamp: str = Field(..., description="Current timestamp")
    version: str = Field(..., description="API version")
    services: Optional[dict] = Field(None, description="Service statuses")


class IngestResponse(BaseModel):
    """Response after triggering ingestion."""

    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field(..., description="Job status")
    message: str = Field(..., description="Status message")


class ErrorDetail(BaseModel):
    """Error detail for job status."""

    url: str = Field(..., description="URL where error occurred")
    error_type: str = Field(..., description="Error classification")
    message: str = Field(..., description="Error message")
    timestamp: datetime = Field(..., description="When error occurred")


class JobStatusResponse(BaseModel):
    """Response for job status query."""

    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field(..., description="Current job status")
    started_at: datetime = Field(..., description="Job start time")
    completed_at: Optional[datetime] = Field(None, description="Job completion time")
    pages_total: int = Field(..., description="Total pages to process")
    pages_processed: int = Field(..., description="Pages processed so far")
    chunks_created: int = Field(..., description="Chunks created so far")
    errors: list[ErrorDetail] = Field(default_factory=list, description="Errors encountered")


class VerifyResponse(BaseModel):
    """Response for collection verification."""

    collection_name: str = Field(..., description="Qdrant collection name")
    vector_count: int = Field(..., description="Total vectors in collection")
    indexed_urls: int = Field(..., description="Number of unique URLs indexed")
    status: str = Field(..., description="Collection status")


class ChunkDetail(BaseModel):
    """Detail for a single chunk."""

    chunk_index: int = Field(..., description="Position in page")
    section: str = Field(..., description="Section header")
    token_count: int = Field(0, description="Token count")
    content_preview: str = Field(..., description="First 200 characters")


class UrlVerifyResponse(BaseModel):
    """Response for URL-specific verification."""

    url: str = Field(..., description="Source URL")
    chunk_count: int = Field(..., description="Number of chunks")
    chunks: list[ChunkDetail] = Field(..., description="Chunk details")


class ErrorResponse(BaseModel):
    """Generic error response."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[dict] = Field(None, description="Additional details")


# Retrieval API schemas
class SearchRequest(BaseModel):
    """Request for semantic search."""

    query: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Natural language search query",
        examples=["What is embodied intelligence?"],
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
        description="Filter by section name (substring match)",
    )


class RetrievalResultResponse(BaseModel):
    """Single retrieval result in API response."""

    content: str = Field(..., description="Chunk text content")
    url: str = Field(..., description="Source URL")
    title: str = Field(..., description="Page title")
    section: str = Field(..., description="Section header")
    chunk_index: int = Field(..., description="Position in page")
    score: float = Field(..., description="Relevance score (cosine similarity)")


class SearchResponseSchema(BaseModel):
    """Response for semantic search."""

    results: list[RetrievalResultResponse] = Field(
        ...,
        description="Matching chunks sorted by relevance",
    )
    total_count: int = Field(..., description="Number of results returned")
    latency_ms: float = Field(..., description="Processing time in milliseconds")
    filters_applied: dict = Field(
        default_factory=dict,
        description="Filters that were applied",
    )


# Agent/Chat schemas
class SourceCitationResponse(BaseModel):
    """Source citation in agent response."""

    url: str = Field(..., description="Source URL")
    title: str = Field(..., description="Page title")
    section: str = Field(..., description="Section header")
    chunk_index: int = Field(..., description="Position in page")
    score: float = Field(..., description="Relevance score (cosine similarity)")
    excerpt: str = Field(..., description="First 100 characters of chunk content")


class TokenUsage(BaseModel):
    """Token usage statistics."""

    prompt: int = Field(..., description="Prompt tokens used")
    completion: int = Field(..., description="Completion tokens used")
    total: int = Field(..., description="Total tokens used")


class SelectedContextSchema(BaseModel):
    """User-selected text context for focused answering."""

    url: str = Field(..., description="Exact URL to filter results to")
    section: Optional[str] = Field(
        default=None,
        description="Section name to filter (optional, substring match)",
    )


class ConversationMessage(BaseModel):
    """A message in the conversation history."""

    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Request to chat with the AI agent."""

    question: str = Field(
        ...,
        description="User's question about the textbook",
        min_length=1,
        examples=["What is embodied intelligence?"],
    )
    top_k: int = Field(
        default=5,
        description="Number of relevant chunks to retrieve (1-50)",
        ge=1,
        le=50,
    )
    selected_context: Optional[SelectedContextSchema] = Field(
        default=None,
        description="Optional context filter to limit answers to specific URL/section",
    )
    conversation_history: Optional[list[ConversationMessage]] = Field(
        default=None,
        description="Optional conversation history for context (last N messages)",
    )


class ChatResponse(BaseModel):
    """Response from the AI agent."""

    answer: str = Field(..., description="Generated answer text")
    sources: list[SourceCitationResponse] = Field(
        ...,
        description="Source citations used to generate the answer",
    )
    confidence: str = Field(
        ...,
        description="Confidence level: high, medium, low, or refused",
        examples=["high"],
    )
    latency_ms: float = Field(..., description="Total response time in milliseconds")
    tokens_used: TokenUsage = Field(..., description="Token usage statistics")
