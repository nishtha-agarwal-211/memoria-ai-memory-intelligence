"""
Metrics API route for the AI Memory Intelligence System.

GET /metrics — Returns aggregate system metrics for the dashboard:
- Total memories and distribution by type
- Query statistics and latencies
- Feedback aggregates
"""
from fastapi import APIRouter
from app.services.memory_engine import memory_engine
from app.routes.chat import get_query_stats
from app.models.chat import SystemMetrics

router = APIRouter(tags=["Metrics"])


@router.get("/metrics")
async def get_metrics():
    """
    Get aggregate system metrics for the dashboard panels.
    
    Returns:
    - Memory statistics (total, by type)
    - Query performance (latencies, counts)
    - Feedback statistics
    """
    memory_metrics = memory_engine.get_metrics()
    query_stats = get_query_stats()

    return SystemMetrics(
        total_memories=memory_metrics["total_memories"],
        memories_by_type=memory_metrics["memories_by_type"],
        avg_retrieval_latency_ms=query_stats["avg_latency_ms"],
        total_queries=query_stats["total_queries"],
        total_feedback=memory_metrics["total_feedback"],
        positive_feedback_ratio=memory_metrics["positive_feedback_ratio"],
        avg_memories_per_query=0.0,  # TODO: track this
        recent_latencies=query_stats["recent_latencies"],
    )
