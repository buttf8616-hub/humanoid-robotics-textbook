# Tasks: RAG Retrieval Pipeline

**Input**: Design documents from `/specs/002-retrieval-pipeline/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Constitution specifies Test-First (TDD) approach. Tests are included.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Web app (backend)**: `backend/src/`, `backend/tests/`
- Extending existing Spec 001 backend structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Configuration and model setup for retrieval feature

- [x] T001 Add retrieval settings (default_top_k=5, max_top_k=50) to backend/src/config/settings.py
- [x] T002 [P] Create SearchQuery model in backend/src/models/retrieval.py
- [x] T003 [P] Create RetrievalResult model in backend/src/models/retrieval.py
- [x] T004 [P] Create SearchResponse model in backend/src/models/retrieval.py
- [x] T005 Export new models from backend/src/models/__init__.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Add embed_query() method to EmbedderService in backend/src/services/embedder.py using input_type="search_query"
- [x] T007 [P] Add embed_query_async() method to EmbedderService in backend/src/services/embedder.py
- [x] T008 [P] Write unit test for embed_query() in backend/tests/unit/test_embedder.py
- [x] T009 Add search() method to StorageService in backend/src/services/storage.py with vector similarity search
- [x] T010 Add URL filter support (MatchValue exact match) to search() in backend/src/services/storage.py
- [x] T011 Add section filter support (MatchText substring) to search() in backend/src/services/storage.py
- [x] T012 [P] Write unit tests for search() method in backend/tests/unit/test_storage_search.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Basic Semantic Search (Priority: P1) MVP

**Goal**: Users can submit natural language queries and receive relevant book chunks with metadata

**Independent Test**: Send query to /api/v1/search endpoint, verify chunks returned with correct metadata structure (url, title, section, chunk_index, score)

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T013 [P] [US1] Write unit test for RetrieverService.retrieve() in backend/tests/unit/test_retriever.py
- [x] T014 [P] [US1] Write integration test for POST /api/v1/search in backend/tests/integration/test_retrieval_api.py

### Implementation for User Story 1

- [x] T015 [US1] Create RetrieverService class in backend/src/services/retriever.py
- [x] T016 [US1] Implement retrieve() method with query embedding and search orchestration in backend/src/services/retriever.py
- [x] T017 [US1] Add latency measurement (time.perf_counter) to retrieve() in backend/src/services/retriever.py
- [x] T018 [US1] Add structured logging for retrieval requests in backend/src/services/retriever.py
- [x] T019 [US1] Export RetrieverService from backend/src/services/__init__.py
- [x] T020 [P] [US1] Add SearchRequest schema to backend/src/api/schemas.py
- [x] T021 [P] [US1] Add RetrievalResultResponse schema to backend/src/api/schemas.py
- [x] T022 [P] [US1] Add SearchResponseSchema to backend/src/api/schemas.py
- [x] T023 [US1] Add POST /api/v1/search endpoint to backend/src/api/routes.py
- [x] T024 [US1] Add empty query validation (return 400) in backend/src/api/routes.py
- [x] T025 [US1] Add error handling for Cohere/Qdrant failures (return 503) in backend/src/api/routes.py

**Checkpoint**: User Story 1 complete - basic semantic search functional with default top_k=5

---

## Phase 4: User Story 2 - Configurable Top-K Retrieval (Priority: P2)

**Goal**: Users can specify how many results to return via top_k parameter

**Independent Test**: Send queries with different top_k values (3, 10, 20), verify correct number of results returned

### Tests for User Story 2

- [x] T026 [P] [US2] Write test for top_k parameter validation in backend/tests/unit/test_retriever.py
- [x] T027 [P] [US2] Write integration test for top_k variations in backend/tests/integration/test_retrieval_api.py

### Implementation for User Story 2

- [x] T028 [US2] Add top_k validation (1-50 bounds) in backend/src/api/routes.py
- [x] T029 [US2] Add top_k parameter to /search endpoint request handling in backend/src/api/routes.py
- [x] T030 [US2] Add test for empty results when no matches in backend/tests/integration/test_retrieval_api.py

**Checkpoint**: User Story 2 complete - configurable top_k working

---

## Phase 5: User Story 3 - Metadata Filtering (Priority: P2)

**Goal**: Users can filter results by URL or section name

**Independent Test**: Apply URL filter, verify only chunks from that URL returned; apply section filter, verify substring matching works

### Tests for User Story 3

- [x] T031 [P] [US3] Write test for url_filter parameter in backend/tests/unit/test_storage_search.py
- [x] T032 [P] [US3] Write test for section_filter parameter in backend/tests/unit/test_storage_search.py
- [x] T033 [P] [US3] Write integration test for filtered search in backend/tests/integration/test_retrieval_api.py

### Implementation for User Story 3

- [x] T034 [US3] Add url_filter parameter to /search endpoint in backend/src/api/routes.py
- [x] T035 [US3] Add section_filter parameter to /search endpoint in backend/src/api/routes.py
- [x] T036 [US3] Add filters_applied field to SearchResponse in backend/src/api/routes.py
- [x] T037 [US3] Add test for combined filters (URL + section) in backend/tests/integration/test_retrieval_api.py

**Checkpoint**: User Story 3 complete - URL and section filtering working

---

## Phase 6: User Story 4 - Retrieval Validation & Testing (Priority: P3)

**Goal**: Validate retrieval quality with predefined test queries

**Independent Test**: Run 5 test queries, verify each returns contextually relevant results within latency bounds

### Tests for User Story 4

- [x] T038 [P] [US4] Create test query suite file backend/tests/integration/test_retrieval_validation.py

### Implementation for User Story 4

- [x] T039 [US4] Add test: "What is embodied intelligence?" returns Physical AI content in backend/tests/integration/test_retrieval_validation.py
- [x] T040 [US4] Add test: "ROS 2 architecture" returns ROS 2 chapter content in backend/tests/integration/test_retrieval_validation.py
- [x] T041 [US4] Add test: "sensor fusion" returns perception content in backend/tests/integration/test_retrieval_validation.py
- [x] T042 [US4] Add test: "robot control systems" returns control content in backend/tests/integration/test_retrieval_validation.py
- [x] T043 [US4] Add test: "humanoid locomotion" returns movement content in backend/tests/integration/test_retrieval_validation.py
- [x] T044 [US4] Add latency assertion (<500ms) to all validation tests in backend/tests/integration/test_retrieval_validation.py

**Checkpoint**: User Story 4 complete - validation suite confirms retrieval quality

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation and final cleanup

- [x] T045 [P] Update backend/README.md with /search endpoint documentation
- [x] T046 [P] Verify quickstart.md examples work with live endpoints
- [x] T047 Run full test suite and verify all tests pass
- [x] T048 [P] Add request/response examples to API documentation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - US1 (P1): Core search - MUST complete first
  - US2 (P2): Top-K - can run after US1 (enhances US1)
  - US3 (P2): Filtering - can run after US1 (enhances US1)
  - US4 (P3): Validation - can run after US1-3 complete
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

| Story | Depends On | Can Parallelize With |
|-------|------------|---------------------|
| US1 (P1) | Foundational | None (must complete first) |
| US2 (P2) | US1 | US3 |
| US3 (P2) | US1 | US2 |
| US4 (P3) | US1, US2, US3 | None |

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models/schemas before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

**Phase 1 (Setup)**:
```
T002, T003, T004 can run in parallel (different models)
```

**Phase 2 (Foundational)**:
```
T007, T008 can run in parallel
T012 can run in parallel with T006-T011
```

**Phase 3 (US1)**:
```
T013, T014 can run in parallel (tests)
T020, T021, T022 can run in parallel (schemas)
```

**Phase 5 (US3)**:
```
T031, T032, T033 can run in parallel (tests)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T012)
3. Complete Phase 3: User Story 1 (T013-T025)
4. **STOP and VALIDATE**: Test basic search independently
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add User Story 1 → Basic search works → Deploy (MVP!)
3. Add User Story 2 → Configurable top_k → Deploy
4. Add User Story 3 → Filtering works → Deploy
5. Add User Story 4 → Validation suite → Final quality gate

---

## Summary

| Phase | Tasks | Parallel Tasks |
|-------|-------|----------------|
| Setup | 5 | 3 |
| Foundational | 7 | 3 |
| US1 (P1) | 13 | 6 |
| US2 (P2) | 5 | 2 |
| US3 (P3) | 7 | 3 |
| US4 (P3) | 7 | 1 |
| Polish | 4 | 3 |
| **Total** | **48** | **21** |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (TDD per constitution)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
