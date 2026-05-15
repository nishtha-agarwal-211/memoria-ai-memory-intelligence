"""
Ranking Engine for the AI Memory Intelligence System.

Implements intelligent multi-factor scoring for memory retrieval:
  final_score = 0.45 * semantic_similarity
              + 0.20 * recency
              + 0.15 * importance
              + 0.10 * feedback_score
              + 0.10 * contextual_match

Each factor is normalized to [0, 1] before weighting.
"""
from datetime import datetime
import math
import re
import logging

logger = logging.getLogger(__name__)

# ── Scoring Weights ──
WEIGHT_SEMANTIC = 0.45
WEIGHT_RECENCY = 0.20
WEIGHT_IMPORTANCE = 0.15
WEIGHT_FEEDBACK = 0.10
WEIGHT_CONTEXTUAL = 0.10

# Recency decay: memories lose ~50% score after this many hours
RECENCY_HALF_LIFE_HOURS = 24.0


def compute_recency_score(created_at: str) -> float:
    """
    Exponential decay based on time since memory creation.
    Returns 1.0 for brand-new memories, approaching 0 for old ones.
    Uses a 24-hour half-life.
    """
    try:
        created = datetime.fromisoformat(created_at)
        now = datetime.utcnow()
        hours_elapsed = (now - created).total_seconds() / 3600.0
        # Exponential decay: score = 2^(-t/half_life)
        score = math.pow(2, -hours_elapsed / RECENCY_HALF_LIFE_HOURS)
        return max(0.0, min(1.0, score))
    except (ValueError, TypeError):
        return 0.5  # Default if timestamp parsing fails


def compute_contextual_match(query: str, memory_text: str) -> float:
    """
    Keyword overlap between query and memory text.
    Simple but effective for hackathon demo — counts shared meaningful words.
    """
    # Tokenize: lowercase, split on non-word chars, filter short words
    def tokenize(text: str) -> set[str]:
        words = re.findall(r'\b\w+\b', text.lower())
        return {w for w in words if len(w) > 2}  # Skip tiny words

    query_tokens = tokenize(query)
    memory_tokens = tokenize(memory_text)

    if not query_tokens:
        return 0.0

    # Jaccard-like overlap normalized by query length
    overlap = query_tokens & memory_tokens
    score = len(overlap) / len(query_tokens)
    return max(0.0, min(1.0, score))


def normalize_feedback_score(feedback_score: float, feedback_count: int) -> float:
    """
    Normalize raw feedback score to [0, 1].
    feedback_score ranges from -1 to 1, we map it to 0-1.
    With Bayesian smoothing: new memories with no feedback get 0.5.
    """
    if feedback_count == 0:
        return 0.5  # Neutral prior for new memories

    # Map [-1, 1] → [0, 1]
    normalized = (feedback_score + 1.0) / 2.0

    # Bayesian smoothing: pull toward 0.5 when few votes exist
    # weight = count / (count + prior_strength)
    prior_strength = 3.0  # Need ~3 votes to deviate significantly from prior
    weight = feedback_count / (feedback_count + prior_strength)
    smoothed = weight * normalized + (1.0 - weight) * 0.5

    return max(0.0, min(1.0, smoothed))


def rank_memory(
    semantic_similarity: float,
    created_at: str,
    importance: float,
    feedback_score: float,
    feedback_count: int,
    query: str,
    memory_text: str,
) -> dict:
    """
    Compute the final ranking score for a memory.
    
    Returns a dict with individual scores and the weighted final score.
    """
    recency = compute_recency_score(created_at)
    feedback = normalize_feedback_score(feedback_score, feedback_count)
    contextual = compute_contextual_match(query, memory_text)

    # Clamp all inputs
    semantic = max(0.0, min(1.0, semantic_similarity))
    imp = max(0.0, min(1.0, importance))

    # ── Weighted combination ──
    final_score = (
        WEIGHT_SEMANTIC * semantic
        + WEIGHT_RECENCY * recency
        + WEIGHT_IMPORTANCE * imp
        + WEIGHT_FEEDBACK * feedback
        + WEIGHT_CONTEXTUAL * contextual
    )

    return {
        "semantic_similarity": round(semantic, 4),
        "recency_score": round(recency, 4),
        "importance_score": round(imp, 4),
        "feedback_score": round(feedback, 4),
        "contextual_match": round(contextual, 4),
        "final_score": round(final_score, 4),
    }


def rank_memories(
    search_results: list[dict],
    query: str,
) -> list[dict]:
    """
    Rank a list of search results by the multi-factor scoring formula.
    
    Args:
        search_results: List of {id, score, payload} from Qdrant search
        query: The user's search query
    
    Returns:
        Sorted list with ranking scores attached
    """
    ranked = []

    for result in search_results:
        payload = result["payload"]
        scores = rank_memory(
            semantic_similarity=result["score"],
            created_at=payload.get("created_at", ""),
            importance=payload.get("importance", 0.5),
            feedback_score=payload.get("feedback_score", 0.0),
            feedback_count=payload.get("feedback_count", 0),
            query=query,
            memory_text=payload.get("text", ""),
        )
        ranked.append({
            **result,
            "ranking": scores,
        })

    # Sort by final score (descending)
    ranked.sort(key=lambda x: x["ranking"]["final_score"], reverse=True)
    return ranked
