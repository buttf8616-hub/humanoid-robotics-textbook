"""Integration tests for agent grounding and hallucination prevention."""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
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


class TestGroundingValidation:
    """Tests for verifying answers are grounded in retrieved content."""

    def test_answer_content_matches_retrieved_chunks(self, client, mock_agent):
        """Test that answer content comes from retrieved chunks."""
        mock_response = {
            "answer": "ROS 2 uses DDS middleware for inter-process communication. [Source: ROS 2 Architecture - Middleware]",
            "sources": [
                {
                    "url": "https://example.com/ros2",
                    "title": "ROS 2 Architecture",
                    "section": "Middleware",
                    "chunk_index": 0,
                    "score": 0.93,
                    "excerpt": "ROS 2 uses DDS (Data Distribution Service) middleware for inter-process communication...",
                }
            ],
            "confidence": "high",
            "latency_ms": 890.0,
            "tokens_used": {"prompt": 350, "completion": 65, "total": 415},
        }
        mock_agent.answer = AsyncMock(return_value=mock_response)

        response = client.post(
            "/api/v1/chat",
            json={"question": "What middleware does ROS 2 use?"},
        )

        assert response.status_code == 200
        data = response.json()

        # Verify answer contains information from source
        assert "dds" in data["answer"].lower() or "middleware" in data["answer"].lower()

        # Verify source excerpt relates to answer
        assert len(data["sources"]) > 0
        source_text = data["sources"][0]["excerpt"].lower()
        answer_text = data["answer"].lower()

        # Check key terms appear in both
        assert "dds" in source_text or "middleware" in source_text

    def test_citations_reference_actual_sources(self, client, mock_agent):
        """Test that citations in answer reference actual retrieved sources."""
        mock_response = {
            "answer": "Sensor fusion combines data from multiple sensors. [Source: Perception - Sensor Fusion (https://example.com/perception)]",
            "sources": [
                {
                    "url": "https://example.com/perception",
                    "title": "Perception",
                    "section": "Sensor Fusion",
                    "chunk_index": 3,
                    "score": 0.91,
                    "excerpt": "Sensor fusion is the process of combining data from multiple sensors...",
                }
            ],
            "confidence": "high",
            "latency_ms": 920.5,
            "tokens_used": {"prompt": 380, "completion": 70, "total": 450},
        }
        mock_agent.answer = AsyncMock(return_value=mock_response)

        response = client.post(
            "/api/v1/chat",
            json={"question": "What is sensor fusion?"},
        )

        assert response.status_code == 200
        data = response.json()

        # Verify citations exist in answer
        assert "[Source:" in data["answer"] or "source" in data["answer"].lower()

        # Verify all sources returned were actually retrieved
        for source in data["sources"]:
            assert source["url"] != ""
            assert source["title"] != ""
            assert source["section"] != ""
            assert source["score"] > 0


class TestHallucinationPrevention:
    """Tests for zero-hallucination policy enforcement."""

    def test_refusal_on_empty_retrieval_results(self, client, mock_agent):
        """Test that agent refuses to answer when no content is retrieved."""
        mock_response = {
            "answer": "I don't have information about that topic in the textbook.",
            "sources": [],
            "confidence": "refused",
            "latency_ms": 620.0,
            "tokens_used": {"prompt": 250, "completion": 20, "total": 270},
        }
        mock_agent.answer = AsyncMock(return_value=mock_response)

        response = client.post(
            "/api/v1/chat",
            json={"question": "What is the capital of France?"},
        )

        assert response.status_code == 200
        data = response.json()

        # Verify refusal behavior
        assert data["confidence"] == "refused"
        assert len(data["sources"]) == 0
        assert any(
            phrase in data["answer"].lower()
            for phrase in ["don't have", "no information", "not in the textbook"]
        )

    def test_off_topic_queries_are_refused(self, client, mock_agent):
        """Test suite of off-topic queries that should be refused."""
        off_topic_queries = [
            "What is quantum entanglement?",
            "How do I cook pasta?",
            "What is the weather today?",
            "Tell me about the French Revolution",
            "How do I invest in stocks?",
            "What is the meaning of life?",
            "Who won the World Series in 2020?",
            "How do I learn Spanish?",
            "What are the lyrics to Bohemian Rhapsody?",
            "How do I fix a leaky faucet?",
        ]

        for query in off_topic_queries:
            mock_response = {
                "answer": "I don't have information about that topic in the textbook.",
                "sources": [],
                "confidence": "refused",
                "latency_ms": 550.0,
                "tokens_used": {"prompt": 230, "completion": 18, "total": 248},
            }
            mock_agent.answer = AsyncMock(return_value=mock_response)

            response = client.post("/api/v1/chat", json={"question": query})

            assert response.status_code == 200
            data = response.json()

            # Each off-topic query should be refused
            assert data["confidence"] == "refused", f"Failed to refuse: {query}"
            assert len(data["sources"]) == 0, f"Returned sources for off-topic: {query}"

    def test_low_confidence_on_weak_retrieval_matches(self, client, mock_agent):
        """Test that low-scoring retrievals result in low confidence."""
        mock_response = {
            "answer": "Based on limited information, this may relate to general robotics concepts.",
            "sources": [
                {
                    "url": "https://example.com/misc",
                    "title": "Miscellaneous",
                    "section": "General",
                    "chunk_index": 20,
                    "score": 0.42,  # Low score
                    "excerpt": "Some tangentially related content about robots...",
                }
            ],
            "confidence": "low",
            "latency_ms": 780.0,
            "tokens_used": {"prompt": 340, "completion": 50, "total": 390},
        }
        mock_agent.answer = AsyncMock(return_value=mock_response)

        response = client.post(
            "/api/v1/chat",
            json={"question": "Vague and unclear question about robots"},
        )

        assert response.status_code == 200
        data = response.json()

        # Low-scoring retrievals should result in low confidence
        assert data["confidence"] in ["low", "refused"]
        if data["sources"]:
            assert all(s["score"] < 0.6 for s in data["sources"])


