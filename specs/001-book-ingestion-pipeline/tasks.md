# Tasks: Book Ingestion Pipeline

**Input**: Design documents from `/specs/001-book-ingestion-pipeline/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/ingestion-api.yaml, research.md, quickstart.md

**Tests**: Tests are included as per constitution (TDD mandatory).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Project**: `backend/` at repository root (single backend project)
- Source: `backend/src/`
- Tests: `backend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize backend project with uv, configure dependencies and environment

- [ ] T001 Create backend directory structure per plan.md in backend/
- [ ] T002 Initialize uv project with pyproject.toml in backend/pyproject.toml
- [ ] T003 Add runtime dependencies (fastapi, uvicorn, httpx, beautifulsoup4, cohere, qdrant-client, tiktoken, pydantic-settings, python-dotenv) in backend/pyproject.toml
- [ ] T004 [P] Add dev dependencies (pytest, pytest-asyncio, pytest-cov) in backend/pyproject.toml
- [ ] T005 [P] Create .env.example with BOOK_BASE_URL, COHERE_API_KEY, QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION_NAME in backend/.env.example
- [ ] T006 Run uv sync to generate lockfile in backend/uv.lock
- [ ] T007 Create __init__.py files for all packages (src/, src/config/, src/models/, src/services/, src/api/, tests/, tests/unit/, tests/integration/)

**Checkpoint**: Project skeleton ready, `uv sync` succeeds

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [ ] T008 Create Settings class with pydantic-settings in backend/src/config/settings.py
- [ ] T009 Create FastAPI app with health endpoint in backend/src/main.py
- [ ] T010 [P] Create BookPage Pydantic model in backend/src/models/book_page.py
- [ ] T011 [P] Create TextChunk Pydantic model in backend/src/models/text_chunk.py
- [ ] T012 [P] Create VectorRecord Pydantic model in backend/src/models/vector_record.py
- [ ] T013 [P] Create IngestionJob Pydantic model in backend/src/models/ingestion_job.py
- [ ] T014 Create models __init__.py exporting all models in backend/src/models/__init__.py
- [ ] T015 Create pytest conftest.py with shared fixtures in backend/tests/conftest.py
- [ ] T016 Verify health endpoint returns 200 OK by running uvicorn

**Checkpoint**: Foundation ready - `uv run uvicorn src.main:app` starts, `/health` returns 200

---

## Phase 3: User Story 1 - Full Book Ingestion (Priority: P1)

**Goal**: Trigger complete ingestion of all published book pages - crawl, extract, chunk

**Independent Test**: Trigger ingestion endpoint and verify all 15+ chapters are processed with correct chunking

### Tests for User Story 1

- [ ] T017 [P] [US1] Create unit test for crawler service (sitemap parsing, page fetching) in backend/tests/unit/test_crawler.py
- [ ] T018 [P] [US1] Create unit test for extractor service (HTML to text) in backend/tests/unit/test_extractor.py
- [ ] T019 [P] [US1] Create unit test for chunker service (token limits, overlap) in backend/tests/unit/test_chunker.py

### Implementation for User Story 1

- [ ] T020 [US1] Implement CrawlerService with sitemap parsing in backend/src/services/crawler.py
- [ ] T021 [US1] Implement async page fetching with httpx and retry logic in backend/src/services/crawler.py
- [ ] T022 [US1] Implement ExtractorService with BeautifulSoup parsing in backend/src/services/extractor.py
- [ ] T023 [US1] Implement HTML content extraction (remove nav, headers, footers, scripts) in backend/src/services/extractor.py
- [ ] T024 [US1] Implement section metadata extraction (h1, h2, h3) in backend/src/services/extractor.py
- [ ] T025 [US1] Implement ChunkerService with tiktoken tokenizer in backend/src/services/chunker.py
- [ ] T026 [US1] Implement chunking with 1000 token max and 100 token overlap in backend/src/services/chunker.py
- [ ] T027 [US1] Implement content hash generation (SHA-256) for deduplication in backend/src/services/chunker.py
- [ ] T028 [US1] Handle edge case: merge small final chunks (<50 tokens) in backend/src/services/chunker.py
- [ ] T029 [US1] Run US1 tests and verify all pass

