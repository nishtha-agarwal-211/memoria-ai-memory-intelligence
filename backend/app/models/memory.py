"""
Memory data models for the AI Memory Intelligence System.

Defines the core data structures for memory storage, retrieval,
ranking, and explanation — the heart of the memory engine.
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
import uuid


class MemoryType(str, Enum):
    """Categories of memories the system can store and retrieve."""
    PREFERENCE = "preference"      # User preferences (e.g., "likes dark mode")
    LONG_TERM = "long_term"        # Persistent facts (e.g., "is a software engineer")
    SESSION = "session"            # Current session context
    EPISODIC = "episodic"          # Event-based memories (e.g., "asked about X yesterday")
    SEMANTIC = "semantic"          # General knowledge and facts


class MemoryCreate(BaseModel):
    """Schema for creating a new memory."""
    text: str = Field(..., min_length=1, max_length=2000, description="The memory content")
    memory_type: MemoryType = Field(default=MemoryType.LONG_TERM, description="Category of memory")
    importance: float = Field(default=0.5, ge=0.0, le=1.0, description="Importance score 0-1")


class Memory(BaseModel):
    """Full memory object stored in the vector database."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str
    memory_type: MemoryType
    importance: float = 0.5
    confidence: float = 1.0           # Reduced when conflicting memories exist
    feedback_score: float = 0.0       # Accumulated from 👍/👎 feedback (-1 to 1)
    feedback_count: int = 0           # Total feedback interactions
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    superseded_by: Optional[str] = None  # ID of newer conflicting memory
    tags: list[str] = Field(default_factory=list)


class ScoreBreakdown(BaseModel):
    """Detailed breakdown of how a memory's ranking score was computed."""
    semantic_similarity: float = 0.0   # 0-1 cosine similarity
    recency_score: float = 0.0        # 0-1 time decay
    importance_score: float = 0.0     # 0-1 from memory metadata
    feedback_score: float = 0.0       # 0-1 normalized feedback
    contextual_match: float = 0.0     # 0-1 keyword overlap
    final_score: float = 0.0         # Weighted combination


class MemoryExplanation(BaseModel):
    """Human-readable explanation of why a memory was retrieved."""
    reasons: list[str]                # e.g., ["high semantic similarity (92%)"]
    score_breakdown: ScoreBreakdown
    rank: int                         # Position in ranked results


class MemorySearchResult(BaseModel):
    """A retrieved memory with its ranking and explanation."""
    memory: Memory
    explanation: MemoryExplanation


class MemoryFeedbackRequest(BaseModel):
    """Request to provide feedback on a retrieved memory."""
    memory_id: str
    is_useful: bool  # True = 👍, False = 👎
    query_context: Optional[str] = None  # What query it was retrieved for


class MemoryFeedbackResponse(BaseModel):
    """Response after processing memory feedback."""
    memory_id: str
    new_feedback_score: float
    feedback_count: int
    message: str
