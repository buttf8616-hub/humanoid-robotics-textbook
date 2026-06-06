# Quickstart: RAG Retrieval Pipeline

**Feature**: 002-retrieval-pipeline
**Prerequisites**: Spec 001 (Book Ingestion Pipeline) completed and collection populated

## Setup

### 1. Environment Variables

Ensure the following are set in `backend/.env` (should already exist from Spec 001):

```bash
COHERE_API_KEY=your_cohere_api_key
QDRANT_URL=your_qdrant_cloud_url
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_COLLECTION_NAME=book-chunks
```

### 2. Install Dependencies

```bash
cd backend
uv sync
```

### 3. Run the Server

```bash
uv run uvicorn src.main:app --reload
```

Server starts at `http://localhost:8000`

## API Usage

### Basic Search

```bash
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "What is embodied intelligence?"}'
```

### Search with Top-K

```bash
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "ROS 2 fundamentals", "top_k": 10}'
```

### Search with Filters

```bash
# Filter by URL
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "sensor integration",
    "url_filter": "https://buttf8616-hub.github.io/humanoid-robotics-textbook/docs/module-2/chapter-1"
  }'

# Filter by section
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "control systems",
    "section_filter": "Introduction"
  }'
```

## Expected Response

```json
{
  "results": [
    {
      "content": "Embodied intelligence refers to the concept that...",
      "url": "https://buttf8616-hub.github.io/humanoid-robotics-textbook/docs/module-1/chapter-2",
      "title": "Embodied Intelligence Principles",
      "section": "Core Concepts",
      "chunk_index": 0,
      "score": 0.89
    }
  ],
  "total_count": 1,
  "latency_ms": 234.5,
  "filters_applied": {}
}
```

## Testing

### Run Unit Tests

```bash
cd backend
uv run pytest tests/unit/ -v
```

### Run Integration Tests

Requires live Qdrant and Cohere connections:

```bash
cd backend
uv run pytest tests/integration/ -v
```

### Manual Validation Queries

Test these queries to validate retrieval quality:

| Query | Expected Content Area |
|-------|----------------------|
| "What is embodied intelligence?" | Physical AI fundamentals |
| "ROS 2 architecture" | ROS 2 chapter |
| "sensor fusion techniques" | Perception/sensors |
| "robot motion planning" | Control/locomotion |
| "humanoid robot design" | Humanoid robotics |

## Troubleshooting

### Empty Results

1. Verify collection is populated: `GET /api/v1/verify`
2. Check if filters are too restrictive
3. Try broader query terms

### High Latency

1. Check Cohere API status
2. Check Qdrant Cloud status
3. Review `latency_ms` in response to identify bottleneck

### 503 Service Unavailable

1. Verify API keys are correct
2. Check service connectivity
3. Wait and retry (rate limiting)

## API Documentation

Interactive docs available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
