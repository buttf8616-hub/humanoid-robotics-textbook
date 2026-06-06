"""IngestionJob model for tracking ingestion status."""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    """Status of an ingestion job."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class IngestionError(BaseModel):
    """Represents an error during ingestion."""

    url: str = Field(..., description="URL where error occurred")
    error_type: str = Field(..., description="Error classification")
    message: str = Field(..., description="Error message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When error occurred")


class IngestionJob(BaseModel):
    """Tracks the status of an ingestion run."""

    job_id: str = Field(..., description="Unique job identifier (UUID)")
    status: JobStatus = Field(default=JobStatus.PENDING, description="Current job status")
    started_at: datetime = Field(default_factory=datetime.utcnow, description="Job start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Job completion timestamp")
    pages_total: int = Field(default=0, description="Total pages to process")
    pages_processed: int = Field(default=0, description="Pages successfully processed")
    chunks_created: int = Field(default=0, description="Total chunks created")
    errors: list[IngestionError] = Field(default_factory=list, description="Errors encountered")
