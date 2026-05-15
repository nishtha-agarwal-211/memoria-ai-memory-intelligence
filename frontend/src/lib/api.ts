/**
 * API Client for the AI Memory Intelligence System.
 * 
 * Handles all communication with the FastAPI backend including:
 * - REST API calls for memory operations
 * - SSE streaming for chat responses
 * - Error handling and type-safe responses
 */
import type {
  ChatResponse,
  MemoryCreate,
  MemorySearchResult,
  Memory,
  SystemMetrics,
  StreamEvent,
  MemoryFeedback,
} from './types';

const API_BASE = 'http://localhost:8000';

/**
 * Generic fetch wrapper with error handling.
 */
async function apiFetch<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`API Error (${response.status}): ${error}`);
  }

  return response.json();
}

// ══════════════════════════════════════════════
// Chat Endpoints
// ══════════════════════════════════════════════

/**
 * Send a chat message and get a full response (non-streaming).
 */
export async function sendChatMessage(message: string): Promise<ChatResponse> {
  return apiFetch<ChatResponse>('/chat', {
    method: 'POST',
    body: JSON.stringify({ message }),
  });
}

/**
 * Send a chat message with streaming response via SSE.
 * Calls onEvent for each received event (metadata, token, done).
 */
export async function streamChatMessage(
  message: string,
  onEvent: (event: StreamEvent) => void,
  onError?: (error: Error) => void
): Promise<void> {
  try {
    const response = await fetch(`${API_BASE}/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message }),
    });

    if (!response.ok) {
      throw new Error(`Stream error: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) throw new Error('No readable stream');

    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6));
            onEvent(data as StreamEvent);
          } catch {
            // Skip malformed JSON
          }
        }
      }
    }
  } catch (error) {
    if (onError) {
      onError(error instanceof Error ? error : new Error(String(error)));
    }
  }
}

// ══════════════════════════════════════════════
// Memory Endpoints
// ══════════════════════════════════════════════

/**
 * Store a new memory in the vector database.
 */
export async function storeMemory(memory: MemoryCreate): Promise<{
  status: string;
  memory: Memory;
  conflicts_resolved: unknown[];
  storage_latency_ms: number;
}> {
  return apiFetch('/memory/store', {
    method: 'POST',
    body: JSON.stringify(memory),
  });
}

/**
 * Search for memories by query string.
 */
export async function searchMemories(
  query: string,
  limit: number = 8,
  memoryType?: string
): Promise<{
  query: string;
  results: MemorySearchResult[];
  total_searched: number;
  retrieval_latency_ms: number;
}> {
  const params = new URLSearchParams({ query, limit: String(limit) });
  if (memoryType) params.set('memory_type', memoryType);
  return apiFetch(`/memory/search?${params}`);
}

/**
 * Get all stored memories.
 */
export async function getAllMemories(): Promise<{
  memories: Memory[];
  total: number;
}> {
  return apiFetch('/memory/all');
}

/**
 * Submit feedback on a memory (👍 or 👎).
 */
export async function submitFeedback(feedback: MemoryFeedback): Promise<{
  memory_id: string;
  new_feedback_score: number;
  feedback_count: number;
  message: string;
}> {
  return apiFetch('/memory/feedback', {
    method: 'POST',
    body: JSON.stringify(feedback),
  });
}

// ══════════════════════════════════════════════
// Metrics Endpoint
// ══════════════════════════════════════════════

/**
 * Get system metrics for the dashboard.
 */
export async function getMetrics(): Promise<SystemMetrics> {
  return apiFetch('/metrics');
}
