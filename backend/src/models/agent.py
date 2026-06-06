"""Data models for AI agent interactions."""
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class AgentMessage(BaseModel):
    """A single message in a conversation."""

    role: Literal["user", "assistant"] = Field(
        ...,
        description="The role of the message sender",
    )
    content: str = Field(
        ...,
        description="The message content",
    )
    sources: list["SourceCitation"] = Field(
        default_factory=list,
        description="Source citations (only for assistant messages)",
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the message was created",
    )


class SelectedContext(BaseModel):
    """User-selected text context for focused answering."""

    url: str = Field(
        ...,
        description="Exact URL to filter results to",
    )
    section: Optional[str] = Field(
        default=None,
        description="Section name to filter (optional, substring match)",
    )


class SourceCitation(BaseModel):
    """A citation to a source in the textbook."""

    url: str = Field(
        ...,
        description="Source URL",
    )
    title: str = Field(
        ...,
        description="Page title",
    )
    section: str = Field(
        ...,
        description="Section header",
    )
    chunk_index: int = Field(
        ...,
        description="Position in page",
    )
    score: float = Field(
        ...,
        description="Relevance score (cosine similarity)",
    )
    excerpt: str = Field(
        default="",
        description="First 100 characters of chunk content",
    )


# Update forward references
AgentMessage.model_rebuild()
