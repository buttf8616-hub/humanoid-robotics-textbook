# Quick Start: AI Agent with RAG

This guide shows how to interact with the AI agent that provides grounded answers from the Physical AI & Humanoid Robotics textbook.

## Prerequisites

1. Backend server running on `http://localhost:8000`
2. OpenRouter API key configured in `.env`
3. Textbook content ingested into vector database

## Basic Usage

### 1. Simple Question

Ask a question about the textbook:

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is embodied intelligence?"
  }'
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

### 2. Retrieve More Context

Increase the number of retrieved chunks with `top_k`:

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How does ROS 2 handle inter-process communication?",
    "top_k": 10
  }'
```

### 3. Focus on Specific Content (User-Selected Text)

Ask questions about specific sections of the textbook:

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What sensor types are discussed?",
    "selected_context": {
      "url": "https://buttf8616-hub.github.io/humanoid-robotics-textbook/physical-ai/sensors",
      "section": "Sensor Types"
    }
  }'
```

This limits answers to only the specified URL and section.

### 4. Multi-Turn Conversation

Maintain conversation context for follow-up questions:

**First turn:**
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Tell me about ROS 2 middleware"
  }'
```

**Second turn with context:**
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are its key features?",
    "conversation_history": [
      {
        "role": "user",
        "content": "Tell me about ROS 2 middleware"
      },
      {
        "role": "assistant",
        "content": "ROS 2 uses DDS (Data Distribution Service) middleware..."
      }
    ]
  }'
```

The agent will understand "its" refers to "ROS 2 middleware" from the previous turn.

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `answer` | string | Generated answer with citations |
| `sources` | array | Retrieved book chunks used for the answer |
| `confidence` | string | `high`, `medium`, `low`, or `refused` |
| `latency_ms` | float | Total response time in milliseconds |
| `tokens_used` | object | LLM token usage (prompt, completion, total) |

### Source Object Fields

| Field | Type | Description |
|-------|------|-------------|
| `url` | string | Source page URL |
| `title` | string | Page title |
| `section` | string | Section header |
| `chunk_index` | integer | Position in page (0-based) |
| `score` | float | Relevance score (0.0-1.0, cosine similarity) |
| `excerpt` | string | First 100 characters of content |

## Confidence Levels

- **high**: Multiple high-scoring sources (score ≥ 0.8, ≥ 3 sources)
- **medium**: Good sources (score ≥ 0.6, ≥ 2 sources)
- **low**: Weak sources (score < 0.6 or few sources)
- **refused**: No relevant content found, off-topic query

## Error Handling

### Empty Question (422)
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"question": ""}'
```

Returns `422 Unprocessable Entity`

### Service Unavailable (503)

When OpenRouter API or retrieval service is down:

```json
{
  "detail": {
    "error": "service_unavailable",
    "message": "AI agent service temporarily unavailable",
    "details": {
      "service": "openrouter",
      "retry_after": 5
    }
  }
}
```

## Best Practices

1. **Be Specific**: Ask clear, focused questions about robotics topics
2. **Use Context Filters**: For long documents, use `selected_context` to narrow scope
3. **Check Confidence**: Low confidence answers may need more context or rephrasing
4. **Maintain History**: For multi-turn conversations, include last 3-6 messages
5. **Handle Refusals**: If the agent refuses, the topic may not be in the textbook

## Example: Complete Interaction

```python
import requests

# Configuration
BASE_URL = "http://localhost:8000"
CHAT_ENDPOINT = f"{BASE_URL}/api/v1/chat"

# Ask a question
response = requests.post(
    CHAT_ENDPOINT,
    json={
        "question": "What is sensor fusion and why is it important?",
        "top_k": 5
    }
)

data = response.json()

print(f"Answer: {data['answer']}")
print(f"Confidence: {data['confidence']}")
print(f"Sources: {len(data['sources'])} chunks")
print(f"Latency: {data['latency_ms']:.2f}ms")

# Follow-up question
follow_up = requests.post(
    CHAT_ENDPOINT,
    json={
        "question": "Give me examples of algorithms used for it",
        "conversation_history": [
            {"role": "user", "content": "What is sensor fusion and why is it important?"},
            {"role": "assistant", "content": data['answer']}
        ]
    }
)

print(f"\nFollow-up Answer: {follow_up.json()['answer']}")
```

## Monitoring

Track these metrics for production use:

- **Token Usage**: Monitor `tokens_used.total` to track API costs
- **Latency**: Average `latency_ms` for performance
- **Refusal Rate**: Percentage of `refused` responses (indicates poor query-content match)
- **Confidence Distribution**: Track high/medium/low distribution for quality

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Agent always refuses | Check textbook is ingested, try broader questions |
| High latency | Reduce `top_k`, check OpenRouter API status |
| Low confidence | Rephrase question, use more specific terms |
| Empty sources | Verify vector database has content for topic |

## Next Steps

- Integrate into web frontend for interactive chat
- Add user feedback collection for answer quality
- Implement caching for common questions
- Set up monitoring and alerting for production
