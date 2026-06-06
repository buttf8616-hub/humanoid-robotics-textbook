# RAG Backend for Physical AI & Humanoid Robotics Book

Complete RAG (Retrieval-Augmented Generation) backend with ingestion and semantic search.

## Features

### Ingestion Pipeline
- Crawl deployed Docusaurus book pages
- Extract clean text from HTML
- Chunk text with token limits and overlap
- Generate embeddings with Cohere
- Store vectors in Qdrant Cloud
- Automatic deduplication via content hashing

### Retrieval Pipeline
- Semantic search over book content
- Configurable top-k retrieval (1-50 results)
- Metadata filtering by URL and section
- Sub-500ms query latency (P95)

## Setup

```bash
# Install dependencies
uv sync

# Copy environment file
cp .env.example .env
# Edit .env with your API keys

# Run development server
uv run uvicorn src.main:app --reload
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `COHERE_API_KEY` | Cohere API key for embeddings | Yes |
| `QDRANT_URL` | Qdrant Cloud cluster URL | Yes |
| `QDRANT_API_KEY` | Qdrant API key | Yes |
| `GEMINI_API_KEY` | Google Gemini API key for AI agent | Yes (for chat) |
| `QDRANT_COLLECTION_NAME` | Vector collection name | No (default: `book-chunks`) |
| `BOOK_BASE_URL` | Base URL of deployed book | No (default: textbook URL) |
| `GEMINI_MODEL` | Gemini model to use | No (default: `gemini-2.0-flash`) |
| `GEMINI_TEMPERATURE` | LLM temperature | No (default: `0.3`) |
| `GEMINI_MAX_TOKENS` | Max tokens per response | No (default: `2000`) |
| `AGENT_TIMEOUT_SECONDS` | Timeout for LLM requests | No (default: `4`) |

## API Endpoints

All API routes are prefixed with `/api/v1`.

### Ingestion Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/api/v1/ingest` | Trigger book ingestion |
| `GET` | `/api/v1/ingest/status/{job_id}` | Get job status |
| `GET` | `/api/v1/verify` | Get collection statistics |
| `GET` | `/api/v1/verify/url?url=<url>` | Get chunks for a specific URL |

### Retrieval Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/search` | Semantic search for book content |

#### POST /api/v1/search

Perform semantic search over stored book embeddings.

**Request Body:**
```json
{
  "query": "What is embodied intelligence?",
  "top_k": 5,                                    // Optional: 1-50, default 5
  "url_filter": "https://example.com/page",      // Optional: exact URL match
  "section_filter": "Introduction"               // Optional: section substring match
}
```

**Response:**
```json
{
  "results": [
    {
      "content": "Embodied intelligence refers to...",
      "url": "https://example.com/chapter-1",
      "title": "Introduction to Physical AI",
      "section": "Core Concepts",
      "chunk_index": 0,
      "score": 0.89
    }
  ],
  "total_count": 5,
  "latency_ms": 145.2,
  "filters_applied": {
    "url_filter": "https://example.com/page",
    "section_filter": "Introduction"
  }
}
```

**Parameters:**
- `query` (required): Natural language search query (1-1000 characters)
- `top_k` (optional): Number of results to return (1-50, default: 5)
- `url_filter` (optional): Filter results to specific URL (exact match)
- `section_filter` (optional): Filter results by section name (substring match)

**Error Responses:**
- `400`: Invalid query or parameters
- `503`: Service unavailable (Cohere or Qdrant error)

### Agent/Chat Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/chat` | Chat with AI agent for grounded answers |

#### POST /api/v1/chat

Chat with an AI agent that retrieves relevant book content and generates grounded answers with citations.

**Request Body:**
```json
{
  "question": "What is embodied intelligence?",
  "top_k": 5,                                    // Optional: 1-50, default 5
  "selected_context": {                          // Optional: focus on specific content
    "url": "https://example.com/page",           // Required if selected_context provided
    "section": "Introduction"                    // Optional: section filter
  },
  "conversation_history": [                      // Optional: for multi-turn conversations
    {
      "role": "user",
      "content": "Tell me about ROS 2"
    },
    {
      "role": "assistant",
      "content": "ROS 2 is a robotics middleware..."
    }
  ]
}
```

**Response:**
```json
{
  "answer": "Embodied intelligence refers to the concept that intelligence arises from the interaction between an agent's body and its environment. [Source: Introduction - Core Concepts]",
  "sources": [
    {
      "url": "https://example.com/chapter-1",
      "title": "Introduction to Physical AI",
      "section": "Core Concepts",
      "chunk_index": 0,
      "score": 0.92,
      "excerpt": "Embodied intelligence refers to..."
    }
  ],
  "confidence": "high",
  "latency_ms": 1250.5,
  "tokens_used": {
    "prompt": 450,
    "completion": 120,
    "total": 570
  }
}
```