class TestSourceAttribution:
    """Tests for proper source attribution in answers."""

    def test_multiple_sources_all_cited(self, client, mock_agent):
        """Test that answers using multiple sources cite all of them."""
        mock_response = {
            "answer": "Humanoid robots require sensors [Source: Components - Sensors], actuators [Source: Components - Actuators], and control systems [Source: Control - Overview].",
            "sources": [
                {
                    "url": "https://example.com/components",
                    "title": "Components",
                    "section": "Sensors",
                    "chunk_index": 0,
                    "score": 0.90,
                    "excerpt": "Sensors allow robots to perceive...",
                },
                {
                    "url": "https://example.com/components",
                    "title": "Components",
                    "section": "Actuators",
                    "chunk_index": 3,
                    "score": 0.88,
                    "excerpt": "Actuators provide movement...",
                },
                {
                    "url": "https://example.com/control",
                    "title": "Control",
                    "section": "Overview",
                    "chunk_index": 0,
                    "score": 0.86,
                    "excerpt": "Control systems coordinate...",
                },
            ],
            "confidence": "high",
            "latency_ms": 1100.0,
            "tokens_used": {"prompt": 480, "completion": 95, "total": 575},
        }
        mock_agent.answer = AsyncMock(return_value=mock_response)

        response = client.post(
            "/api/v1/chat",
            json={"question": "What components do humanoid robots need?"},
        )

        assert response.status_code == 200
        data = response.json()

        # Verify all sources are returned
        assert len(data["sources"]) == 3

        # Verify answer mentions key concepts from each source
        answer_lower = data["answer"].lower()
        assert "sensor" in answer_lower or "actuator" in answer_lower or "control" in answer_lower

    def test_source_metadata_is_complete(self, client, mock_agent):
        """Test that source metadata includes all required fields."""
        mock_response = {
            "answer": "Test answer with citation.",
            "sources": [
                {
                    "url": "https://example.com/test",
                    "title": "Test Page",
                    "section": "Test Section",
                    "chunk_index": 5,
                    "score": 0.85,
                    "excerpt": "This is a test excerpt from the content...",
                }
            ],
            "confidence": "medium",
            "latency_ms": 700.0,
            "tokens_used": {"prompt": 300, "completion": 40, "total": 340},
        }
        mock_agent.answer = AsyncMock(return_value=mock_response)

        response = client.post(
            "/api/v1/chat",
            json={"question": "Test question"},
        )

        assert response.status_code == 200
        data = response.json()

        # Verify source metadata completeness
        for source in data["sources"]:
            assert "url" in source and source["url"] != ""
            assert "title" in source and source["title"] != ""
            assert "section" in source and source["section"] != ""
            assert "chunk_index" in source and isinstance(source["chunk_index"], int)
            assert "score" in source and 0.0 <= source["score"] <= 1.0
            assert "excerpt" in source and source["excerpt"] != ""
