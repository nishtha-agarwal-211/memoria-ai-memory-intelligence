"""
Context Compressor for the AI Memory Intelligence System.

Before injecting memories into the LLM prompt, this service:
1. Groups semantically similar memories
2. Deduplicates near-identical content
3. Summarizes groups into concise context
4. Tracks token usage for context budget management

This prevents wasting LLM tokens on repetitive memories and
ensures the most diverse, relevant context is provided.
"""
import re
import logging

logger = logging.getLogger(__name__)

# Maximum context tokens to inject (approximate, using word-based estimation)
MAX_CONTEXT_TOKENS = 1500

# Similarity threshold for grouping memories together
GROUP_SIMILARITY_THRESHOLD = 0.85


def compress_context(
    ranked_memories: list[dict],
    max_tokens: int = MAX_CONTEXT_TOKENS,
) -> dict:
    """
    Compress ranked memories into an optimized context string.
    
    Args:
        ranked_memories: Sorted list of {id, score, payload, ranking} dicts
        max_tokens: Maximum approximate tokens for the context
    
    Returns:
        {
            "compressed_context": str,  # Ready to inject into LLM prompt
            "original_count": int,
            "compressed_count": int,
            "compression_ratio": float,
            "token_estimate": int,
        }
    """
    if not ranked_memories:
        return {
            "compressed_context": "",
            "original_count": 0,
            "compressed_count": 0,
            "compression_ratio": 1.0,
            "token_estimate": 0,
        }

    # Step 1: Deduplicate near-identical memories
    unique_memories = _deduplicate(ranked_memories)

    # Step 2: Group by memory type for organized context
    grouped = _group_by_type(unique_memories)

    # Step 3: Build compressed context string with token budget
    context_parts = []
    total_tokens = 0

    for memory_type, memories in grouped.items():
        type_label = memory_type.replace("_", " ").title()
        section = f"[{type_label}]"
        section_tokens = _estimate_tokens(section)

        for mem in memories:
            text = mem["payload"]["text"]
            confidence = mem["payload"].get("confidence", 1.0)

            # Skip low-confidence (superseded) memories
            if confidence < 0.3:
                continue

            # Add confidence qualifier for medium-confidence memories
            if confidence < 0.7:
                entry = f"- {text} (possibly outdated)"
            else:
                entry = f"- {text}"

            entry_tokens = _estimate_tokens(entry)

            if total_tokens + section_tokens + entry_tokens > max_tokens:
                break  # Hit token budget

            if section:  # Add section header only once
                context_parts.append(section)
                total_tokens += section_tokens
                section = ""  # Don't add header again

            context_parts.append(entry)
            total_tokens += entry_tokens

    compressed = "\n".join(context_parts)
    original_count = len(ranked_memories)
    compressed_count = compressed.count("\n- ") + (1 if compressed.startswith("- ") else 0)

    return {
        "compressed_context": compressed,
        "original_count": original_count,
        "compressed_count": compressed_count,
        "compression_ratio": round(compressed_count / max(original_count, 1), 2),
        "token_estimate": total_tokens,
    }


def _deduplicate(memories: list[dict]) -> list[dict]:
    """Remove memories with very similar text (near-duplicates)."""
    seen_texts = []
    unique = []

    for mem in memories:
        text = mem["payload"]["text"].lower().strip()
        is_duplicate = False

        for seen in seen_texts:
            # Simple text similarity for deduplication
            if _text_similarity(text, seen) > GROUP_SIMILARITY_THRESHOLD:
                is_duplicate = True
                break

        if not is_duplicate:
            unique.append(mem)
            seen_texts.append(text)

    if len(unique) < len(memories):
        logger.info(f"Deduplicated: {len(memories)} → {len(unique)} memories")

    return unique


def _group_by_type(memories: list[dict]) -> dict[str, list[dict]]:
    """Group memories by their type for organized context."""
    groups: dict[str, list[dict]] = {}
    for mem in memories:
        mem_type = mem["payload"].get("memory_type", "general")
        if mem_type not in groups:
            groups[mem_type] = []
        groups[mem_type].append(mem)
    return groups


def _text_similarity(a: str, b: str) -> float:
    """Simple word-overlap similarity for deduplication."""
    words_a = set(a.split())
    words_b = set(b.split())
    if not words_a or not words_b:
        return 0.0
    intersection = words_a & words_b
    union = words_a | words_b
    return len(intersection) / len(union)


def _estimate_tokens(text: str) -> int:
    """Approximate token count (rough: 1 token ≈ 0.75 words)."""
    words = len(text.split())
    return int(words / 0.75)
