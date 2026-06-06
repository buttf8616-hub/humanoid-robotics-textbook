# Feature Specification: Book Ingestion Pipeline

**Feature Branch**: `001-book-ingestion-pipeline`
**Created**: 2025-01-07
**Status**: Draft
**Input**: User description: "Deploy Docusaurus book URL ingestion, Cohere embeddings generation, and Qdrant vector storage"

## Overview

Automated pipeline to crawl the deployed Physical AI & Humanoid Robotics book website, extract readable content from all published pages, chunk the text appropriately, generate embeddings using Cohere models, and store vectors with metadata in Qdrant Cloud for downstream retrieval operations.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Full Book Ingestion (Priority: P1)

As a system operator, I want to trigger a complete ingestion of all published book pages so that the entire book content is available as searchable vectors in Qdrant.

**Why this priority**: This is the core functionality - without full book ingestion, no retrieval or chat features can work. It's the foundation for the entire RAG system.

**Independent Test**: Can be fully tested by triggering the ingestion endpoint and verifying all 15+ chapters are stored in Qdrant with correct metadata.

**Acceptance Scenarios**:

1. **Given** the book is deployed at a known URL, **When** the ingestion endpoint is triggered, **Then** all published book pages are crawled and processed
2. **Given** a page contains valid content, **When** text extraction occurs, **Then** clean text without HTML tags or navigation elements is produced
3. **Given** extracted text exceeds chunk size limits, **When** chunking occurs, **Then** text is split into chunks <1000 tokens with appropriate overlap

---

### User Story 2 - Embedding Generation & Storage (Priority: P1)

As a system operator, I want each text chunk to be converted into a vector embedding and stored in Qdrant so that semantic search can be performed later.

**Why this priority**: Without embeddings stored in the vector database, retrieval is impossible. This is equally critical as ingestion.

**Independent Test**: Can be tested by verifying Qdrant collection contains vectors with correct dimensions matching Cohere's embedding model output.

**Acceptance Scenarios**:

1. **Given** a text chunk is ready, **When** embedding generation is requested, **Then** Cohere API returns a valid embedding vector
2. **Given** a valid embedding is generated, **When** storage is attempted, **Then** the vector is stored in Qdrant with associated metadata
3. **Given** metadata includes url, title, section, and chunk_index, **When** vector is stored, **Then** all metadata fields are queryable

---

### User Story 3 - Duplicate Prevention (Priority: P2)

As a system operator, I want the system to detect and skip duplicate content so that the vector database remains clean and storage-efficient.

**Why this priority**: Prevents storage bloat and ensures retrieval quality. Important but not blocking for initial functionality.

**Independent Test**: Can be tested by running ingestion twice and verifying no duplicate vectors exist in Qdrant.

**Acceptance Scenarios**:

1. **Given** a chunk has already been ingested, **When** the same chunk is encountered again, **Then** it is skipped without creating a duplicate vector
2. **Given** content has been updated on a page, **When** re-ingestion occurs, **Then** old vectors for that page are replaced with new ones

---

### User Story 4 - Ingestion Verification (Priority: P2)

As a system operator, I want to verify the ingestion status and statistics so that I can confirm successful completion and diagnose issues.

**Why this priority**: Essential for operations and debugging, but the system can function without it initially.

**Independent Test**: Can be tested by calling the verification endpoint and confirming it returns accurate collection statistics.

**Acceptance Scenarios**:

1. **Given** ingestion has completed, **When** verification endpoint is called, **Then** total vector count and collection metadata are returned
2. **Given** specific URL is queried, **When** verification is requested, **Then** chunks associated with that URL are listed

---

### Edge Cases

- What happens when a page returns 404 or is temporarily unavailable?
  - System logs the error and continues with remaining pages
- What happens when Cohere API rate limits are hit?
  - System implements exponential backoff and retries
- What happens when Qdrant Cloud is unreachable?
  - System queues failed operations and retries with backoff
- What happens when a page has no extractable content?
  - System logs a warning and skips the page
- What happens when chunk overlap creates very small final chunks?
  - Chunks below minimum threshold (50 tokens) are merged with previous chunk

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST crawl all published book pages from the deployed Docusaurus site
- **FR-002**: System MUST extract clean, readable text from HTML pages, removing navigation, headers, footers, and styling
- **FR-003**: System MUST preserve document structure metadata (title, section headings, URL)
- **FR-004**: System MUST chunk text into segments of less than 1000 tokens
- **FR-005**: System MUST apply overlap between consecutive chunks (default: 100 tokens)
- **FR-006**: System MUST generate embeddings using Cohere embedding models
- **FR-007**: System MUST store vectors in Qdrant Cloud with metadata (url, title, section, chunk_index)
- **FR-008**: System MUST detect and skip duplicate chunks based on content hash
- **FR-009**: System MUST expose a FastAPI endpoint to trigger full ingestion
- **FR-010**: System MUST expose a FastAPI endpoint to verify ingestion status and statistics
- **FR-011**: System MUST handle API rate limits with exponential backoff
- **FR-012**: System MUST log all ingestion operations for debugging and monitoring

### Key Entities

- **BookPage**: Represents a single page from the deployed book (URL, title, raw HTML, extracted text)
- **TextChunk**: A segment of text ready for embedding (content, source_url, title, section, chunk_index, token_count)
- **VectorRecord**: An embedding stored in Qdrant (vector, metadata payload including url, title, section, chunk_index, content_hash)
- **IngestionJob**: Tracks the status of an ingestion run (job_id, started_at, completed_at, pages_processed, chunks_created, errors)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of published book pages (15+ chapters) are successfully crawled and processed
- **SC-002**: All text chunks are stored with complete metadata (url, title, section, chunk_index)
- **SC-003**: No duplicate chunks exist in the vector collection after repeated ingestion runs
- **SC-004**: Full book ingestion completes within 10 minutes for the current book size
- **SC-005**: Verification endpoint returns accurate statistics matching actual Qdrant collection state
- **SC-006**: System recovers gracefully from transient API failures without manual intervention

## Scope

### In Scope

- Web crawling of deployed Docusaurus book
- HTML to clean text extraction
- Text chunking with token limits and overlap
- Cohere embedding generation
- Qdrant Cloud vector storage
- Duplicate detection and prevention
- FastAPI endpoints for ingestion and verification
- Error handling and retry logic

### Out of Scope

- Retrieval logic or semantic search (Spec 2)
- Agent reasoning or chat functionality (Spec 3)
- Frontend integration or UI components (Spec 4)
- Manual file upload or local markdown ingestion
- Local database storage (Qdrant Cloud only)
- Authentication/authorization for API endpoints (can be added later)

## Assumptions

- The deployed book URL is publicly accessible
- Cohere API credentials are available and have sufficient quota
- Qdrant Cloud account is set up with Free Tier access
- Book structure follows standard Docusaurus patterns (sitemap available or predictable URL structure)
- Network connectivity is stable for API calls
- Token counting uses standard tokenization compatible with Cohere models

## Dependencies

- Deployed Docusaurus book (Phase 1 complete)
- Cohere API account and credentials
- Qdrant Cloud account and credentials
- Python 3.11 runtime environment
- FastAPI framework

## Constraints

- Must use Cohere embedding models only (no OpenAI, HuggingFace, etc.)
- Must use Qdrant Cloud Free Tier (storage and rate limits apply)
- Chunk size must be <1000 tokens with overlap
- Must ingest from live deployed URLs, not local files
- No manual steps allowed in the pipeline
