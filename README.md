# 🧠 Memoria — AI Memory Intelligence System

> An intelligent memory orchestration layer for AI assistants — without retraining the model.

![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=flat&logo=typescript&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=flat&logo=react&logoColor=black)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![Qdrant](https://img.shields.io/badge/Qdrant-FF6B6B?style=flat&logo=data:image/png;base64,&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)

---

## 🎯 What is this?

**Memoria** is a full-stack AI Memory Intelligence System that gives any LLM a persistent, intelligent memory. Instead of retraining models, it:

- **Stores** memories with semantic embeddings
- **Retrieves** relevant memories using hybrid search (vector + keyword + metadata)
- **Ranks** memories with a multi-factor scoring system
- **Injects** only the best memories into LLM prompts
- **Explains** exactly WHY each memory was selected

Think of it as: **"ChatGPT with a brain-like adaptive memory system."**

---

## ✨ Features

### 🔮 Memory Engine
- **5 memory types**: preference, long_term, session, episodic, semantic
- **Conflict resolution**: automatically detects contradictions and prioritizes recent truth
- **Feedback loop**: 👍/👎 voting updates future ranking scores

### 🎯 Hybrid Retrieval
- Semantic vector search via Qdrant
- Keyword overlap matching
- Metadata filtering by type

### 📊 Intelligent Ranking
```
final_score = 0.45 × semantic_similarity
            + 0.20 × recency
            + 0.15 × importance
            + 0.10 × feedback_score
            + 0.10 × contextual_match
```

### 🧪 Explainable AI
Every retrieved memory comes with:
- Similarity percentage
- Score breakdown (5 factors)
- Human-readable reasons
- Rank position

### 💎 Premium UI
- Futuristic 3-panel dark theme
- Glassmorphism and glow effects
- Smooth Framer Motion animations
- Real-time streaming responses
- Live latency sparklines

---

## 🏗️ Architecture

```
┌────────────────┐   ┌──────────────────────────────────────────┐   ┌──────────────┐
│                │   │              FastAPI Backend              │   │              │
│  React + Vite  │──▶│  Memory Engine → Ranking → Compression   │──▶│   Qdrant DB  │
│  + TailwindCSS │   │  Conflict Resolver → Explanation Engine  │   │  (Vectors)   │
│  + Framer      │◀──│  LLM Service (OpenAI-compatible + Mock)  │   │              │
│                │   │                                          │   │              │
└────────────────┘   └──────────────────────────────────────────┘   └──────────────┘
                                        │
                                        ▼
                              ┌──────────────────┐
                              │  sentence-        │
                              │  transformers     │
                              │  BAAI/bge-small   │
                              └──────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- (Optional) Docker for Qdrant server

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env to add your OpenAI API key (optional — mock mode works without it)

# Start the server
uvicorn app.main:app --reload --port 8000
```

> ⚡ First startup downloads the embedding model (~130MB) — takes ~30 seconds.
> After that, startup is fast.

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Open **http://localhost:5173** — you're ready!

---

## 🔑 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | `sk-mock-key` | OpenAI API key (mock mode if not set) |
| `OPENAI_MODEL` | `gpt-4o-mini` | LLM model name |
| `QDRANT_MODE` | `memory` | `memory` (in-process) or `server` (Docker) |
| `EMBEDDING_MODEL` | `BAAI/bge-small-en-v1.5` | Sentence transformer model |

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/chat` | Send message, get memory-augmented response |
| `POST` | `/chat/stream` | Same as above, but streaming (SSE) |
| `POST` | `/memory/store` | Store a new memory |
| `GET` | `/memory/search?query=...` | Search memories by query |
| `GET` | `/memory/all` | List all stored memories |
| `POST` | `/memory/feedback` | Submit 👍/👎 feedback |
| `GET` | `/metrics` | System metrics for dashboard |

---

## 🎨 UI Layout

```
┌─────────────────────────────────────────────────────┐
│  🧠 Memoria — AI Memory Engine          Engine Active │
├──────────┬─────────────────────┬────────────────────┤
│          │                     │                    │
│ Memory   │                     │  Intelligence      │
│ Bank     │    Neural Chat      │  Panel             │
│          │                     │                    │
│ Timeline │  Chat messages      │  Retrieved         │
│ Category │  with streaming     │  memories with     │
│ filters  │                     │  score breakdowns  │
│          │                     │                    │
│ + Add    │                     │  System metrics    │
│ Memory   │                     │  Latency chart     │
│          │  [Message input]    │                    │
└──────────┴─────────────────────┴────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React, TypeScript, Vite, TailwindCSS v4, Framer Motion, shadcn/ui, Lucide Icons |
| Backend | FastAPI, Python, Pydantic v2, SSE Streaming |
| Vector DB | Qdrant (in-memory or server mode) |
| Embeddings | sentence-transformers (BAAI/bge-small-en-v1.5, 384-dim) |
| LLM | OpenAI-compatible API (with mock fallback) |

---

## 🏆 Built for Hackathon

This project is designed to be demo-friendly:
- **Zero config**: Works out of the box with in-memory Qdrant and mock LLM
- **Pre-seeded**: Comes with 15 sample memories across all categories
- **Visual**: Every feature is visible in the UI — no hidden functionality
- **Explainable**: Shows exactly how the AI makes memory decisions

---

## 📄 License

MIT
