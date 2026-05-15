"""
Chat API routes for the AI Memory Intelligence System.

POST /chat — The main interaction endpoint:
1. Receives user message
2. Searches for relevant memories
3. Ranks and compresses context
4. Sends to LLM with memory-augmented prompt
5. Returns response + retrieved memories + metrics

Supports both streaming (SSE) and non-streaming responses.
"""
import json
import time
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from app.models.chat import ChatRequest, ChatResponse, RetrievalMetrics
from app.services.memory_engine import memory_engine
from app.services.context_compressor import compress_context
from app.services.llm_service import llm_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Track latencies for the metrics dashboard
_recent_latencies: list[float] = []
_query_count: int = 0


@router.post("/chat")
async def chat(request: ChatRequest):
    """
    Main chat endpoint with memory-augmented AI responses.
    
    Flow:
    1. Search memories for relevant context
    2. Rank and compress memories
    3. Generate LLM response with injected memory context
    4. Return full response with memory explanations and metrics
    """
    global _query_count
    _query_count += 1
    total_start = time.time()

    # ── Step 1: Retrieve relevant memories ──
    retrieval_start = time.time()
    search_result = memory_engine.search_memories(
        query=request.message,
        limit=6,  # Top 6 most relevant memories
    )
    retrieval_latency = (time.time() - retrieval_start) * 1000

    # ── Step 2: Compress context for LLM ──
    ranked_memories = []
    for sr in search_result["results"]:
        ranked_memories.append({
            "id": sr.memory.id,
            "score": sr.explanation.score_breakdown.final_score,
            "payload": {
                "text": sr.memory.text,
                "memory_type": sr.memory.memory_type.value,
                "importance": sr.memory.importance,
                "confidence": sr.memory.confidence,
            },
            "ranking": sr.explanation.score_breakdown.model_dump(),
        })

    compression_result = compress_context(ranked_memories)
    memory_context = compression_result["compressed_context"]

    # ── Step 3: Generate LLM response ──
    llm_result = await llm_service.generate_response(
        user_message=request.message,
        memory_context=memory_context,
    )

    total_latency = (time.time() - total_start) * 1000

    # Track latencies
    _recent_latencies.append(total_latency)
    if len(_recent_latencies) > 20:
        _recent_latencies.pop(0)

    # ── Build response ──
    metrics = RetrievalMetrics(
        total_memories_searched=search_result["total_searched"],
        memories_retrieved=len(search_result["results"]),
        retrieval_latency_ms=round(retrieval_latency, 1),
        llm_latency_ms=round(llm_result["latency_ms"], 1),
        total_latency_ms=round(total_latency, 1),
        tokens_used=llm_result["tokens_used"],
        context_tokens=compression_result["token_estimate"],
        compression_ratio=compression_result["compression_ratio"],
    )

    return ChatResponse(
        response=llm_result["response"],
        retrieved_memories=search_result["results"],
        metrics=metrics,
        conversation_id=request.conversation_id,
    )


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Streaming chat endpoint using Server-Sent Events (SSE).
    
    First sends the retrieved memories and metrics as a metadata event,
    then streams the LLM response token by token.
    """
    global _query_count
    _query_count += 1
    total_start = time.time()

    # Retrieve and rank memories
    search_result = memory_engine.search_memories(
        query=request.message,
        limit=6,
    )

    ranked_memories = []
    for sr in search_result["results"]:
        ranked_memories.append({
            "id": sr.memory.id,
            "score": sr.explanation.score_breakdown.final_score,
            "payload": {
                "text": sr.memory.text,
                "memory_type": sr.memory.memory_type.value,
                "importance": sr.memory.importance,
                "confidence": sr.memory.confidence,
            },
            "ranking": sr.explanation.score_breakdown.model_dump(),
        })

    compression_result = compress_context(ranked_memories)
    memory_context = compression_result["compressed_context"]

    retrieval_latency = (time.time() - total_start) * 1000

    async def event_generator():
        # First event: send metadata (memories, metrics)
        metadata = {
            "type": "metadata",
            "retrieved_memories": [sr.model_dump() for sr in search_result["results"]],
            "retrieval_latency_ms": round(retrieval_latency, 1),
            "total_searched": search_result["total_searched"],
            "context_tokens": compression_result["token_estimate"],
        }
        yield f"data: {json.dumps(metadata)}\n\n"

        # Stream LLM response
        token_count = 0
        async for chunk in llm_service.generate_stream(
            user_message=request.message,
            memory_context=memory_context,
        ):
            token_count += 1
            yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\n\n"

        # Final event: done signal with total metrics
        total_latency = (time.time() - total_start) * 1000
        _recent_latencies.append(total_latency)
        if len(_recent_latencies) > 20:
            _recent_latencies.pop(0)

        done_data = {
            "type": "done",
            "total_latency_ms": round(total_latency, 1),
            "tokens_used": token_count,
        }
        yield f"data: {json.dumps(done_data)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


def get_query_stats() -> dict:
    """Return query statistics for the metrics endpoint."""
    return {
        "total_queries": _query_count,
        "recent_latencies": _recent_latencies[-20:],
        "avg_latency_ms": round(
            sum(_recent_latencies) / max(len(_recent_latencies), 1), 1
        ),
    }
