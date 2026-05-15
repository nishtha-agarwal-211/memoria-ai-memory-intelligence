/**
 * TypeScript type definitions for the AI Memory Intelligence System.
 * Mirrors the backend Pydantic models for full type safety.
 */

// ── Memory Types ──

export type MemoryType = 'preference' | 'long_term' | 'session' | 'episodic' | 'semantic';

export interface Memory {
  id: string;
  text: string;
  memory_type: MemoryType;
  importance: number;
  confidence: number;
  feedback_score: number;
  feedback_count: number;
  created_at: string;
  updated_at: string;
  superseded_by: string | null;
  tags: string[];
}

export interface MemoryCreate {
  text: string;
  memory_type: MemoryType;
  importance: number;
}

// ── Scoring & Explanation ──

export interface ScoreBreakdown {
  semantic_similarity: number;
  recency_score: number;
  importance_score: number;
  feedback_score: number;
  contextual_match: number;
  final_score: number;
}

export interface MemoryExplanation {
  reasons: string[];
  score_breakdown: ScoreBreakdown;
  rank: number;
}

export interface MemorySearchResult {
  memory: Memory;
  explanation: MemoryExplanation;
}

// ── Chat ──

export interface ChatRequest {
  message: string;
  conversation_id?: string;
}

export interface RetrievalMetrics {
  total_memories_searched: number;
  memories_retrieved: number;
  retrieval_latency_ms: number;
  llm_latency_ms: number;
  total_latency_ms: number;
  tokens_used: number;
  context_tokens: number;
  compression_ratio: number;
}

export interface ChatResponse {
  response: string;
  retrieved_memories: MemorySearchResult[];
  metrics: RetrievalMetrics;
  conversation_id?: string;
}

// ── Streaming Events ──

export interface StreamMetadataEvent {
  type: 'metadata';
  retrieved_memories: MemorySearchResult[];
  retrieval_latency_ms: number;
  total_searched: number;
  context_tokens: number;
}

export interface StreamTokenEvent {
  type: 'token';
  content: string;
}

export interface StreamDoneEvent {
  type: 'done';
  total_latency_ms: number;
  tokens_used: number;
}

export type StreamEvent = StreamMetadataEvent | StreamTokenEvent | StreamDoneEvent;

// ── Metrics ──

export interface SystemMetrics {
  total_memories: number;
  memories_by_type: Record<string, number>;
  avg_retrieval_latency_ms: number;
  avg_llm_latency_ms: number;
  total_queries: number;
  total_feedback: number;
  positive_feedback_ratio: number;
  avg_memories_per_query: number;
  recent_latencies: number[];
}

// ── Feedback ──

export interface MemoryFeedback {
  memory_id: string;
  is_useful: boolean;
  query_context?: string;
}

// ── UI State ──

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  retrieved_memories?: MemorySearchResult[];
  metrics?: RetrievalMetrics;
  isStreaming?: boolean;
}

// ── Memory Type Metadata ──

export const MEMORY_TYPE_CONFIG: Record<MemoryType, {
  label: string;
  color: string;
  bgColor: string;
  icon: string;
}> = {
  preference: {
    label: 'Preference',
    color: '#a78bfa',
    bgColor: 'rgba(167, 139, 250, 0.15)',
    icon: '💜',
  },
  long_term: {
    label: 'Long Term',
    color: '#22d3ee',
    bgColor: 'rgba(34, 211, 238, 0.15)',
    icon: '🧠',
  },
  session: {
    label: 'Session',
    color: '#34d399',
    bgColor: 'rgba(52, 211, 153, 0.15)',
    icon: '⚡',
  },
  episodic: {
    label: 'Episodic',
    color: '#fbbf24',
    bgColor: 'rgba(251, 191, 36, 0.15)',
    icon: '📅',
  },
  semantic: {
    label: 'Semantic',
    color: '#60a5fa',
    bgColor: 'rgba(96, 165, 250, 0.15)',
    icon: '📚',
  },
};