**Checkpoint**: Crawler, Extractor, Chunker services complete and tested. Can crawl book and produce chunks.

---

## Phase 4: User Story 2 - Embedding Generation & Storage (Priority: P1)

**Goal**: Convert text chunks to vector embeddings and store in Qdrant with metadata

**Independent Test**: Verify Qdrant collection contains vectors with correct dimensions (1024) and queryable metadata

### Tests for User Story 2

- [ ] T030 [P] [US2] Create unit test for embedder service (Cohere API, batching) in backend/tests/unit/test_embedder.py
- [ ] T031 [P] [US2] Create unit test for storage service (Qdrant operations) in backend/tests/unit/test_storage.py

### Implementation for User Story 2

- [ ] T032 [US2] Implement EmbedderService with Cohere client initialization in backend/src/services/embedder.py
- [ ] T033 [US2] Implement batch embedding generation using embed-english-v3.0 in backend/src/services/embedder.py
- [ ] T034 [US2] Implement rate limit handling with exponential backoff in backend/src/services/embedder.py
- [ ] T035 [US2] Implement StorageService with Qdrant client initialization in backend/src/services/storage.py
- [ ] T036 [US2] Implement collection creation (vector size 1024, cosine distance) in backend/src/services/storage.py
- [ ] T037 [US2] Implement vector upsert with metadata payload (url, title, section, chunk_index, content_hash) in backend/src/services/storage.py
- [ ] T038 [US2] Run US2 tests and verify all pass

**Checkpoint**: Embedder and Storage services complete. Can generate embeddings and store in Qdrant.

---

## Phase 5: User Story 3 - Duplicate Prevention (Priority: P2)

**Goal**: Detect and skip duplicate content to keep vector database clean

**Independent Test**: Run ingestion twice and verify no duplicate vectors exist in Qdrant

### Tests for User Story 3

- [ ] T039 [P] [US3] Create unit test for deduplication logic (content hash check) in backend/tests/unit/test_storage.py

### Implementation for User Story 3

- [ ] T040 [US3] Implement duplicate detection using content_hash as point ID in backend/src/services/storage.py
- [ ] T041 [US3] Implement upsert behavior (update existing, skip unchanged) in backend/src/services/storage.py
- [ ] T042 [US3] Run US3 tests and verify deduplication works

**Checkpoint**: Duplicate prevention complete. Re-ingestion does not create duplicates.

---

## Phase 6: User Story 4 - Ingestion Verification (Priority: P2)

**Goal**: Verify ingestion status and statistics for operations and debugging

**Independent Test**: Call verification endpoint and confirm accurate collection statistics

### Tests for User Story 4

- [ ] T043 [P] [US4] Create integration test for /verify endpoint in backend/tests/integration/test_api_endpoints.py
- [ ] T044 [P] [US4] Create integration test for /verify/url endpoint in backend/tests/integration/test_api_endpoints.py

### Implementation for User Story 4

- [ ] T045 [US4] Implement collection statistics retrieval in backend/src/services/storage.py
- [ ] T046 [US4] Implement URL-specific chunk retrieval in backend/src/services/storage.py
- [ ] T047 [US4] Create API schemas (request/response models) in backend/src/api/schemas.py
- [ ] T048 [US4] Implement GET /verify endpoint in backend/src/api/routes.py
- [ ] T049 [US4] Implement GET /verify/url endpoint in backend/src/api/routes.py
- [ ] T050 [US4] Run US4 tests and verify endpoints return correct data

**Checkpoint**: Verification endpoints complete. Can check collection stats and URL chunks.

---

## Phase 7: API Integration (Full Pipeline)

**Purpose**: Wire all services together with ingestion API endpoint

### Tests

- [ ] T051 [P] Create integration test for POST /ingest endpoint in backend/tests/integration/test_api_endpoints.py
- [ ] T052 [P] Create integration test for full ingestion flow in backend/tests/integration/test_ingestion_flow.py

### Implementation

