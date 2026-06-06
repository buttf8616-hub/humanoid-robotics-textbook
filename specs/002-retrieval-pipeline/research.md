# Technical Research: RAG Retrieval Pipeline

**Feature**: 002-retrieval-pipeline
**Date**: 2026-01-08

## Research Questions

### 1. Cohere Query Embedding vs Document Embedding

**Question**: How should query embeddings differ from document embeddings?

**Finding**: Cohere's embed-english-v3.0 model supports asymmetric search via the `input_type` parameter:
- `search_document`: Used for documents being stored (used in Spec 001)
- `search_query`: Optimized for search queries - produces embeddings tuned to match documents

**Decision**: Use `input_type="search_query"` for all query embeddings to leverage asymmetric search optimization.

**Source**: Cohere Embed API documentation

---

### 2. Qdrant Vector Search with Filters

**Question**: How to implement filtered vector search in Qdrant?

**Finding**: Qdrant supports pre-filtering via the `query_filter` parameter in search:
- `FieldCondition` with `MatchValue` for exact string matches (URL filter)
- `FieldCondition` with `MatchText` for substring/text contains matches (section filter)
- Filters are applied BEFORE similarity ranking for efficiency

**Decision**:
- URL filter: Use `MatchValue` for exact match
- Section filter: Use `MatchText` for substring matching (allows partial section names)

**Source**: qdrant-client documentation, existing storage.py patterns

---

### 3. Latency Optimization

**Question**: How to achieve <500ms latency for retrieval?

**Finding**: Latency breakdown:
1. Query embedding: ~100-200ms (Cohere API call)
2. Vector search: ~50-100ms (Qdrant Cloud)
3. Network overhead: ~50ms
4. Processing: <10ms

**Decision**:
- Single embedding call (not batched) for queries
- Use Qdrant's native filtering (pre-filter, not post-filter)
- Measure and log latency components for monitoring
- No caching for MVP (queries are unique)

**Source**: Performance testing estimates based on API documentation

---

### 4. Score Normalization

**Question**: Should relevance scores be normalized?

**Finding**: Qdrant returns cosine similarity scores in range [-1, 1] for COSINE distance. Higher is more similar.

**Decision**: Return raw scores from Qdrant. Score interpretation:
- 0.8+ : High relevance
- 0.6-0.8: Moderate relevance
- <0.6: Low relevance

No normalization needed for MVP. Downstream consumers (agents) can threshold as needed.

---

### 5. Error Handling Strategy

**Question**: How to handle partial failures?

**Decision Matrix**:

| Failure | Response | Status Code |
|---------|----------|-------------|
| Empty query | Validation error | 400 |
| Invalid top_k | Validation error | 400 |
| Cohere API error | Service unavailable | 503 |
| Qdrant unavailable | Service unavailable | 503 |
| No results found | Empty array (success) | 200 |
| Filter matches nothing | Empty array (success) | 200 |

---

## Technology Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Query embedding type | `search_query` | Asymmetric search optimization |
| URL filter method | `MatchValue` (exact) | Precise URL matching |
| Section filter method | `MatchText` (substring) | Flexible section matching |
| Score handling | Raw cosine similarity | Simple, interpretable |
| Caching | None for MVP | Queries are unique |
| Async pattern | Sync embedding, async endpoint | Cohere client is sync |

## Reusable Components from Spec 001

| Component | Reuse Strategy |
|-----------|----------------|
| `EmbedderService` | Extend with `embed_query()` method |
| `StorageService` | Extend with `search()` method |
| `settings` | Add retrieval-specific settings |
| API patterns | Follow existing route/schema structure |
| Error handling | Follow existing `ErrorResponse` pattern |
