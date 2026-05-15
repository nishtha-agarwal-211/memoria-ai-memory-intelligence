"""
Qdrant Vector Database Client for the AI Memory Intelligence System.

Handles all vector database operations: collection management,
point insertion, similarity search, and payload updates.
Uses in-memory mode by default for zero-setup hackathon demos.
"""
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)
from app.config import settings
from app.models.memory import Memory
import logging

logger = logging.getLogger(__name__)


class QdrantManager:
    """Manages the Qdrant vector database connection and operations."""

    def __init__(self):
        self.client: QdrantClient | None = None
        self.collection_name = settings.qdrant_collection

    def initialize(self):
        """Initialize the Qdrant client and create collection if needed."""
        if settings.qdrant_mode == "memory":
            # In-memory mode: no Docker needed, perfect for hackathon demos
            self.client = QdrantClient(":memory:")
            logger.info("Qdrant initialized in IN-MEMORY mode")
        else:
            # Server mode: connect to a running Qdrant instance
            self.client = QdrantClient(
                host=settings.qdrant_host,
                port=settings.qdrant_port,
            )
            logger.info(f"Qdrant connected to {settings.qdrant_host}:{settings.qdrant_port}")

        # Create the memories collection
        self._create_collection()

    def _create_collection(self):
        """Create the vector collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        existing_names = [c.name for c in collections]

        if self.collection_name not in existing_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=settings.embedding_dim,  # 384 for bge-small-en-v1.5
                    distance=Distance.COSINE,
                ),
            )
            logger.info(f"Created collection '{self.collection_name}' (dim={settings.embedding_dim})")
        else:
            logger.info(f"Collection '{self.collection_name}' already exists")

    def upsert_memory(self, memory: Memory, embedding: list[float]):
        """
        Insert or update a memory point in the vector database.
        The embedding is the vector, and all memory fields go into the payload.
        """
        point = PointStruct(
            id=memory.id,  # UUID string from Memory model
            vector=embedding,
            payload={
                "text": memory.text,
                "memory_type": memory.memory_type.value,
                "importance": memory.importance,
                "confidence": memory.confidence,
                "feedback_score": memory.feedback_score,
                "feedback_count": memory.feedback_count,
                "created_at": memory.created_at,
                "updated_at": memory.updated_at,
                "superseded_by": memory.superseded_by,
                "tags": memory.tags,
            },
        )
        self.client.upsert(
            collection_name=self.collection_name,
            points=[point],
        )
        logger.info(f"Upserted memory {memory.id[:8]}...: '{memory.text[:50]}...'")

    def search_similar(
        self,
        query_vector: list[float],
        limit: int = 10,
        memory_type: str | None = None,
        score_threshold: float = 0.0,
    ) -> list[dict]:
        """
        Search for similar memories using vector similarity.
        Optionally filter by memory type.
        Returns list of {id, score, payload} dicts.
        
        Uses query_points (Qdrant v1.12+ API).
        """
        # Build optional filter
        query_filter = None
        if memory_type:
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="memory_type",
                        match=MatchValue(value=memory_type),
                    )
                ]
            )

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit,
            query_filter=query_filter,
            score_threshold=score_threshold,
        )

        return [
            {
                "id": str(hit.id),
                "score": hit.score,
                "payload": hit.payload,
            }
            for hit in results.points
        ]

    def get_all_memories(self, limit: int = 100, offset: int = 0) -> list[dict]:
        """Retrieve all memories from the collection."""
        points, _ = self.client.scroll(
            collection_name=self.collection_name,
            limit=limit,
            with_vectors=False,
        )
        return [
            {
                "id": str(point.id),
                "payload": point.payload,
            }
            for point in points
        ]

    def update_payload(self, memory_id: str, payload_updates: dict):
        """Update specific payload fields for a memory point."""
        self.client.set_payload(
            collection_name=self.collection_name,
            payload=payload_updates,
            points=[memory_id],
        )
        logger.info(f"Updated payload for memory {memory_id[:8]}...: {list(payload_updates.keys())}")

    def get_collection_info(self) -> dict:
        """Get collection statistics."""
        info = self.client.get_collection(self.collection_name)
        return {
            "total_points": info.points_count,
            "vectors_count": info.vectors_count,
            "status": info.status.value if info.status else "unknown",
        }

    def delete_memory(self, memory_id: str):
        """Delete a memory point from the collection."""
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=[memory_id],
        )
        logger.info(f"Deleted memory {memory_id[:8]}...")


# Singleton instance
qdrant_manager = QdrantManager()
