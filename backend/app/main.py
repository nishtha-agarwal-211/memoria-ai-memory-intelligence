"""
AI Memory Intelligence System — FastAPI Application

Main entry point for the backend. Sets up:
- CORS middleware for frontend communication
- Lifespan events (load models on startup)
- Route registration for all API endpoints
- Seed data for demo purposes
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.qdrant_client import qdrant_manager
from app.services.embedding_service import embedding_service
from app.services.llm_service import llm_service
from app.routes import chat, memory, metrics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Runs startup logic before the app serves requests,
    and cleanup logic on shutdown.
    """
    logger.info("=" * 60)
    logger.info("🧠 AI Memory Intelligence System — Starting Up")
    logger.info("=" * 60)

    # 1. Initialize Qdrant vector database
    qdrant_manager.initialize()

    # 2. Load embedding model (this takes a few seconds)
    embedding_service.load_model()

    # 3. Initialize LLM service
    llm_service.initialize()

    # 4. Seed demo data
    _seed_demo_data()

    logger.info("=" * 60)
    logger.info("✅ System ready — all services initialized")
    logger.info("=" * 60)

    yield  # App runs here

    # Shutdown
    logger.info("🛑 Shutting down AI Memory Intelligence System")


def _seed_demo_data():
    """Pre-seed the database with sample memories for demo purposes."""
    from app.services.memory_engine import memory_engine
    from app.models.memory import MemoryCreate, MemoryType

    demo_memories = [
        # Preferences
        MemoryCreate(
            text="User prefers dark mode in all applications",
            memory_type=MemoryType.PREFERENCE,
            importance=0.7,
        ),
        MemoryCreate(
            text="User likes TypeScript over plain JavaScript for type safety",
            memory_type=MemoryType.PREFERENCE,
            importance=0.8,
        ),
        MemoryCreate(
            text="User prefers functional programming patterns over OOP",
            memory_type=MemoryType.PREFERENCE,
            importance=0.6,
        ),
        MemoryCreate(
            text="User enjoys using React with hooks for frontend development",
            memory_type=MemoryType.PREFERENCE,
            importance=0.7,
        ),
        # Long-term facts
        MemoryCreate(
            text="User is a software engineer working at a tech startup",
            memory_type=MemoryType.LONG_TERM,
            importance=0.9,
        ),
        MemoryCreate(
            text="User has 3 years of experience with Python and FastAPI",
            memory_type=MemoryType.LONG_TERM,
            importance=0.8,
        ),
        MemoryCreate(
            text="User is interested in AI and machine learning applications",
            memory_type=MemoryType.LONG_TERM,
            importance=0.7,
        ),
        # Episodic
        MemoryCreate(
            text="User asked about vector databases and chose Qdrant for their project",
            memory_type=MemoryType.EPISODIC,
            importance=0.6,
        ),
        MemoryCreate(
            text="User was debugging a CORS issue in their FastAPI backend yesterday",
            memory_type=MemoryType.EPISODIC,
            importance=0.4,
        ),
        # Semantic knowledge
        MemoryCreate(
            text="RAG (Retrieval Augmented Generation) combines vector search with LLM generation",
            memory_type=MemoryType.SEMANTIC,
            importance=0.5,
        ),
        MemoryCreate(
            text="Cosine similarity measures the angle between two vectors, ranging from -1 to 1",
            memory_type=MemoryType.SEMANTIC,
            importance=0.5,
        ),
        MemoryCreate(
            text="Sentence transformers convert text into dense vector embeddings for semantic search",
            memory_type=MemoryType.SEMANTIC,
            importance=0.5,
        ),
        # Session context
        MemoryCreate(
            text="User is currently building a hackathon project about AI memory systems",
            memory_type=MemoryType.SESSION,
            importance=0.9,
        ),
        MemoryCreate(
            text="User wants to demo intelligent memory retrieval with explainability",
            memory_type=MemoryType.SESSION,
            importance=0.8,
        ),
        MemoryCreate(
            text="The current project uses React, FastAPI, Qdrant, and sentence-transformers",
            memory_type=MemoryType.SESSION,
            importance=0.7,
        ),
    ]

    logger.info(f"Seeding {len(demo_memories)} demo memories...")
    for mem in demo_memories:
        memory_engine.store_memory(mem)
    logger.info("✅ Demo memories seeded successfully")


# ── Create FastAPI application ──
app = FastAPI(
    title="AI Memory Intelligence System",
    description="An intelligent memory orchestration layer for AI assistants",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS middleware (allow frontend to connect) ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For hackathon demo — restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register routes ──
app.include_router(chat.router, tags=["Chat"])
app.include_router(memory.router)
app.include_router(metrics.router)


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "system": "AI Memory Intelligence System",
        "version": "1.0.0",
    }
