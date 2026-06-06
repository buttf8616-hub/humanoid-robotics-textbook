# Data Model: RAG Retrieval Pipeline

**Feature**: 002-retrieval-pipeline
**Date**: 2026-01-08

## Entity Definitions

### SearchQuery

Represents a user's search request.

| Attribute | Type | Required | Default | Constraints |
|-----------|------|----------|---------|-------------|
| query | string | Yes | - | Non-empty, max 1000 chars |
| top_k | integer | No | 5 | Min 1, max 50 |
| url_filter | string | No | null | Valid URL if provided |
| section_filter | string | No | null | Max 200 chars |

**Validation Rules**:
- `query` must not be empty or whitespace-only
- `top_k` must be within bounds [1, 50]
- Filters are optional and independent

---

### RetrievalResult

Represents a single matching chunk from the vector database.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| content | string | Yes | Full chunk text content |
| url | string | Yes | Source page URL |
| title | string | Yes | Page title |
| section | string | Yes | Section header (may be empty) |
| chunk_index | integer | Yes | Position within source page |
| score | float | Yes | Relevance score (cosine similarity) |

**Score Interpretation**:
- Range: -1.0 to 1.0 (cosine similarity)
- Higher is more relevant
- Typical thresholds: 0.8+ high, 0.6-0.8 moderate, <0.6 low

---

### SearchResponse

Contains search results with metadata.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| results | list[RetrievalResult] | Yes | Matching chunks, sorted by score desc |
| total_count | integer | Yes | Number of results returned |
| latency_ms | float | Yes | Total processing time in milliseconds |
| filters_applied | dict | Yes | Active filters (url_filter, section_filter) |

**Response Invariants**:
- `total_count` == `len(results)`
- `results` sorted by `score` descending
- `latency_ms` includes embedding + search time

---

## Relationship to Spec 001 Entities

### Existing: TextChunk (from Spec 001)

The retrieval pipeline queries chunks stored during ingestion:

| Payload Field | Maps To |
|---------------|---------|
| content | RetrievalResult.content |
| url | RetrievalResult.url |
| title | RetrievalResult.title |
| section | RetrievalResult.section |
| chunk_index | RetrievalResult.chunk_index |

The `score` field is computed during search (not stored).

---

## Pydantic Model Definitions

```python
# src/models/retrieval.py

from pydantic import BaseModel, Field
from typing import Optional

class SearchQuery(BaseModel):
    """Search query with optional filters."""
    query: str = Field(..., min_length=1, max_length=1000, description="Search query text")
    top_k: int = Field(default=5, ge=1, le=50, description="Number of results to return")
    url_filter: Optional[str] = Field(default=None, description="Filter by exact URL match")
    section_filter: Optional[str] = Field(default=None, max_length=200, description="Filter by section name (substring)")


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
    filters_applied: dict = Field(default_factory=dict, description="Active filters")
```

---

## Data Flow

```
User Query
    │
    ▼
┌─────────────┐
│ SearchQuery │  ← Validated input
└─────────────┘
    │
    ▼
┌─────────────┐
│ Cohere API  │  ← Embed query (search_query type)
└─────────────┘
    │
    ▼
┌─────────────┐
│ Qdrant      │  ← Vector search + filters
└─────────────┘
    │
    ▼
┌─────────────────┐
│ RetrievalResult │  ← For each matching point
└─────────────────┘
    │
    ▼
┌────────────────┐
│ SearchResponse │  ← Aggregated response
└────────────────┘
```
