"""
Memory API routes for the AI Memory Intelligence System.

Endpoints:
- POST /memory/store     — Store a new memory
- GET  /memory/search    — Search memories by query
- GET  /memory/all       — List all stored memories
- POST /memory/feedback  — Submit 👍/👎 feedback on a memory
"""
from fastapi import APIRouter, Query
from app.models.memory import (
    MemoryCreate,
    MemoryFeedbackRequest,
    MemoryFeedbackResponse,
)
from app.services.memory_engine import memory_engine
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/memory", tags=["Memory"])


@router.post("/store")
async def store_memory(memory_input: MemoryCreate):
    """
    Store a new memory in the vector database.
    
    Automatically:
    - Generates embedding vector
    - Detects and resolves conflicts with existing memories
    - Returns the stored memory with metadata
    """
    result = memory_engine.store_memory(memory_input)
    return {
        "status": "stored",
        **result,
    }


@router.get("/search")
async def search_memories(
    query: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(default=8, ge=1, le=20, description="Max results"),
    memory_type: str | None = Query(default=None, description="Filter by memory type"),
):
    """
    Search for relevant memories using hybrid retrieval.
    
    Returns ranked results with:
    - Similarity scores
    - Ranking breakdown
    - Human-readable explanations of why each memory was selected
    """
    result = memory_engine.search_memories(
        query=query,
        limit=limit,
        memory_type=memory_type,
    )

    return {
        "query": query,
        "results": [r.model_dump() for r in result["results"]],
        "total_searched": result["total_searched"],
        "retrieval_latency_ms": result["retrieval_latency_ms"],
    }


@router.get("/all")
async def get_all_memories(
    limit: int = Query(default=100, ge=1, le=500, description="Max memories to return"),
):
    """
    Retrieve all stored memories.
    
    Returns memories sorted by creation time with full metadata.
    """
    memories = memory_engine.get_all_memories(limit=limit)
    return {
        "memories": memories,
        "total": len(memories),
    }


@router.post("/feedback")
async def submit_feedback(feedback: MemoryFeedbackRequest):
    """
    Submit feedback on a retrieved memory.
    
    👍 (is_useful=true): Increases memory's future ranking score
    👎 (is_useful=false): Decreases memory's future ranking score
    
    Feedback is stored persistently and influences the ranking engine.
    """
    result = memory_engine.process_feedback(
        memory_id=feedback.memory_id,
        is_useful=feedback.is_useful,
    )

    if "error" in result:
        return {"status": "error", **result}

    return MemoryFeedbackResponse(**result)
