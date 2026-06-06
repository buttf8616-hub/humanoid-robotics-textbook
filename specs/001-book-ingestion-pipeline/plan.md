# Implementation Plan: Book Ingestion Pipeline

**Branch**: `001-book-ingestion-pipeline` | **Date**: 2025-01-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-book-ingestion-pipeline/spec.md`

## Summary

Automated pipeline to crawl the deployed Physical AI & Humanoid Robotics Docusaurus book, extract readable content, chunk text with token limits, generate Cohere embeddings, and store vectors with metadata in Qdrant Cloud. FastAPI exposes ingestion trigger and verification endpoints.

## Technical Context

**Language/Version**: Python 3.11
**Package Manager**: uv (modern, fast Python package manager)
**Primary Dependencies**: FastAPI, httpx, beautifulsoup4, cohere, qdrant-client, tiktoken
**Storage**: Qdrant Cloud (vector database)
**Testing**: pytest, pytest-asyncio
**Target Platform**: Hugging Face Spaces (Docker)
**Project Type**: Backend API service
**Performance Goals**: Full book ingestion <10 minutes, API response <500ms
**Constraints**: Cohere Free Tier rate limits, Qdrant Cloud Free Tier storage limits
**Scale/Scope**: 15+ chapters, ~1000 chunks estimated

## Constitution Check

*GATE: Must pass before implementation*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-First | ✅ PASS | spec.md created and validated |
| II. AI-Assisted, Human-Directed | ✅ PASS | User provides direction, AI implements |
| III. Source-Grounded | ✅ PASS | Using Context7 MCP for library docs |
| IV. Modular & Maintainable | ✅ PASS | Clean project structure defined |
| V. Reproducibility | ✅ PASS | uv lockfile ensures reproducible builds |
| VI. Test-First (TDD) | ✅ PASS | Tests defined before implementation |

## Project Structure

### Documentation (this feature)

```text
specs/001-book-ingestion-pipeline/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Technical research
├── data-model.md        # Entity definitions
├── quickstart.md        # Setup guide
├── contracts/           # API contracts (OpenAPI)
│   └── ingestion-api.yaml
└── checklists/
    └── requirements.md  # Quality checklist
```

### Source Code (repository root)

```text
backend/
├── pyproject.toml       # Project config + dependencies (uv)
├── uv.lock              # Lockfile for reproducibility
├── README.md            # Backend documentation
├── .env.example         # Environment variables template
├── Dockerfile           # Hugging Face Spaces deployment
│
├── src/
│   ├── __init__.py
│   ├── main.py          # FastAPI app entry point
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py  # Environment configuration
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── book_page.py     # BookPage entity
│   │   ├── text_chunk.py    # TextChunk entity
│   │   ├── vector_record.py # VectorRecord entity
│   │   └── ingestion_job.py # IngestionJob entity
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── crawler.py       # Web crawling service
│   │   ├── extractor.py     # HTML text extraction
│   │   ├── chunker.py       # Text chunking service
│   │   ├── embedder.py      # Cohere embedding service
│   │   └── storage.py       # Qdrant storage service
│   │
│   └── api/
│       ├── __init__.py
│       ├── routes.py        # API route definitions
│       └── schemas.py       # Pydantic request/response models
│
└── tests/
    ├── __init__.py
    ├── conftest.py          # Pytest fixtures
    │
    ├── unit/
    │   ├── __init__.py
    │   ├── test_crawler.py
    │   ├── test_extractor.py
    │   ├── test_chunker.py
    │   ├── test_embedder.py
    │   └── test_storage.py
    │
    └── integration/
        ├── __init__.py
        ├── test_ingestion_flow.py
        └── test_api_endpoints.py
