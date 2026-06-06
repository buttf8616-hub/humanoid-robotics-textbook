# Implementation Plan: RAG Retrieval Pipeline

**Branch**: `002-retrieval-pipeline` | **Date**: 2026-01-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-retrieval-pipeline/spec.md`

## Summary

Implement semantic retrieval over stored book embeddings in Qdrant Cloud. The system accepts natural language queries, converts them to embeddings using Cohere, performs vector similarity search with optional metadata filtering, and returns relevant chunks with metadata and latency metrics. This extends the existing backend from Spec 001.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: FastAPI, qdrant-client, cohere, pydantic
**Storage**: Qdrant Cloud (existing collection from Spec 001)
**Testing**: pytest with unit and integration tests
**Target Platform**: Hugging Face Spaces (Docker)
**Project Type**: Backend API extension
**Performance Goals**: <500ms p95 latency, 100 concurrent requests
**Constraints**: Must use same embedding model as ingestion (Cohere embed-english-v3.0, 1024 dims)
**Scale/Scope**: Single collection, ~1000s of chunks

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| Spec-First Development | PASS | Spec created before planning |
| AI-Assisted, Human-Directed | PASS | Plan requires user approval |
| Source-Grounded Content | PASS | Using existing Qdrant/Cohere patterns |
| Test-First (NON-NEGOTIABLE) | PASS | Tests defined before implementation |

## Project Structure

### Documentation (this feature)

```text
specs/002-retrieval-pipeline/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Technical decisions
├── data-model.md        # Entity definitions
├── quickstart.md        # Setup guide
├── contracts/
│   └── retrieval-api.yaml  # OpenAPI spec
└── checklists/
    └── requirements.md  # Quality checklist
```

### Source Code (extending existing backend)

```text
backend/
├── src/
│   ├── api/
│   │   ├── routes.py        # Add retrieval routes
│   │   └── schemas.py       # Add retrieval schemas
│   ├── config/
│   │   └── settings.py      # Add retrieval settings
│   ├── models/
│   │   └── retrieval.py     # NEW: Retrieval models
│   └── services/
│       ├── embedder.py      # Extend for query embedding
│       ├── storage.py       # Extend for vector search
│       └── retriever.py     # NEW: Retrieval orchestration
└── tests/
    ├── unit/
    │   ├── test_retriever.py    # NEW
    │   └── test_storage_search.py  # NEW
    └── integration/
        └── test_retrieval_api.py   # NEW
```

**Structure Decision**: Extend existing backend structure from Spec 001. New retrieval functionality added as:
- New service (`retriever.py`) to orchestrate query embedding + search
- Extended storage service with `search()` method
- Extended embedder service with query embedding
- New API schemas and routes for retrieval endpoint

## Implementation Phases

### Phase 1: Core Models & Configuration

**Goal**: Define data models and configuration for retrieval

**Tasks**:
1. Create `src/models/retrieval.py` with SearchQuery, RetrievalResult, SearchResponse models
2. Update `src/models/__init__.py` to export new models
3. Add retrieval settings to `src/config/settings.py` (default_top_k, max_top_k)

**Files**:
- `backend/src/models/retrieval.py` (NEW)
- `backend/src/models/__init__.py` (MODIFY)
- `backend/src/config/settings.py` (MODIFY)

**Tests**:
- Unit tests for model validation and defaults

---

### Phase 2: Embedder Extension for Query Embedding

**Goal**: Add query embedding capability using Cohere's search_query input type

**Tasks**:
1. Add `embed_query()` method to EmbedderService
2. Use `input_type="search_query"` for asymmetric search optimization
3. Add async variant `embed_query_async()`

**Files**:
- `backend/src/services/embedder.py` (MODIFY)

**Tests**:
- `backend/tests/unit/test_embedder.py` (extend with query embedding tests)

**Key Implementation Detail**:
```python
def embed_query(self, query: str) -> list[float]:
    """Embed a search query using search_query input type."""
    response = self._get_client().embed(
        texts=[query],
        model=self.model,
        input_type="search_query",  # Optimized for queries
    )
    return response.embeddings[0]
