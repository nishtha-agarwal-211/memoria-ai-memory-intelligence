/**
 * useMemories Hook — Manages memory state and operations.
 * 
 * Handles:
 * - Fetching all memories
 * - Storing new memories
 * - Submitting feedback (👍/👎)
 * - Auto-refresh after mutations
 */
import { useState, useCallback, useEffect } from 'react';
import type { Memory, MemoryCreate } from '@/lib/types';
import { getAllMemories, storeMemory, submitFeedback } from '@/lib/api';

interface UseMemoriesReturn {
  memories: Memory[];
  isLoading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  addMemory: (memory: MemoryCreate) => Promise<void>;
  sendFeedback: (memoryId: string, isUseful: boolean) => Promise<void>;
}

export function useMemories(): UseMemoriesReturn {
  const [memories, setMemories] = useState<Memory[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await getAllMemories();
      // Sort by creation time (newest first)
      const sorted = data.memories.sort((a, b) =>
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      );
      setMemories(sorted);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch memories');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const addMemory = useCallback(async (memory: MemoryCreate) => {
    try {
      await storeMemory(memory);
      await refresh(); // Re-fetch to get updated list
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to store memory');
      throw err;
    }
  }, [refresh]);

  const sendFeedback = useCallback(async (memoryId: string, isUseful: boolean) => {
    try {
      await submitFeedback({ memory_id: memoryId, is_useful: isUseful });
      await refresh(); // Re-fetch to get updated scores
    } catch (err) {
      console.error('Feedback error:', err);
    }
  }, [refresh]);

  // Load memories on mount
  useEffect(() => {
    refresh();
  }, [refresh]);

  return {
    memories,
    isLoading,
    error,
    refresh,
    addMemory,
    sendFeedback,
  };
}