```

**Structure Decision**: Single backend project structure selected. No frontend in this spec (that's Spec 4). Clean separation: config → models → services → api.

## Implementation Phases

### Phase 1: Project Setup & Configuration

**Goal**: Initialize backend project with uv, configure dependencies and environment.

**Tasks**:
1. Create `backend/` directory structure
2. Initialize uv project with `pyproject.toml`
3. Add dependencies: fastapi, uvicorn, httpx, beautifulsoup4, cohere, qdrant-client, tiktoken, python-dotenv, pydantic-settings
4. Add dev dependencies: pytest, pytest-asyncio, httpx (for test client)
5. Create `.env.example` with required variables
6. Create `src/config/settings.py` with pydantic-settings
7. Create basic `src/main.py` FastAPI app with health endpoint

**Acceptance**: `uv run uvicorn src.main:app` starts server, `/health` returns 200.

---

### Phase 2: Web Crawler Service

**Goal**: Crawl all published book pages from deployed Docusaurus site.

**Tasks**:
1. Create `src/services/crawler.py`
2. Implement sitemap parsing (Docusaurus generates sitemap.xml)
3. Implement page fetching with httpx (async)
4. Handle rate limiting and retries with exponential backoff
5. Return list of BookPage objects with URL and raw HTML

**Acceptance**: Crawler returns all 15+ chapter URLs with HTML content.

---

### Phase 3: Text Extraction Service

**Goal**: Extract clean, readable text from HTML pages.

**Tasks**:
1. Create `src/services/extractor.py`
2. Use BeautifulSoup to parse HTML
3. Remove navigation, headers, footers, scripts, styles
4. Extract main content area (Docusaurus article/main element)
5. Preserve section structure (h1, h2, h3 as metadata)
6. Return clean text with section metadata

**Acceptance**: Extracted text contains no HTML tags, preserves logical structure.

---

### Phase 4: Text Chunking Service

**Goal**: Split extracted text into chunks suitable for embedding.

**Tasks**:
1. Create `src/services/chunker.py`
2. Implement token counting with tiktoken (cl100k_base tokenizer)
3. Implement chunking with max 1000 tokens per chunk
4. Implement 100-token overlap between chunks
5. Handle edge cases (small final chunks merged)
6. Generate chunk metadata (url, title, section, chunk_index)
7. Generate content hash for deduplication

**Acceptance**: All chunks <1000 tokens, overlap applied, metadata complete.

---

### Phase 5: Embedding Service

**Goal**: Generate vector embeddings using Cohere API.

**Tasks**:
1. Create `src/services/embedder.py`
2. Initialize Cohere client with API key
3. Implement batch embedding generation (Cohere supports batching)
4. Use `embed-english-v3.0` model
5. Handle rate limits with exponential backoff
6. Return embeddings with matching chunk indices

**Acceptance**: Embeddings generated for all chunks, correct dimension (1024).

---

### Phase 6: Qdrant Storage Service

**Goal**: Store vectors and metadata in Qdrant Cloud.

**Tasks**:
1. Create `src/services/storage.py`
2. Initialize Qdrant client with cloud credentials
3. Create collection if not exists (vector size 1024, cosine distance)
4. Implement upsert with content hash as point ID (deduplication)
5. Store metadata payload (url, title, section, chunk_index, content_hash)
6. Implement collection statistics retrieval

**Acceptance**: Vectors stored in Qdrant, queryable by metadata, no duplicates.

---

### Phase 7: API Endpoints

**Goal**: Expose FastAPI endpoints for ingestion and verification.

**Tasks**:
1. Create `src/api/schemas.py` with Pydantic models
2. Create `src/api/routes.py` with endpoint handlers
3. `POST /ingest` - Trigger full ingestion pipeline
4. `GET /ingest/status/{job_id}` - Get ingestion job status
5. `GET /verify` - Get collection statistics
6. `GET /verify/url/{url}` - Get chunks for specific URL
7. Add error handling and logging

**Acceptance**: All endpoints return correct responses, errors handled gracefully.

---

### Phase 8: Deployment Configuration

**Goal**: Prepare for Hugging Face Spaces deployment.

**Tasks**:
1. Create `Dockerfile` for Hugging Face Spaces
2. Configure environment variables for secrets
3. Create deployment documentation
4. Test containerized deployment locally

**Acceptance**: Docker image builds, runs correctly with all services connected.

## Dependencies Graph

```
Phase 1 (Setup)
    ↓
Phase 2 (Crawler) → Phase 3 (Extractor) → Phase 4 (Chunker)
                                              ↓
                                         Phase 5 (Embedder)
                                              ↓
                                         Phase 6 (Storage)
                                              ↓
                                         Phase 7 (API)
                                              ↓
                                         Phase 8 (Deploy)
```

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Cohere rate limits | Slow ingestion | Batch requests, exponential backoff |
| Qdrant Cloud limits | Storage exceeded | Monitor usage, optimize chunk size |
| Website structure changes | Extraction fails | Use robust CSS selectors, test regularly |
| Token count mismatch | Incorrect chunks | Use same tokenizer as Cohere model |

## Environment Variables

```bash
# .env.example
BOOK_BASE_URL=https://your-book-url.github.io
COHERE_API_KEY=your-cohere-api-key
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key
QDRANT_COLLECTION_NAME=book-chunks
```

## Testing Strategy

**Unit Tests**: Each service tested in isolation with mocks
**Integration Tests**: Full pipeline tested with real APIs (separate test collection)
**Contract Tests**: API responses validated against OpenAPI schema

## Next Steps

1. ✅ Plan approved → Create `tasks.md` with `/sp.tasks`
2. Implement Phase 1-8 following TDD cycle
3. Deploy to Hugging Face Spaces
4. Verify full ingestion of deployed book
