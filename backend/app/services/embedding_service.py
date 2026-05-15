"""
Embedding Service for the AI Memory Intelligence System.

Manages the sentence-transformers model (BAAI/bge-small-en-v1.5) for
generating 384-dimensional embeddings. Handles model loading and
query/document encoding with proper instruction prefixing.
"""
from sentence_transformers import SentenceTransformer
from app.config import settings
import numpy as np
import logging

logger = logging.getLogger(__name__)

# BGE models perform better with this prefix for retrieval queries
QUERY_INSTRUCTION = "Represent this sentence for searching relevant passages: "


class EmbeddingService:
    """Manages text embedding generation using sentence-transformers."""

    def __init__(self):
        self.model: SentenceTransformer | None = None
        self.model_name = settings.embedding_model
        self.dimension = settings.embedding_dim

    def load_model(self):
        """Load the embedding model into memory. Called on app startup."""
        logger.info(f"Loading embedding model: {self.model_name}...")
        self.model = SentenceTransformer(self.model_name)
        logger.info(f"Embedding model loaded (dim={self.dimension})")

    def encode_document(self, text: str) -> list[float]:
        """
        Encode a document/memory text into an embedding vector.
        Documents are encoded WITHOUT the query instruction prefix.
        """
        if not self.model:
            raise RuntimeError("Embedding model not loaded. Call load_model() first.")

        embedding = self.model.encode(
            text,
            normalize_embeddings=True,  # Normalize for cosine similarity
        )
        return embedding.tolist()

    def encode_query(self, query: str) -> list[float]:
        """
        Encode a search query into an embedding vector.
        Queries use the BGE instruction prefix for better retrieval performance.
        """
        if not self.model:
            raise RuntimeError("Embedding model not loaded. Call load_model() first.")

        # BGE models: add instruction prefix for queries, not documents
        prefixed_query = QUERY_INSTRUCTION + query

        embedding = self.model.encode(
            prefixed_query,
            normalize_embeddings=True,
        )
        return embedding.tolist()

    def compute_similarity(self, vec_a: list[float], vec_b: list[float]) -> float:
        """Compute cosine similarity between two normalized vectors (= dot product)."""
        a = np.array(vec_a)
        b = np.array(vec_b)
        return float(np.dot(a, b))


# Singleton instance
embedding_service = EmbeddingService()
