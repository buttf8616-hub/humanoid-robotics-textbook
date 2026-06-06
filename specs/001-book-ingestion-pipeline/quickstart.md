# Quickstart: Book Ingestion Pipeline

**Feature**: 001-book-ingestion-pipeline

## Prerequisites

- Python 3.11+
- uv package manager (`pip install uv`)
- Cohere API key (free tier: https://dashboard.cohere.com/)
- Qdrant Cloud account (free tier: https://cloud.qdrant.io/)

## Setup

### 1. Clone and Navigate

```bash
cd humanoid-robotics-textbook
git checkout 001-book-ingestion-pipeline
cd backend
```

### 2. Install Dependencies

```bash
uv sync
```

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```bash
BOOK_BASE_URL=https://buttf8616-hub.github.io/humanoid-robotics-textbook
COHERE_API_KEY=your-cohere-api-key
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key
QDRANT_COLLECTION_NAME=book-chunks
```

### 4. Start Development Server

```bash
uv run uvicorn src.main:app --reload
```

Server starts at http://localhost:8000

## Usage

### Trigger Ingestion

```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"base_url": "https://buttf8616-hub.github.io/humanoid-robotics-textbook"}'
```

Response:
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "running",
  "message": "Ingestion started"
}
```

### Check Job Status

```bash
curl http://localhost:8000/ingest/status/{job_id}
```

### Verify Collection

```bash
curl http://localhost:8000/verify
```

### Check Specific URL

```bash
curl "http://localhost:8000/verify/url?url=https://..."
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Running Tests

```bash
uv run pytest
```

With coverage:
```bash
uv run pytest --cov=src --cov-report=html
```

## Deployment

### Hugging Face Spaces

1. Create new Space (Docker SDK)
2. Set secrets in Space settings:
   - `COHERE_API_KEY`
   - `QDRANT_URL`
   - `QDRANT_API_KEY`
3. Push code to Space repository

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Cohere rate limit | Wait 60 seconds, retry |
| Qdrant connection failed | Check QDRANT_URL and API key |
| Empty extraction | Check book URL is accessible |
| Token count mismatch | Ensure tiktoken is installed |
