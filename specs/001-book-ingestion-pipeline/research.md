# Technical Research: Book Ingestion Pipeline

**Feature**: 001-book-ingestion-pipeline
**Date**: 2025-01-07

## Technology Decisions

### Python Version: 3.11

**Rationale**:
- Compatible with all dependencies (FastAPI, Cohere, Qdrant)
- 10-60% performance improvement over 3.10
- Stable and well-supported on deployment platforms
- Better error messages and debugging

### Package Manager: uv

**Rationale**:
- 10-100x faster than pip
- Built-in lockfile support for reproducibility
- Drop-in replacement for pip commands
- Active development by Astral (creators of Ruff)

### Web Framework: FastAPI

**Rationale**:
- Native async support for concurrent API calls
- Automatic OpenAPI documentation
- Pydantic integration for validation
- High performance (Starlette + Uvicorn)

### HTTP Client: httpx

**Rationale**:
- Async support (required for FastAPI)
- Similar API to requests
- Built-in retry and timeout support
- HTTP/2 support

### HTML Parser: BeautifulSoup4

**Rationale**:
- Battle-tested HTML parsing
- Flexible selector support (CSS, XPath-like)
- Handles malformed HTML gracefully
- Good documentation

### Embedding Model: Cohere embed-english-v3.0

**Rationale**:
- 1024 dimensions (good balance of quality/size)
- Excellent for semantic search
- Batch API support (up to 96 texts)
- Free tier available for development

**Specifications**:
- Dimension: 1024
- Max tokens per text: 512
- Rate limit (free): 100 calls/minute

### Vector Database: Qdrant Cloud

**Rationale**:
- Free tier (1GB storage, 1M vectors)
- Native Python client
- Excellent filtering capabilities
- Easy to self-host if needed later

**Configuration**:
- Distance metric: Cosine
- Vector size: 1024
- Payload indexing: url, title, section

### Tokenizer: tiktoken (cl100k_base)

**Rationale**:
- Fast tokenization
- Compatible with most modern embedding models
- Used by OpenAI, similar to Cohere tokenization

## API Rate Limits & Quotas

| Service | Free Tier Limit | Strategy |
|---------|-----------------|----------|
| Cohere Embed | 100 calls/min, 10k/month | Batch requests, backoff |
| Qdrant Cloud | 1GB storage, 1M vectors | Monitor usage |
| GitHub Pages | No rate limit | Cache responses |

## Chunking Strategy

**Configuration**:
- Max chunk size: 1000 tokens
- Overlap: 100 tokens
- Min chunk size: 50 tokens (merge smaller)

**Algorithm**:
1. Split text by section headers (preserve metadata)
2. For each section, split by paragraphs
3. Accumulate paragraphs until ~900 tokens
4. If paragraph exceeds limit, split by sentences
5. Add 100-token overlap from previous chunk

## Deduplication Strategy

**Approach**: Content-based hashing

1. Generate SHA-256 hash of chunk content
2. Use hash as Qdrant point ID
3. Upsert (update or insert) based on ID
4. Re-ingestion automatically updates changed content

## Error Handling Strategy

| Error Type | Response |
|------------|----------|
| Network timeout | Retry 3x with exponential backoff |
| Rate limit (429) | Wait for Retry-After header, then retry |
| Server error (5xx) | Retry 3x with backoff |
| Client error (4xx) | Log and skip, continue pipeline |
| Parse error | Log warning, skip page |

## Docusaurus Site Structure

**Expected Structure**:
```
/sitemap.xml          # List of all URLs
/docs/intro           # Introduction page
/docs/modules/...     # Chapter pages
```

**Content Selectors**:
- Main content: `article.markdown` or `main`
- Title: `h1` or `meta[property="og:title"]`
- Sections: `h2`, `h3` headers

## References

- [Cohere Embed Documentation](https://docs.cohere.com/docs/embeddings)
- [Qdrant Python Client](https://qdrant.tech/documentation/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [tiktoken Library](https://github.com/openai/tiktoken)
