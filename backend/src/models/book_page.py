"""BookPage model representing a page from the deployed book."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Section(BaseModel):
    """A section within a page."""

    header: str = Field(..., description="Section header text")
    level: int = Field(..., ge=1, le=6, description="Header level (1-6)")
    content: str = Field(..., description="Text content under this header")


class BookPage(BaseModel):
    """Represents a single page from the deployed Docusaurus book."""

    url: str = Field(..., description="Full URL of the page")
    title: str = Field(..., description="Page title")
    raw_html: str = Field(..., description="Raw HTML content")
    extracted_text: Optional[str] = Field(None, description="Clean text after extraction")
    sections: list[Section] = Field(default_factory=list, description="Parsed sections")
    fetched_at: datetime = Field(default_factory=datetime.utcnow, description="Fetch timestamp")