**Parameters:**
- `question` (required): User's question about the textbook (min 1 character)
- `top_k` (optional): Number of chunks to retrieve (1-50, default: 5)
- `selected_context` (optional): Focus answers on specific URL/section
  - `url` (required): Exact URL to filter results
  - `section` (optional): Section name substring to filter
- `conversation_history` (optional): Previous messages for multi-turn conversations
  - Array of `{role: "user"|"assistant", content: string}` objects

**Confidence Levels:**
- `high`: Multiple high-scoring sources (≥0.8, ≥3 sources)
- `medium`: Good sources (≥0.6, ≥2 sources)
- `low`: Weak or few sources
- `refused`: No relevant content found, off-topic query

**Error Responses:**
- `400`: Invalid request (empty question)
- `422`: Validation error (malformed request)
- `503`: Service unavailable (Gemini or retrieval service error)

**Example curl commands:**

```bash
# Basic question
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is embodied intelligence?"
  }'

# Question with more context
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How does sensor fusion work?",
    "top_k": 10
  }'

# Focus on specific section
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What sensors are discussed?",
    "selected_context": {
      "url": "https://buttf8616-hub.github.io/humanoid-robotics-textbook/physical-ai/sensors",
      "section": "Sensor Types"
    }
  }'

# Multi-turn conversation
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are its main components?",
    "conversation_history": [
      {
        "role": "user",
        "content": "Tell me about ROS 2"
      },
      {
        "role": "assistant",
        "content": "ROS 2 is a robotics middleware framework..."
      }
    ]
  }'
```

## Testing

```bash
uv run pytest
```

## Deployment (Hugging Face Spaces)

### 1. Create a new Space

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Create new Space with Docker SDK
3. Select "Blank" template

### 2. Configure Secrets

Add these secrets in Space settings:

- `COHERE_API_KEY` - For generating embeddings
- `QDRANT_URL` - Qdrant Cloud cluster URL
- `QDRANT_API_KEY` - Qdrant authentication
- `GEMINI_API_KEY` - For AI agent (chat endpoint)

**Note:** The chat endpoint (`/api/v1/chat`) requires `GEMINI_API_KEY`. If not configured, the endpoint will return 503 errors.

### 3. Push Code

```bash
# Clone the Space repo
git clone https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME

# Copy backend files
cp -r backend/* YOUR_SPACE_NAME/

# Push to trigger build
cd YOUR_SPACE_NAME
git add .
git commit -m "Deploy book ingestion pipeline"
git push
```

### 4. Local Docker Testing

```bash
# Build image
docker build -t book-ingestion .

# Run container
docker run -p 7860:7860 \
  -e COHERE_API_KEY=your_key \
  -e QDRANT_URL=your_url \
  -e QDRANT_API_KEY=your_key \
  book-ingestion
```

## Usage Examples

### Ingesting Book Content

```bash
curl -X POST http://localhost:8000/api/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "base_url": "https://buttf8616-hub.github.io/humanoid-robotics-textbook"
  }'
```

### Semantic Search

```bash
# Basic search
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is embodied intelligence?"
  }'

# Search with more results
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "ROS 2 architecture",
    "top_k": 10
  }'

# Search with filters
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "sensor fusion",
    "url_filter": "https://buttf8616-hub.github.io/humanoid-robotics-textbook/docs/perception",
    "section_filter": "Sensors"
  }'
```

## Project Structure

```
backend/
├── src/
│   ├── api/
│   │   ├── routes.py      # API route handlers
│   │   └── schemas.py     # Request/response models
│   ├── config/
│   │   └── settings.py    # Configuration management
│   ├── models/
│   │   ├── book_page.py   # Crawled page model
│   │   ├── text_chunk.py  # Chunked text model
│   │   ├── retrieval.py   # Search models
│   │   ├── vector_record.py
│   │   └── ingestion_job.py
│   ├── services/
│   │   ├── crawler.py     # Web crawler
│   │   ├── extractor.py   # HTML text extraction
│   │   ├── chunker.py     # Text chunking
│   │   ├── embedder.py    # Cohere embeddings
│   │   ├── storage.py     # Qdrant operations
│   │   └── retriever.py   # Semantic search orchestration
│   └── main.py            # FastAPI app
├── tests/
│   ├── unit/              # Unit tests
│   │   ├── test_embedder.py
│   │   ├── test_storage_search.py
│   │   └── test_retriever.py
│   └── integration/       # Integration tests
│       ├── test_retrieval_api.py
│       └── test_retrieval_validation.py
├── Dockerfile
├── pyproject.toml
└── README.md
```
