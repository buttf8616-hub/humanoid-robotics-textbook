"""Retrieval validation tests for quality assurance.

These tests validate retrieval quality with predefined test queries
that should return contextually relevant results from the book content.

NOTE: These tests require actual data to be ingested into Qdrant.
Run the ingestion pipeline first before executing these tests.
"""
import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


class TestRetrievalValidation:
    """Validation tests for retrieval quality with real queries."""

    @pytest.mark.integration
    @pytest.mark.requires_data
    def test_embodied_intelligence_query(self, client):
        """Test query about embodied intelligence returns Physical AI content.

        Expected: Results should contain content from Physical AI fundamentals
        discussing embodied intelligence, physical interaction, and real-world
        interaction capabilities.
        """
        response = client.post(
            "/api/v1/search",
            json={"query": "What is embodied intelligence?", "top_k": 5},
        )

        assert response.status_code == 200
        data = response.json()

        # Validate response structure
        assert data["total_count"] > 0, "Query should return results"
        assert len(data["results"]) > 0, "Should have at least one result"

        # Validate latency requirement (P95 < 500ms)
        assert data["latency_ms"] < 500, f"Latency {data['latency_ms']}ms exceeds 500ms threshold"

        # Validate relevance - at least one result should be highly relevant
        top_result = data["results"][0]
        assert top_result["score"] > 0.5, "Top result should have relevance score > 0.5"

        # Validate content contains relevant terms
        content_lower = top_result["content"].lower()
        relevant_terms = ["embodied", "intelligence", "physical", "robot", "interaction"]
        matches = sum(1 for term in relevant_terms if term in content_lower)
        assert matches >= 2, f"Content should contain at least 2 relevant terms, found {matches}"

    @pytest.mark.integration
    @pytest.mark.requires_data
    def test_ros2_architecture_query(self, client):
        """Test query about ROS 2 returns ROS 2 chapter content.

        Expected: Results should contain content about ROS 2 architecture,
        nodes, topics, services, or other ROS 2 core concepts.
        """
        response = client.post(
            "/api/v1/search",
            json={"query": "ROS 2 architecture", "top_k": 5},
        )

        assert response.status_code == 200
        data = response.json()

        # Validate response structure
        assert data["total_count"] > 0, "Query should return results"

        # Validate latency requirement
        assert data["latency_ms"] < 500, f"Latency {data['latency_ms']}ms exceeds 500ms threshold"

        # Validate relevance
        top_result = data["results"][0]
        assert top_result["score"] > 0.5, "Top result should have relevance score > 0.5"

        # Validate content mentions ROS 2
        content_lower = top_result["content"].lower()
        assert "ros" in content_lower or "robot operating system" in content_lower, \
            "Content should mention ROS or Robot Operating System"

    @pytest.mark.integration
    @pytest.mark.requires_data
    def test_sensor_fusion_query(self, client):
        """Test query about sensor fusion returns perception content.

        Expected: Results should contain content about sensor fusion,
        perception systems, multi-sensor integration, or related topics.
        """
        response = client.post(
            "/api/v1/search",
            json={"query": "sensor fusion", "top_k": 5},
        )

        assert response.status_code == 200
        data = response.json()

        # Validate response structure
        assert data["total_count"] > 0, "Query should return results"

        # Validate latency requirement
        assert data["latency_ms"] < 500, f"Latency {data['latency_ms']}ms exceeds 500ms threshold"

        # Validate relevance
        top_result = data["results"][0]
        assert top_result["score"] > 0.4, "Top result should have relevance score > 0.4"

        # Validate content contains sensor-related terms
        content_lower = top_result["content"].lower()
        relevant_terms = ["sensor", "fusion", "perception", "data", "integration"]
        matches = sum(1 for term in relevant_terms if term in content_lower)
        assert matches >= 2, f"Content should contain at least 2 sensor-related terms, found {matches}"

    @pytest.mark.integration
    @pytest.mark.requires_data
    def test_robot_control_systems_query(self, client):
        """Test query about robot control systems returns control content.

        Expected: Results should contain content about control systems,
        control algorithms, feedback loops, or control theory.
        """
        response = client.post(
            "/api/v1/search",
            json={"query": "robot control systems", "top_k": 5},
        )

        assert response.status_code == 200
        data = response.json()

        # Validate response structure
        assert data["total_count"] > 0, "Query should return results"

        # Validate latency requirement
        assert data["latency_ms"] < 500, f"Latency {data['latency_ms']}ms exceeds 500ms threshold"

        # Validate relevance
        top_result = data["results"][0]
        assert top_result["score"] > 0.4, "Top result should have relevance score > 0.4"

        # Validate content contains control-related terms
        content_lower = top_result["content"].lower()
        relevant_terms = ["control", "robot", "system", "algorithm", "feedback"]
        matches = sum(1 for term in relevant_terms if term in content_lower)
        assert matches >= 2, f"Content should contain at least 2 control-related terms, found {matches}"

    @pytest.mark.integration
    @pytest.mark.requires_data
    def test_humanoid_locomotion_query(self, client):
        """Test query about humanoid locomotion returns movement content.

        Expected: Results should contain content about humanoid locomotion,
        walking, balance, gait, or bipedal movement.
        """
        response = client.post(
            "/api/v1/search",
            json={"query": "humanoid locomotion", "top_k": 5},
        )

        assert response.status_code == 200
        data = response.json()

        # Validate response structure
        assert data["total_count"] > 0, "Query should return results"

        # Validate latency requirement
        assert data["latency_ms"] < 500, f"Latency {data['latency_ms']}ms exceeds 500ms threshold"

        # Validate relevance
        top_result = data["results"][0]
        assert top_result["score"] > 0.4, "Top result should have relevance score > 0.4"

        # Validate content contains locomotion-related terms
        content_lower = top_result["content"].lower()
        relevant_terms = ["locomotion", "humanoid", "walking", "movement", "balance", "gait"]
        matches = sum(1 for term in relevant_terms if term in content_lower)
        assert matches >= 2, f"Content should contain at least 2 locomotion-related terms, found {matches}"

    @pytest.mark.integration
    @pytest.mark.requires_data
    def test_all_queries_meet_latency_requirement(self, client):
        """Test that all standard queries meet the <500ms latency requirement.

        This test runs multiple queries and validates that 95% meet the
        latency requirement (P95 < 500ms).
        """
        queries = [
            "What is embodied intelligence?",
            "ROS 2 architecture",
            "sensor fusion",
            "robot control systems",
            "humanoid locomotion",
            "computer vision",
            "path planning",
            "inverse kinematics",
        ]

        latencies = []
        for query in queries:
            response = client.post(
                "/api/v1/search",
                json={"query": query, "top_k": 5},
            )
            assert response.status_code == 200
            data = response.json()
            latencies.append(data["latency_ms"])

        # Calculate P95 latency
        latencies.sort()
        p95_index = int(len(latencies) * 0.95)
        p95_latency = latencies[p95_index]

        assert p95_latency < 500, \
            f"P95 latency {p95_latency:.2f}ms exceeds 500ms threshold. All latencies: {latencies}"

        # Also validate that mean latency is reasonable
        mean_latency = sum(latencies) / len(latencies)
        assert mean_latency < 300, \
            f"Mean latency {mean_latency:.2f}ms is high (expected < 300ms)"
