"""
Configuration module for the AI Memory Intelligence System.
Loads settings from environment variables with sensible defaults.
"""
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ── OpenAI Configuration ──
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "sk-mock-key")
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # ── Qdrant Configuration ──
    qdrant_host: str = os.getenv("QDRANT_HOST", "localhost")
    qdrant_port: int = int(os.getenv("QDRANT_PORT", "6333"))
    qdrant_collection: str = os.getenv("QDRANT_COLLECTION", "memories")
    qdrant_mode: str = os.getenv("QDRANT_MODE", "memory")  # "memory" or "server"

    # ── Embedding Configuration ──
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
    embedding_dim: int = int(os.getenv("EMBEDDING_DIM", "384"))

    # ── Server Configuration ──
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))

    class Config:
        env_file = ".env"
        extra = "allow"


# Singleton settings instance
settings = Settings()