- [ ] T053 Create IngestRequest and IngestResponse schemas in backend/src/api/schemas.py
- [ ] T054 Create JobStatusResponse schema in backend/src/api/schemas.py
- [ ] T055 Implement POST /ingest endpoint (orchestrate crawler→extractor→chunker→embedder→storage) in backend/src/api/routes.py
- [ ] T056 Implement GET /ingest/status/{job_id} endpoint in backend/src/api/routes.py
- [ ] T057 Add comprehensive error handling and logging in backend/src/api/routes.py
- [ ] T058 Register all routes in FastAPI app in backend/src/main.py
- [ ] T059 Run all integration tests and verify full pipeline works

**Checkpoint**: Full API complete. Can trigger ingestion via API and monitor status.

---

## Phase 8: Deployment & Polish

**Purpose**: Prepare for Hugging Face Spaces deployment and final polish

- [ ] T060 [P] Create Dockerfile for Hugging Face Spaces in backend/Dockerfile
- [ ] T061 [P] Create backend README with setup and usage instructions in backend/README.md
- [ ] T062 [P] Add type hints to all public functions
- [ ] T063 Test Docker build locally with `docker build`
- [ ] T064 Validate against quickstart.md scenarios
- [ ] T065 Run full test suite with coverage report

**Checkpoint**: Deployment ready. Docker builds, all tests pass, documentation complete.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational
- **User Story 2 (Phase 4)**: Depends on Foundational (can run parallel to US1 if staffed)
- **User Story 3 (Phase 5)**: Depends on US2 (uses storage service)
- **User Story 4 (Phase 6)**: Depends on US2 (uses storage service)
- **API Integration (Phase 7)**: Depends on US1, US2, US3, US4
- **Deployment (Phase 8)**: Depends on Phase 7

### User Story Dependencies

```
Foundational (Phase 2)
        │
        ├──────────────────┐
        │                  │
        ▼                  ▼
   User Story 1       User Story 2
   (Crawl/Extract/    (Embed/Store)
    Chunk)                 │
        │                  │
        │          ┌───────┴───────┐
        │          │               │
        │          ▼               ▼
        │     User Story 3    User Story 4
        │     (Dedup)         (Verify)
        │          │               │
        └──────────┴───────────────┘
                   │
                   ▼
            API Integration
                   │
                   ▼
              Deployment
```

### Within Each Phase

- Tests MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration

### Parallel Opportunities

**Phase 1**:
- T004, T005 can run in parallel

**Phase 2**:
- T010, T011, T012, T013 can run in parallel (all models)

**Phase 3 (US1)**:
- T017, T018, T019 can run in parallel (all tests)

**Phase 4 (US2)**:
- T030, T031 can run in parallel (all tests)

**Phase 6 (US4)**:
- T043, T044 can run in parallel (all tests)

**Phase 7**:
- T051, T052 can run in parallel (all tests)

**Phase 8**:
- T060, T061, T062 can run in parallel

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)

**MVP = Phase 1 + Phase 2 + Phase 3 + Phase 4**

With these phases complete, you can:
- Crawl the deployed book
- Extract and chunk content
- Generate embeddings
- Store in Qdrant

This is sufficient for downstream retrieval (Spec 2).

### Incremental Delivery

1. **Sprint 1**: Phases 1-2 (Setup + Foundation) → Project skeleton working
2. **Sprint 2**: Phases 3-4 (US1 + US2) → Core ingestion pipeline complete
3. **Sprint 3**: Phases 5-6 (US3 + US4) → Deduplication and verification
4. **Sprint 4**: Phases 7-8 (API + Deploy) → Production ready

---

## Summary

| Phase | Tasks | Parallel Tasks | Story |
|-------|-------|----------------|-------|
| 1. Setup | T001-T007 | 2 | - |
| 2. Foundational | T008-T016 | 4 | - |
| 3. US1 Ingestion | T017-T029 | 3 | US1 |
| 4. US2 Embedding | T030-T038 | 2 | US2 |
| 5. US3 Dedup | T039-T042 | 1 | US3 |
| 6. US4 Verify | T043-T050 | 2 | US4 |
| 7. API Integration | T051-T059 | 2 | - |
| 8. Deployment | T060-T065 | 3 | - |

**Total Tasks**: 65
**Parallel Opportunities**: 19 tasks
**User Stories**: 4 (US1, US2, US3, US4)
**MVP Tasks**: T001-T038 (38 tasks)
