"""Pytest configuration and shared fixtures."""
import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def sample_html() -> str:
    """Sample HTML content for testing extraction."""
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Test Page</title></head>
    <body>
        <nav>Navigation content</nav>
        <article class="markdown">
            <h1>Introduction to Physical AI</h1>
            <p>Physical AI represents the integration of artificial intelligence
            with physical systems and robotics.</p>
            <h2>Key Concepts</h2>
            <p>This section covers the fundamental concepts.</p>
            <h3>Embodied Intelligence</h3>
            <p>Embodied intelligence is a key principle.</p>
        </article>
        <footer>Footer content</footer>
    </body>
    </html>
    """


@pytest.fixture
def sample_text() -> str:
    """Sample clean text for testing chunking."""
    return """Introduction to Physical AI

Physical AI represents the integration of artificial intelligence
with physical systems and robotics. This emerging field combines
machine learning, computer vision, and control systems to create
intelligent machines that can interact with the physical world.

Key Concepts

This section covers the fundamental concepts that underpin
physical AI systems. Understanding these concepts is essential
for anyone working in the field of robotics and automation.

Embodied Intelligence

Embodied intelligence is a key principle in physical AI.
It suggests that intelligence arises from the interaction
between an agent and its environment, not just from
computation alone."""


@pytest.fixture
def sample_chunks() -> list[dict]:
    """Sample text chunks for testing embedding."""
    return [
        {
            "content": "Physical AI represents the integration of AI with robotics.",
            "source_url": "https://example.com/intro",
            "title": "Introduction",
            "section": "Overview",
            "chunk_index": 0,
            "token_count": 12,
            "content_hash": "abc123",
        },
        {
            "content": "Embodied intelligence is a key principle in physical AI.",
            "source_url": "https://example.com/intro",
            "title": "Introduction",
            "section": "Key Concepts",
            "chunk_index": 1,
            "token_count": 11,
            "content_hash": "def456",
        },
    ]
