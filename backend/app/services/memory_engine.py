"""
Memory Engine for the AI Memory Intelligence System.

Central orchestrator that coordinates all memory operations:
- Store new memories (embed → store → conflict check)
- Search memories (embed query → vector search → rank → explain)
- Retrieve all memories
- Process feedback

This is the brain of the system — it ties together the vector DB,
embedding service, ranking engine, and explanation engine.
"""
from datetime import datetime
from app.database.qdrant_client import qdrant_manager
from app.services.embedding_service import embedding_service
from app.services.ranking_engine import rank_memories
from app.services.conflict_resolver import detect_and_resolve_conflicts
from app.services.explanation_engine import generate_explanation
from app.models.memory import (
    Memory,
    MemoryCreate,
    MemorySearchResult,
    MemoryType,
)
import logging
import time

logger = logging.getLogger(__name__)


class MemoryEngine:
    """Core memory orchestration engine."""

    def store_memory(self, memory_input: MemoryCreate) -> dict:
        """
        Store a new memory in the vector database.
        
        Pipeline:
        1. Generate embedding from text
        2. Create Memory object with metadata
        3. Store in Qdrant
        4. Check for conflicting memories
        5. Return stored memory + any conflict resolutions
        """
        start = time.time()

        # Step 1: Generate embedding
        embedding = embedding_service.encode_document(memory_input.text)

        # Step 2: Create memory object
        memory = Memory(
            text=memory_input.text,
            memory_type=memory_input.memory_type,
            importance=memory_input.importance,
        )

        # Step 3: Store in Qdrant
        qdrant_manager.upsert_memory(memory, embedding)

        # Step 4: Check for conflicts
        conflicts = detect_and_resolve_conflicts(
            new_memory_id=memory.id,
            new_text=memory.text,
            new_embedding=embedding,
            new_memory_type=memory.memory_type.value,
        )

        elapsed_ms = (time.time() - start) * 1000
        logger.info(f"Stored memory in {elapsed_ms:.1f}ms (conflicts: {len(conflicts)})")

        return {
            "memory": memory.model_dump(),
            "conflicts_resolved": conflicts,
            "storage_latency_ms": round(elapsed_ms, 1),
        }

    def search_memories(
        self,
        query: str,
        limit: int = 8,
        memory_type: str | None = None,
    ) -> dict:
        """
        Search for relevant memories using hybrid retrieval.
        
        Pipeline:
        1. Embed the query
        2. Vector search in Qdrant
        3. Rank results with multi-factor scoring
        4. Generate explanations for each result
        5. Return ranked results with explanations
        """
        start = time.time()

        # Step 1: Embed query
        query_vector = embedding_service.encode_query(query)

        # Step 2: Vector search
        search_results = qdrant_manager.search_similar(
            query_vector=query_vector,
            limit=limit * 2,  # Fetch more, rank will filter
            memory_type=memory_type,
            score_threshold=0.2,  # Minimum relevance threshold
        )

        # Step 3: Rank results
        ranked = rank_memories(search_results, query)

        # Step 4: Generate explanations and build response
        results: list[MemorySearchResult] = []
        for i, item in enumerate(ranked[:limit]):
            payload = item["payload"]

            memory = Memory(
                id=item["id"],
                text=payload["text"],
                memory_type=MemoryType(payload["memory_type"]),
                importance=payload.get("importance", 0.5),
                confidence=payload.get("confidence", 1.0),
                feedback_score=payload.get("feedback_score", 0.0),
                feedback_count=payload.get("feedback_count", 0),
                created_at=payload.get("created_at", ""),
                updated_at=payload.get("updated_at", ""),
                superseded_by=payload.get("superseded_by"),
                tags=payload.get("tags", []),
            )

            explanation = generate_explanation(
                ranking=item["ranking"],
                rank_position=i + 1,
                memory_text=payload["text"],
                memory_type=payload["memory_type"],
            )

            results.append(MemorySearchResult(
                memory=memory,
                explanation=explanation,
            ))

        elapsed_ms = (time.time() - start) * 1000

        return {
            "results": results,
            "total_searched": len(search_results),
            "retrieval_latency_ms": round(elapsed_ms, 1),
        }

    def get_all_memories(self, limit: int = 100) -> list[dict]:
        """Retrieve all stored memories."""
        raw = qdrant_manager.get_all_memories(limit=limit)
        memories = []
        for item in raw:
            payload = item["payload"]
            memories.append({
                "id": item["id"],
                "text": payload.get("text", ""),
                "memory_type": payload.get("memory_type", "general"),
                "importance": payload.get("importance", 0.5),
                "confidence": payload.get("confidence", 1.0),
                "feedback_score": payload.get("feedback_score", 0.0),
                "feedback_count": payload.get("feedback_count", 0),
                "created_at": payload.get("created_at", ""),
                "updated_at": payload.get("updated_at", ""),
                "superseded_by": payload.get("superseded_by"),
                "tags": payload.get("tags", []),
            })
        return memories

    def process_feedback(self, memory_id: str, is_useful: bool) -> dict:
        """
        Process user feedback (👍/👎) on a retrieved memory.
        Updates the memory's feedback score which influences future rankings.
        
        Feedback scoring:
        - 👍: +0.2 toward 1.0
        - 👎: -0.2 toward -1.0
        - Score clamped to [-1, 1]
        """
        # Get current state
        all_mems = qdrant_manager.get_all_memories(limit=1000)
        target = None
        for mem in all_mems:
            if mem["id"] == memory_id:
                target = mem
                break

        if not target:
            return {"error": f"Memory {memory_id} not found"}

        payload = target["payload"]
        current_score = payload.get("feedback_score", 0.0)
        current_count = payload.get("feedback_count", 0)

        # Update score
        delta = 0.2 if is_useful else -0.2
        new_score = max(-1.0, min(1.0, current_score + delta))
        new_count = current_count + 1

        # Persist update
        qdrant_manager.update_payload(
            memory_id=memory_id,
            payload_updates={
                "feedback_score": round(new_score, 3),
                "feedback_count": new_count,
                "updated_at": datetime.utcnow().isoformat(),
            },
        )

        return {
            "memory_id": memory_id,
            "new_feedback_score": round(new_score, 3),
            "feedback_count": new_count,
            "message": f"Feedback recorded: {'👍 useful' if is_useful else '👎 not useful'}",
        }

    def get_metrics(self) -> dict:
        """Get aggregate metrics for the dashboard."""
        all_mems = self.get_all_memories(limit=1000)

        # Count by type
        type_counts: dict[str, int] = {}
        total_feedback = 0
        positive_feedback = 0

        for mem in all_mems:
            mt = mem.get("memory_type", "unknown")
            type_counts[mt] = type_counts.get(mt, 0) + 1
            fc = mem.get("feedback_count", 0)
            total_feedback += fc
            if mem.get("feedback_score", 0) > 0:
                positive_feedback += fc

        return {
            "total_memories": len(all_mems),
            "memories_by_type": type_counts,
            "total_feedback": total_feedback,
            "positive_feedback_ratio": round(
                positive_feedback / max(total_feedback, 1), 2
            ),
        }


# Singleton instance
memory_engine = MemoryEngine()
