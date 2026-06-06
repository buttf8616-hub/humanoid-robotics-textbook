"""Pydantic models for the ingestion pipeline."""
from .agent import AgentMessage, SelectedContext, SourceCitation
from .book_page import BookPage, Section
from .ingestion_job import IngestionError, IngestionJob, JobStatus
from .retrieval import RetrievalResult, SearchQuery, SearchResponse
from .text_chunk import TextChunk
from .vector_record import VectorPayload, VectorRecord

__all__ = [
    "BookPage",
    "Section",
    "TextChunk",
    "VectorRecord",
    "VectorPayload",
    "IngestionJob",
    "IngestionError",
    "JobStatus",
    "SearchQuery",
    "RetrievalResult",
    "SearchResponse",
    "AgentMessage",
    "SelectedContext",
    "SourceCitation",
]
