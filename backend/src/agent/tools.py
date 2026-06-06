"""Tool definitions for the AI agent."""
import httpx
import time
from typing import Annotated, Optional

# Note: We'll use OpenAI's function calling but with OpenRouter as the backend
# The @function_tool decorator isn't actually from OpenAI Agents SDK
# Instead, we'll define tools using OpenAI's function calling format

# Circuit breaker state for retrieval service
_circuit_breaker = {
    "failure_count": 0,
    "last_failure_time": 0,
    "state": "closed",  # closed, open, half_open
    "failure_threshold": 5,
    "timeout_duration": 30,  # seconds
}


async def retrieve_book_content(
    query: Annotated[str, "The search query or user's question"],
    top_k: Annotated[int, "Number of results to return (1-50)"] = 5,
    url_filter: Annotated[Optional[str], "Exact URL to filter results"] = None,
    section_filter: Annotated[Optional[str], "Section name substring to filter"] = None,
) -> dict:
    """Retrieve relevant content from the Physical AI & Humanoid Robotics textbook.

    This tool searches the textbook's vector database and returns relevant chunks
    based on semantic similarity to the query.

    IMPORTANT: You MUST call this tool before answering any user question.
    Never provide answers without retrieved content.

    Args:
        query: The user's question or search query
        top_k: Number of results to return (1-50, default 5)
        url_filter: Optional exact URL to filter results to
        section_filter: Optional section name substring to filter results

    Returns:
        Dictionary containing:
        - results: List of relevant book chunks with content, url, title, section, score
        - total_count: Number of results returned
        - latency_ms: Time taken to retrieve results
        - filters_applied: Dictionary of filters that were applied
    """
    # Check circuit breaker state
    current_time = time.time()

    if _circuit_breaker["state"] == "open":
        # Check if timeout has passed to transition to half-open
        if current_time - _circuit_breaker["last_failure_time"] > _circuit_breaker["timeout_duration"]:
            _circuit_breaker["state"] = "half_open"
        else:
            # Circuit is open, fail fast
            return {
                "results": [],
                "total_count": 0,
                "latency_ms": 0,
                "filters_applied": {},
                "error": "Retrieval service circuit breaker open (too many failures)",
            }

    # Call the internal retrieval endpoint
    async with httpx.AsyncClient(timeout=3.0) as client:
        try:
            response = await client.post(
                "http://localhost:8000/api/v1/search",
                json={
                    "query": query,
                    "top_k": top_k,
                    "url_filter": url_filter,
                    "section_filter": section_filter,
                },
            )
            response.raise_for_status()

            # Success - reset circuit breaker
            if _circuit_breaker["state"] == "half_open":
                _circuit_breaker["state"] = "closed"
                _circuit_breaker["failure_count"] = 0

            return response.json()

        except httpx.TimeoutException:
            _record_failure()
            return {
                "results": [],
                "total_count": 0,
                "latency_ms": 0,
                "filters_applied": {},
                "error": "Retrieval service timeout",
            }
        except httpx.HTTPError as e:
            _record_failure()
            return {
                "results": [],
                "total_count": 0,
                "latency_ms": 0,
                "filters_applied": {},
                "error": f"Retrieval service error: {str(e)}",
            }


def _record_failure():
    """Record a failure and update circuit breaker state."""
    _circuit_breaker["failure_count"] += 1
    _circuit_breaker["last_failure_time"] = time.time()

    if _circuit_breaker["failure_count"] >= _circuit_breaker["failure_threshold"]:
        _circuit_breaker["state"] = "open"


# Define the tool schema for OpenAI function calling
RETRIEVE_BOOK_CONTENT_SCHEMA = {
    "type": "function",
    "function": {
        "name": "retrieve_book_content",
        "description": """Retrieve relevant content from the Physical AI & Humanoid Robotics textbook based on a search query. Returns book chunks with source metadata.

IMPORTANT: You MUST call this tool before answering any user question. Never provide answers without retrieved content.""",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query or user's question",
                },
                "top_k": {
                    "type": "integer",
                    "description": "Number of results to return (1-50)",
                    "default": 5,
                    "minimum": 1,
                    "maximum": 50,
                },
                "url_filter": {
                    "type": "string",
                    "description": "Optional exact URL to filter results to",
                },
                "section_filter": {
                    "type": "string",
                    "description": "Optional section name substring to filter results",
                },
            },
            "required": ["query"],
        },
    },
}
