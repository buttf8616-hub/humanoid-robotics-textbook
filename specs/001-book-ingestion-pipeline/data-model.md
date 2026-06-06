# Data Model: Book Ingestion Pipeline

**Feature**: 001-book-ingestion-pipeline
**Date**: 2025-01-07

## Entity Definitions

### BookPage

Represents a single page from the deployed Docusaurus book.

| Field | Type | Description |
|-------|------|-------------|
| url | string | Full URL of the page |
| title | string | Page title (from h1 or meta) |
| raw_html | string | Raw HTML content |
| extracted_text | string | Clean text after extraction |
| sections | list[Section] | Parsed sections with headers |
| fetched_at | datetime | Timestamp of fetch |

### Section

Represents a section within a page.

| Field | Type | Description |
|-------|------|-------------|
| header | string | Section header text (h2/h3) |
| level | int | Header level (2 or 3) |
| content | string | Text content under this header |

### TextChunk

A segment of text ready for embedding.

| Field | Type | Description |
|-------|------|-------------|
| content | string | Chunk text content |
| source_url | string | URL of source page |
| title | string | Page title |
| section | string | Section header (if applicable) |
| chunk_index | int | Position in page (0-indexed) |
| token_count | int | Number of tokens in chunk |
| content_hash | string | SHA-256 hash for deduplication |

### VectorRecord

An embedding stored in Qdrant.

| Field | Type | Description |
|-------|------|-------------|
| id | string | Point ID (content_hash) |
| vector | list[float] | 1024-dim embedding vector |
| payload | dict | Metadata payload |

**Payload Structure**:
```json
{
  "url": "https://...",
  "title": "Chapter Title",
  "section": "Section Header",
  "chunk_index": 0,
  "content": "The chunk text...",
  "content_hash": "sha256...",
  "ingested_at": "2025-01-07T12:00:00Z"
}
```

### IngestionJob

Tracks the status of an ingestion run.

| Field | Type | Description |
|-------|------|-------------|
| job_id | string | Unique job identifier (UUID) |
| status | enum | pending, running, completed, failed |
| started_at | datetime | Job start timestamp |
| completed_at | datetime | Job completion timestamp (nullable) |
| pages_total | int | Total pages to process |
| pages_processed | int | Pages successfully processed |
| chunks_created | int | Total chunks created |
| errors | list[Error] | List of errors encountered |

### Error

Represents an error during ingestion.

| Field | Type | Description |
|-------|------|-------------|
| url | string | URL where error occurred |
| error_type | string | Error classification |
| message | string | Error message |
| timestamp | datetime | When error occurred |

## Qdrant Collection Schema

**Collection Name**: `book-chunks`

**Configuration**:
```json
{
  "vectors": {
    "size": 1024,
    "distance": "Cosine"
  },
  "payload_schema": {
    "url": "keyword",
    "title": "keyword",
    "section": "keyword",
    "chunk_index": "integer",
    "content": "text",
    "content_hash": "keyword",
    "ingested_at": "datetime"
  }
}
```

## Pydantic Models (API)

### Request Models

```python
class IngestRequest(BaseModel):
    base_url: str = Field(..., description="Base URL of deployed book")
    force: bool = Field(False, description="Force re-ingestion of all pages")

class VerifyUrlRequest(BaseModel):
    url: str = Field(..., description="URL to verify")
```

### Response Models

```python
class IngestResponse(BaseModel):
    job_id: str
    status: str
    message: str

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    pages_total: int
    pages_processed: int
    chunks_created: int
    errors: List[ErrorDetail]

class VerifyResponse(BaseModel):
    collection_name: str
    vector_count: int
    indexed_urls: int
    status: str

class ChunkDetail(BaseModel):
    chunk_index: int
    section: str
    token_count: int
    content_preview: str  # First 200 chars

class UrlVerifyResponse(BaseModel):
    url: str
    chunk_count: int
    chunks: List[ChunkDetail]
```

## Data Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Docusaurus │────▶│  BookPage   │────▶│  Section[]  │
│   Website   │     │  (raw HTML) │     │  (parsed)   │
└─────────────┘     └─────────────┘     └─────────────┘
                                              │
                                              ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Qdrant    │◀────│  Embedding  │◀────│ TextChunk[] │
│   Cloud     │     │   Vector    │     │  (chunked)  │
└─────────────┘     └─────────────┘     └─────────────┘
```
