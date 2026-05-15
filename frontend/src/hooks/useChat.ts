/**
 * useChat Hook — Manages chat state and streaming communication.
 * 
 * Handles:
 * - Message history
 * - Streaming SSE responses with typing animation
 * - Retrieved memories per message
 * - Performance metrics per interaction
 */
import { useState, useCallback, useRef } from 'react';
import type { ChatMessage, MemorySearchResult, RetrievalMetrics, StreamEvent } from '@/lib/types';
import { streamChatMessage } from '@/lib/api';

interface UseChatReturn {
  messages: ChatMessage[];
  isLoading: boolean;
  currentMemories: MemorySearchResult[];
  currentMetrics: RetrievalMetrics | null;
  sendMessage: (content: string) => Promise<void>;
  clearMessages: () => void;
}

export function useChat(): UseChatReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentMemories, setCurrentMemories] = useState<MemorySearchResult[]>([]);
  const [currentMetrics, setCurrentMetrics] = useState<RetrievalMetrics | null>(null);
  const messageIdCounter = useRef(0);

  const generateId = () => {
    messageIdCounter.current += 1;
    return `msg-${Date.now()}-${messageIdCounter.current}`;
  };

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim() || isLoading) return;

    // Add user message
    const userMessage: ChatMessage = {
      id: generateId(),
      role: 'user',
      content: content.trim(),
      timestamp: new Date().toISOString(),
    };

    // Add placeholder assistant message for streaming
    const assistantId = generateId();
    const assistantMessage: ChatMessage = {
      id: assistantId,
      role: 'assistant',
      content: '',
      timestamp: new Date().toISOString(),
      isStreaming: true,
    };

    setMessages(prev => [...prev, userMessage, assistantMessage]);
    setIsLoading(true);
    setCurrentMemories([]);
    setCurrentMetrics(null);

    let fullContent = '';
    let memories: MemorySearchResult[] = [];
    let metrics: RetrievalMetrics | null = null;

    await streamChatMessage(
      content,
      (event: StreamEvent) => {
        switch (event.type) {
          case 'metadata':
            // Memory retrieval data arrived
            memories = event.retrieved_memories || [];
            setCurrentMemories(memories);
            break;

          case 'token':
            // Streaming token arrived — append to message
            fullContent += event.content;
            setMessages(prev =>
              prev.map(msg =>
                msg.id === assistantId
                  ? { ...msg, content: fullContent }
                  : msg
              )
            );
            break;

          case 'done':
            // Stream complete — finalize message
            metrics = {
              total_memories_searched: 0,
              memories_retrieved: memories.length,
              retrieval_latency_ms: 0,
              llm_latency_ms: 0,
              total_latency_ms: event.total_latency_ms,
              tokens_used: event.tokens_used,
              context_tokens: 0,
              compression_ratio: 1,
            };
            setCurrentMetrics(metrics);
            break;
        }
      },
      (error: Error) => {
        console.error('Chat stream error:', error);
        fullContent = 'Sorry, there was an error processing your request. Please make sure the backend server is running on port 8000.';
        setMessages(prev =>
          prev.map(msg =>
            msg.id === assistantId
              ? { ...msg, content: fullContent, isStreaming: false }
              : msg
          )
        );
      }
    );

    // Finalize: mark streaming as complete, attach memories and metrics
    setMessages(prev =>
      prev.map(msg =>
        msg.id === assistantId
          ? {
              ...msg,
              content: fullContent,
              isStreaming: false,
              retrieved_memories: memories,
              metrics: metrics || undefined,
            }
          : msg
      )
    );

    setIsLoading(false);
  }, [isLoading]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setCurrentMemories([]);
    setCurrentMetrics(null);
  }, []);

  return {
    messages,
    isLoading,
    currentMemories,
    currentMetrics,
    sendMessage,
    clearMessages,
  };
}