```

---

### Phase 3: Storage Extension for Vector Search

**Goal**: Add semantic search capability to StorageService

**Tasks**:
1. Add `search()` method with vector similarity search
2. Support optional URL filter (exact match)
3. Support optional section filter (substring match via text contains)
4. Return results with scores sorted by relevance

**Files**:
- `backend/src/services/storage.py` (MODIFY)

**Tests**:
- `backend/tests/unit/test_storage_search.py` (NEW)

**Key Implementation Detail**:
```python
def search(
    self,
    query_vector: list[float],
    top_k: int = 5,
    url_filter: Optional[str] = None,
    section_filter: Optional[str] = None,
) -> list[dict]:
    """Search for similar vectors with optional filters."""
    # Build filter conditions
    must_conditions = []
    if url_filter:
        must_conditions.append(
            models.FieldCondition(key="url", match=models.MatchValue(value=url_filter))
        )
    if section_filter:
        must_conditions.append(
            models.FieldCondition(key="section", match=models.MatchText(text=section_filter))
        )

    search_filter = models.Filter(must=must_conditions) if must_conditions else None

    results = self._get_client().search(
        collection_name=self.collection_name,
        query_vector=query_vector,
        limit=top_k,
        query_filter=search_filter,
        with_payload=True,
    )
    return [{"score": r.score, **r.payload} for r in results]
```

---

### Phase 4: Retriever Service

**Goal**: Create orchestration service combining embedding and search

**Tasks**:
1. Create RetrieverService class
2. Orchestrate: validate query → embed query → search → format response
3. Add timing/latency measurement
4. Add structured logging for requests

**Files**:
- `backend/src/services/retriever.py` (NEW)
- `backend/src/services/__init__.py` (MODIFY)

**Tests**:
- `backend/tests/unit/test_retriever.py` (NEW)

**Key Implementation Detail**:
```python
class RetrieverService:
    def __init__(self):
        self.embedder = EmbedderService()
        self.storage = StorageService()

    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        url_filter: Optional[str] = None,
        section_filter: Optional[str] = None,
    ) -> SearchResponse:
        start_time = time.perf_counter()

        # Embed query
        query_vector = self.embedder.embed_query(query)

        # Search
        results = self.storage.search(
            query_vector=query_vector,
            top_k=top_k,
            url_filter=url_filter,
            section_filter=section_filter,
        )

        latency_ms = (time.perf_counter() - start_time) * 1000

        return SearchResponse(
            results=[RetrievalResult(...) for r in results],
            total_count=len(results),
            latency_ms=latency_ms,
            filters_applied={...},
        )
```

---

### Phase 5: API Schemas & Routes

**Goal**: Expose retrieval via REST API

**Tasks**:
1. Add SearchRequest, RetrievalResultResponse, SearchResponse schemas
2. Add `POST /api/v1/search` endpoint
3. Add request validation (empty query, top_k bounds)
4. Add error handling for embedding/search failures

**Files**:
- `backend/src/api/schemas.py` (MODIFY)
- `backend/src/api/routes.py` (MODIFY)

**Tests**:
- `backend/tests/integration/test_retrieval_api.py` (NEW)

**API Contract**:
```
POST /api/v1/search
Request:
{
  "query": "What is embodied intelligence?",
  "top_k": 5,
  "url_filter": null,
  "section_filter": null
}

Response:
{
  "results": [
    {
      "content": "...",
      "url": "...",
      "title": "...",
      "section": "...",
      "chunk_index": 0,
      "score": 0.89
    }
  ],
  "total_count": 5,
  "latency_ms": 234.5,
  "filters_applied": {}
}
```

---

### Phase 6: Validation & Testing

**Goal**: Validate retrieval quality and performance

**Tasks**:
1. Create test query suite with expected outcomes
2. Run latency benchmarks
3. Validate filter precision
4. Document test results

**Files**:
- `backend/tests/integration/test_retrieval_validation.py` (NEW)

**Test Queries**:
| Query | Expected Topic |
|-------|----------------|
| "What is embodied intelligence?" | Physical AI fundamentals |
| "ROS 2 architecture" | ROS 2 chapter content |
| "sensor fusion" | Perception/sensors content |
| "robot control systems" | Control systems content |
| "humanoid locomotion" | Movement/walking content |

## Risk Analysis

| Risk | Mitigation |
|------|------------|
| Cohere rate limits on query embedding | Implement retry with exponential backoff |
| Qdrant connection failures | Graceful error handling with service unavailable response |
| Poor retrieval relevance | Test with diverse queries, adjust if needed |
| Latency exceeds 500ms | Profile and optimize, consider caching |

## Dependencies

- **Spec 001**: Populated Qdrant collection with book embeddings
- **External**: Cohere API availability
- **External**: Qdrant Cloud availability

## Definition of Done

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] API endpoint returns results within 500ms for test queries
- [ ] Filters correctly exclude non-matching content
- [ ] Empty/invalid queries return proper error responses
- [ ] Logging captures all retrieval requests
- [ ] Documentation updated (README, quickstart)
