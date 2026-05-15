"""
Chat data models for the AI Memory Intelligence System.

Defines request/response schemas for the chat endpoint,
including memory retrieval metadata and performance metrics.
"""
from typing import Optional
from pydantic import BaseModel, Field
from app.models.memory import MemorySearchResult


class ChatRequest(BaseModel):
    """Incoming chat message from the user."""
    message: str = Field(..., min_length=1, max_length=4000)
    conversation_id: Optional[str] = None  # For future multi-conversation support


class RetrievalMetrics(BaseModel):
    """Performance metrics for a single chat interaction."""
    total_memories_searched: int = 0
    memories_retrieved: int = 0
    retrieval_latency_ms: float = 0.0    # Time to search + rank memories
    llm_latency_ms: float = 0.0         # Time for LLM response
    total_latency_ms: float = 0.0       # End-to-end latency
    tokens_used: int = 0                 # Approximate tokens in context
    context_tokens: int = 0              # Tokens from memory injection
    compression_ratio: float = 1.0       # Before/after compression


class ChatResponse(BaseModel):
    """Full response from the chat endpoint (non-streaming version)."""
    response: str
    retrieved_memories: list[MemorySearchResult] = []
    metrics: RetrievalMetrics = RetrievalMetrics()
    conversation_id: Optional[str] = None


class SystemMetrics(BaseModel):
    """Aggregate system metrics for the dashboard."""
    total_memories: int = 0
    memories_by_type: dict[str, int] = {}
    avg_retrieval_latency_ms: float = 0.0
    avg_llm_latency_ms: float = 0.0
    total_queries: int = 0
    total_feedback: int = 0
    positive_feedback_ratio: float = 0.0
    avg_memories_per_query: float = 0.0
    recent_latencies: list[float] = []  # Last 20 latencies for sparkline
