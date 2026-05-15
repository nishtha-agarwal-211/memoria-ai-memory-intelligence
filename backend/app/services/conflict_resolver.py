"""
Conflict Resolver for the AI Memory Intelligence System.

Detects when new memories contradict existing ones and handles
the conflict by reducing confidence in older memories and
establishing supersession relationships.

Example:
  Old: "User likes React" (confidence: 1.0)
  New: "User switched to Vue"
  → Old confidence reduced to 0.3, superseded_by = new_memory_id
"""
from datetime import datetime
from app.database.qdrant_client import qdrant_manager
from app.services.embedding_service import embedding_service
import logging

logger = logging.getLogger(__name__)

# Similarity threshold: above this, two memories are about the same topic
CONFLICT_SIMILARITY_THRESHOLD = 0.78

# How much to reduce old memory confidence when superseded
CONFIDENCE_DECAY_FACTOR = 0.3


def detect_and_resolve_conflicts(
    new_memory_id: str,
    new_text: str,
    new_embedding: list[float],
    new_memory_type: str,
) -> list[dict]:
    """
    Check if the new memory conflicts with existing memories.
    If conflicts are found, reduce old memory confidence and mark as superseded.
    
    Returns list of conflict resolution actions taken.
    """
    resolutions = []

    # Search for highly similar existing memories
    similar = qdrant_manager.search_similar(
        query_vector=new_embedding,
        limit=5,
        score_threshold=CONFLICT_SIMILARITY_THRESHOLD,
    )

    for result in similar:
        # Skip self-match
        if result["id"] == new_memory_id:
            continue

        old_payload = result["payload"]
        similarity = result["score"]

        # Only conflict within same memory type (preferences conflict with preferences, etc.)
        if old_payload.get("memory_type") != new_memory_type:
            continue

        # Check if the texts are different enough to be contradictory
        # (high similarity in topic but different content = conflict)
        if _texts_are_contradictory(old_payload.get("text", ""), new_text):
            # Reduce old memory confidence
            old_confidence = old_payload.get("confidence", 1.0)
            new_confidence = old_confidence * CONFIDENCE_DECAY_FACTOR

            qdrant_manager.update_payload(
                memory_id=result["id"],
                payload_updates={
                    "confidence": round(new_confidence, 3),
                    "superseded_by": new_memory_id,
                    "updated_at": datetime.utcnow().isoformat(),
                },
            )

            resolution = {
                "old_memory_id": result["id"],
                "old_text": old_payload.get("text", ""),
                "new_memory_id": new_memory_id,
                "new_text": new_text,
                "similarity": round(similarity, 3),
                "old_confidence": old_confidence,
                "new_confidence": round(new_confidence, 3),
                "action": "confidence_reduced",
            }
            resolutions.append(resolution)
            logger.info(
                f"Conflict resolved: '{old_payload.get('text', '')[:40]}...' "
                f"superseded by '{new_text[:40]}...' "
                f"(confidence {old_confidence:.2f} → {new_confidence:.2f})"
            )

    return resolutions


def _texts_are_contradictory(old_text: str, new_text: str) -> bool:
    """
    Heuristic check for contradictory content.
    Two memories are contradictory if they discuss the same topic
    but with different specifics. For a hackathon, we use simple
    text-difference heuristics rather than NLI models.
    """
    old_lower = old_text.lower().strip()
    new_lower = new_text.lower().strip()

    # Exact match = not contradictory, it's a duplicate
    if old_lower == new_lower:
        return False

    # Check for negation patterns
    negation_pairs = [
        ("likes", "dislikes"),
        ("prefers", "avoids"),
        ("uses", "stopped using"),
        ("switched to", "switched from"),
        ("enjoys", "hates"),
        ("wants", "doesn't want"),
    ]
    for pos, neg in negation_pairs:
        if (pos in old_lower and neg in new_lower) or (neg in old_lower and pos in new_lower):
            return True

    # If texts are about the same topic (high similarity was already checked)
    # but differ significantly, assume potential conflict
    # Simple heuristic: if they share many words but not all, it's a conflict
    old_words = set(old_lower.split())
    new_words = set(new_lower.split())
    overlap = len(old_words & new_words)
    total = len(old_words | new_words)

    if total > 0:
        jaccard = overlap / total
        # Medium overlap (same topic, different details) = likely conflict
        if 0.2 < jaccard < 0.8:
            return True

    return False
