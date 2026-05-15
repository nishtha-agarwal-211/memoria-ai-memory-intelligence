"""
Explanation Engine for the AI Memory Intelligence System.

Generates human-readable explanations for why each memory was
retrieved and how it scored. This is key for the "explainability"
requirement — users should understand the AI's memory decisions.
"""
from app.models.memory import MemoryExplanation, ScoreBreakdown
import logging

logger = logging.getLogger(__name__)


def generate_explanation(
    ranking: dict,
    rank_position: int,
    memory_text: str,
    memory_type: str,
) -> MemoryExplanation:
    """
    Generate a structured explanation for why a memory was retrieved.
    
    Args:
        ranking: Score breakdown dict from ranking_engine
        rank_position: 1-indexed position in results
        memory_text: The memory's text content
        memory_type: The memory's category
    
    Returns:
        MemoryExplanation with human-readable reasons and score breakdown
    """
    reasons = []

    # ── Analyze each score component and generate reasons ──

    semantic = ranking.get("semantic_similarity", 0)
    if semantic >= 0.85:
        reasons.append(f"Very high semantic similarity ({_pct(semantic)})")
    elif semantic >= 0.7:
        reasons.append(f"High semantic similarity ({_pct(semantic)})")
    elif semantic >= 0.5:
        reasons.append(f"Moderate semantic match ({_pct(semantic)})")

    recency = ranking.get("recency_score", 0)
    if recency >= 0.9:
        reasons.append("Very recently created")
    elif recency >= 0.7:
        reasons.append("Recently mentioned")
    elif recency >= 0.4:
        reasons.append("Created within the last day")

    importance = ranking.get("importance_score", 0)
    if importance >= 0.8:
        reasons.append("Marked as highly important")
    elif importance >= 0.6:
        reasons.append("Above-average importance")

    feedback = ranking.get("feedback_score", 0)
    if feedback >= 0.7:
        reasons.append("Positively rated by user feedback")
    elif feedback < 0.3:
        reasons.append("Low feedback score (may be less reliable)")

    contextual = ranking.get("contextual_match", 0)
    if contextual >= 0.5:
        reasons.append("Strong keyword overlap with query")
    elif contextual >= 0.2:
        reasons.append("Some keyword overlap")

    # Add memory type context
    type_labels = {
        "preference": "User preference memory",
        "long_term": "Long-term knowledge",
        "session": "Current session context",
        "episodic": "Event-based memory",
        "semantic": "General knowledge",
    }
    type_label = type_labels.get(memory_type, memory_type)
    reasons.append(f"Category: {type_label}")

    # Fallback if no strong reasons found
    if len(reasons) <= 1:
        reasons.insert(0, "Best available match for the query")

    # Build score breakdown
    score_breakdown = ScoreBreakdown(
        semantic_similarity=ranking.get("semantic_similarity", 0),
        recency_score=ranking.get("recency_score", 0),
        importance_score=ranking.get("importance_score", 0),
        feedback_score=ranking.get("feedback_score", 0),
        contextual_match=ranking.get("contextual_match", 0),
        final_score=ranking.get("final_score", 0),
    )

    return MemoryExplanation(
        reasons=reasons,
        score_breakdown=score_breakdown,
        rank=rank_position,
    )


def _pct(value: float) -> str:
    """Convert a 0-1 float to a percentage string."""
    return f"{int(value * 100)}%"
