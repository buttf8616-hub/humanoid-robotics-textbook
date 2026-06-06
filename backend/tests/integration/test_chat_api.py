"""Integration tests for chat API endpoint."""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_agent():
    """Mock the AgentService for API tests."""
    with patch("src.api.routes.AgentService") as mock_cls:
        mock_service = MagicMock()
        mock_cls.return_value = mock_service
        yield mock_service


class TestChatEndpoint:
    """Tests for POST /api/v1/chat endpoint."""

    def test_chat_returns_200_with_grounded_answer(self, client, mock_agent):
        """Test successful chat returns 200 with grounded answer and sources."""
        mock_response = {
            "answer": "Embodied intelligence refers to the concept that intelligence arises from the interaction between an agent's body and its environment. [Source: Introduction - Core Concepts]",
            "sources": [
                {
                    "url": "https://example.com/chapter-1",
                    "title": "Introduction to Physical AI",
                    "section": "Core Concepts",
                    "chunk_index": 0,
                    "score": 0.92,
                    "excerpt": "Embodied intelligence refers to the concept that intelligence arises from...",
                }
            ],
            "confidence": "high",
            "latency_ms": 1250.5,
            "tokens_used": {
                "prompt": 450,
                "completion": 120,
                "total": 570,
            },
        }
        mock_agent.answer = AsyncMock(return_value=mock_response)

        response = client.post(
            "/api/v1/chat",
            json={"question": "What is embodied intelligence?"},
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "answer" in data
        assert "sources" in data
        assert "confidence" in data
        assert "latency_ms" in data
        assert "tokens_used" in data

        # Verify answer content
        assert len(data["answer"]) > 0
        assert "embodied intelligence" in data["answer"].lower()

        # Verify sources
        assert len(data["sources"]) == 1
        assert data["sources"][0]["url"] == "https://example.com/chapter-1"
        assert data["sources"][0]["score"] == 0.92

        # Verify confidence
        assert data["confidence"] == "high"

        # Verify tokens
        assert data["tokens_used"]["prompt"] == 450
        assert data["tokens_used"]["completion"] == 120
        assert data["tokens_used"]["total"] == 570

        # Verify AgentService was called with correct parameters
        mock_agent.answer.assert_called_once()
        call_kwargs = mock_agent.answer.call_args[1]
        assert call_kwargs["question"] == "What is embodied intelligence?"
        assert call_kwargs["top_k"] == 5  # default value

    def test_chat_refuses_off_topic_query(self, client, mock_agent):
        """Test that agent refuses to answer off-topic queries."""
        mock_response = {
            "answer": "I don't have information about quantum computing in the textbook.",
            "sources": [],
            "confidence": "refused",
            "latency_ms": 850.2,
            "tokens_used": {
                "prompt": 320,
                "completion": 25,
                "total": 345,
            },
        }
        mock_agent.answer = AsyncMock(return_value=mock_response)

        response = client.post(
            "/api/v1/chat",
            json={"question": "What is quantum computing?"},
        )

        assert response.status_code == 200
        data = response.json()

        # Verify refusal response
        assert data["confidence"] == "refused"
        assert data["sources"] == []
        assert "don't have information" in data["answer"].lower()

    def test_chat_rejects_empty_question(self, client, mock_agent):
        """Test that empty questions are rejected with 422 (Pydantic validation)."""
        response = client.post(
            "/api/v1/chat",
            json={"question": ""},
        )

        # Pydantic's min_length=1 constraint returns 422
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_chat_rejects_whitespace_only_question(self, client, mock_agent):
        """Test that whitespace-only questions are rejected with 400."""
        response = client.post(
            "/api/v1/chat",
            json={"question": "   "},
        )

        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["error"] == "validation_error"

    def test_chat_passes_top_k_parameter(self, client, mock_agent):
        """Test that top_k parameter is passed to AgentService."""
        mock_response = {
            "answer": "Test answer",
            "sources": [],
            "confidence": "medium",
            "latency_ms": 500.0,
            "tokens_used": {
                "prompt": 200,
                "completion": 50,
                "total": 250,
            },
        }
        mock_agent.answer = AsyncMock(return_value=mock_response)

        response = client.post(
            "/api/v1/chat",
            json={"question": "Test question", "top_k": 10},
        )

        assert response.status_code == 200

        # Verify top_k was passed
        mock_agent.answer.assert_called_once()
        call_kwargs = mock_agent.answer.call_args[1]
        assert call_kwargs["top_k"] == 10

    def test_chat_handles_agent_service_error(self, client, mock_agent):
        """Test that agent service errors return 503."""
        mock_agent.answer = AsyncMock(side_effect=Exception("OpenRouter API timeout"))

        response = client.post(
            "/api/v1/chat",
            json={"question": "What is embodied intelligence?"},
        )

        assert response.status_code == 503
        data = response.json()
        assert "detail" in data
        assert "error" in data["detail"]
        assert data["detail"]["error"] == "service_unavailable"

    def test_chat_returns_low_confidence_for_weak_matches(self, client, mock_agent):
        """Test that low-scoring retrieval results return low confidence."""
        mock_response = {
            "answer": "Based on limited information, this topic may be related to...",
            "sources": [
                {
                    "url": "https://example.com/chapter-5",
                    "title": "Advanced Topics",
                    "section": "Miscellaneous",
                    "chunk_index": 12,
                    "score": 0.45,  # Low score
                    "excerpt": "Some tangentially related content...",
                }
            ],
            "confidence": "low",
            "latency_ms": 920.0,
            "tokens_used": {
                "prompt": 380,
                "completion": 85,
                "total": 465,
            },
        }
        mock_agent.answer = AsyncMock(return_value=mock_response)

        response = client.post(
            "/api/v1/chat",
            json={"question": "What is the meaning of life?"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["confidence"] == "low"
        assert data["sources"][0]["score"] == 0.45

    def test_chat_includes_multiple_sources(self, client, mock_agent):
        """Test that multiple sources are returned and formatted correctly."""
        mock_response = {
            "answer": "Humanoid robots combine multiple technologies including sensors, actuators, and control systems.",
            "sources": [
                {
                    "url": "https://example.com/chapter-2",
                    "title": "Robot Components",
                    "section": "Sensors",
                    "chunk_index": 0,
                    "score": 0.88,
                    "excerpt": "Sensors are critical components that allow robots to perceive...",
                },
                {
                    "url": "https://example.com/chapter-2",
                    "title": "Robot Components",
                    "section": "Actuators",
                    "chunk_index": 5,
                    "score": 0.85,
                    "excerpt": "Actuators provide the physical movement and force...",
                },
                {
                    "url": "https://example.com/chapter-3",
                    "title": "Control Systems",
                    "section": "Overview",
                    "chunk_index": 0,
                    "score": 0.82,
                    "excerpt": "Control systems coordinate the operation of sensors and actuators...",
                },
            ],
            "confidence": "high",
            "latency_ms": 1450.3,
            "tokens_used": {
                "prompt": 520,
                "completion": 95,
                "total": 615,
            },
        }
        mock_agent.answer = AsyncMock(return_value=mock_response)

        response = client.post(
            "/api/v1/chat",
            json={"question": "What components make up a humanoid robot?", "top_k": 5},
        )

        assert response.status_code == 200
        data = response.json()

        # Verify all 3 sources are returned
        assert len(data["sources"]) == 3
        assert data["sources"][0]["section"] == "Sensors"
        assert data["sources"][1]["section"] == "Actuators"
        assert data["sources"][2]["section"] == "Overview"

    def test_chat_with_selected_context_filters_results(self, client, mock_agent):
        """Test that selected_context filters retrieval to specific URL/section."""
        mock_response = {
            "answer": "In the Sensors section, three main types are discussed: visual, tactile, and proprioceptive sensors.",
            "sources": [
                {
                    "url": "https://example.com/chapter-2",
                    "title": "Robot Components",
                    "section": "Sensors",
                    "chunk_index": 0,
                    "score": 0.91,
                    "excerpt": "Visual sensors include cameras and depth sensors...",
                },
                {
                    "url": "https://example.com/chapter-2",
                    "title": "Robot Components",
                    "section": "Sensors",
                    "chunk_index": 1,
                    "score": 0.88,
                    "excerpt": "Tactile sensors measure contact forces...",
                },
            ],
            "confidence": "high",
            "latency_ms": 950.2,
            "tokens_used": {
                "prompt": 380,
                "completion": 75,
                "total": 455,
            },
        }
        mock_agent.answer = AsyncMock(return_value=mock_response)

        response = client.post(
            "/api/v1/chat",
            json={
                "question": "What types of sensors are there?",
                "selected_context": {
                    "url": "https://example.com/chapter-2",
                    "section": "Sensors",
                },
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Verify all sources match the filtered URL and section
        assert len(data["sources"]) == 2
        for source in data["sources"]:
            assert source["url"] == "https://example.com/chapter-2"
            assert source["section"] == "Sensors"

        # Verify AgentService was called with filters
        mock_agent.answer.assert_called_once()
        call_kwargs = mock_agent.answer.call_args[1]
        assert call_kwargs["url_filter"] == "https://example.com/chapter-2"
        assert call_kwargs["section_filter"] == "Sensors"

    def test_chat_acknowledges_insufficient_filtered_context(self, client, mock_agent):
        """Test that agent acknowledges when filtered context has insufficient information."""
        mock_response = {
            "answer": "I don't have information about quantum computing in the Sensors section of this chapter.",
            "sources": [],
            "confidence": "refused",
            "latency_ms": 720.5,
            "tokens_used": {
                "prompt": 290,
                "completion": 30,
                "total": 320,
            },
        }
        mock_agent.answer = AsyncMock(return_value=mock_response)

        response = client.post(
            "/api/v1/chat",
            json={
                "question": "What is quantum computing?",
                "selected_context": {
                    "url": "https://example.com/chapter-2",
                    "section": "Sensors",
                },
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Verify refusal due to insufficient filtered context
        assert data["confidence"] == "refused"
        assert data["sources"] == []
        assert "don't have information" in data["answer"].lower()

    def test_multi_turn_conversation_maintains_context(self, client, mock_agent):
        """Test that conversation history maintains context across turns."""
        # First turn: Ask about embodied intelligence
        mock_response_1 = {
            "answer": "Embodied intelligence refers to intelligence arising from body-environment interaction.",
            "sources": [
                {
                    "url": "https://example.com/chapter-1",
                    "title": "Introduction",
                    "section": "Core Concepts",
                    "chunk_index": 0,
                    "score": 0.92,
                    "excerpt": "Embodied intelligence...",
                }
            ],
            "confidence": "high",
            "latency_ms": 980.2,
            "tokens_used": {"prompt": 300, "completion": 60, "total": 360},
        }

        # Second turn: Ask follow-up with pronoun
        mock_response_2 = {
            "answer": "Its key components include sensors, actuators, and control systems that enable physical interaction.",
            "sources": [
                {
                    "url": "https://example.com/chapter-1",
                    "title": "Introduction",
                    "section": "Components",
                    "chunk_index": 2,
                    "score": 0.89,
                    "excerpt": "Key components of embodied systems...",
                }
            ],
            "confidence": "high",
            "latency_ms": 1050.5,
            "tokens_used": {"prompt": 420, "completion": 70, "total": 490},
        }

        mock_agent.answer = AsyncMock(side_effect=[mock_response_1, mock_response_2])

        # First question
        response1 = client.post(
            "/api/v1/chat",
            json={"question": "What is embodied intelligence?"},
        )
        assert response1.status_code == 200
        data1 = response1.json()

        # Second question with conversation history
        response2 = client.post(
            "/api/v1/chat",
            json={
                "question": "What are its key components?",
                "conversation_history": [
                    {"role": "user", "content": "What is embodied intelligence?"},
                    {"role": "assistant", "content": data1["answer"]},
                ],
            },
        )
        assert response2.status_code == 200
        data2 = response2.json()

        # Verify second call included conversation history
        assert mock_agent.answer.call_count == 2
        second_call_kwargs = mock_agent.answer.call_args_list[1][1]
        assert "conversation_history" in second_call_kwargs
        assert second_call_kwargs["conversation_history"] is not None
        assert len(second_call_kwargs["conversation_history"]) == 2

    def test_pronoun_resolution_in_follow_up(self, client, mock_agent):
        """Test that pronouns in follow-up questions are resolved using context."""
        mock_response = {
            "answer": "ROS 2 uses DDS (Data Distribution Service) for its communication middleware.",
            "sources": [
                {
                    "url": "https://example.com/chapter-3",
                    "title": "ROS 2 Architecture",
                    "section": "Middleware",
                    "chunk_index": 1,
                    "score": 0.91,
                    "excerpt": "ROS 2 uses DDS for communication...",
                }
            ],
            "confidence": "high",
            "latency_ms": 920.0,
            "tokens_used": {"prompt": 380, "completion": 55, "total": 435},
        }
        mock_agent.answer = AsyncMock(return_value=mock_response)

        # Follow-up question using "it" to refer to ROS 2
        response = client.post(
            "/api/v1/chat",
            json={
                "question": "What middleware does it use?",
                "conversation_history": [
                    {"role": "user", "content": "Tell me about ROS 2"},
                    {
                        "role": "assistant",
                        "content": "ROS 2 is a robotics middleware framework...",
                    },
                ],
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Verify answer resolves the pronoun correctly
        assert "ros 2" in data["answer"].lower() or "dds" in data["answer"].lower()

        # Verify conversation history was passed
        mock_agent.answer.assert_called_once()
        call_kwargs = mock_agent.answer.call_args[1]
        assert call_kwargs["conversation_history"] is not None
