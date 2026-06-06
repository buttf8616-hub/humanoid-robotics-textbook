"""Application settings using pydantic-settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Book configuration
    book_base_url: str = "https://buttf8616-hub.github.io/humanoid-robotics-textbook"

    # Cohere API
    cohere_api_key: str = ""

    # Qdrant Cloud
    qdrant_url: str = ""
    qdrant_api_key: str = ""
    qdrant_collection_name: str = "book-chunks"

    # Chunking configuration
    chunk_max_tokens: int = 1000
    chunk_overlap_tokens: int = 100
    chunk_min_tokens: int = 50

    # Embedding configuration
    embedding_model: str = "embed-english-v3.0"
    embedding_dimension: int = 1024
    embedding_batch_size: int = 96

    # Retrieval configuration
    retrieval_default_top_k: int = 10
    retrieval_max_top_k: int = 50

    # Gemini Agent configuration (kept for reference)
    gemini_api_key: str = ""
    gemini_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
    gemini_model: str = "gemini-2.0-flash"
    gemini_temperature: float = 0.3
    gemini_max_tokens: int = 4000

    # Anthropic (Claude) configuration
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-haiku-4-5-20251001"

    # Groq configuration - active LLM backend
    groq_api_key: str = ""
    groq_base_url: str = "https://api.groq.com/openai/v1"
    groq_model: str = "llama-3.3-70b-versatile"
    groq_temperature: float = 0.3
    groq_max_tokens: int = 2000

    agent_timeout_seconds: int = 30
    agent_max_conversation_turns: int = 10


settings = Settings()
