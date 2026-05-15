/**
 * ChatPanel Component — Main chat interface (center panel).
 * 
 * Features:
 * - Message history with auto-scroll
 * - Streaming responses with typing animation
 * - Welcome state for empty conversations
 * - Integrated with useChat hook
 */
import { useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { TypingIndicator } from './TypingIndicator';
import type { ChatMessage as ChatMessageType } from '@/lib/types';
import { Brain, Sparkles, Zap, Search } from 'lucide-react';

interface ChatPanelProps {
  messages: ChatMessageType[];
  isLoading: boolean;
  onSend: (message: string) => void;
}

export function ChatPanel({ messages, isLoading, onSend }: ChatPanelProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="panel-center flex flex-col h-full bg-[var(--color-background)]">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-3 border-b border-[var(--color-border)] glass-strong">
        <div className="flex items-center gap-3">
          <div className="relative">
            <Brain className="w-6 h-6 text-cyan-400" />
            <div className="absolute -top-0.5 -right-0.5 w-2 h-2 bg-emerald-400 rounded-full animate-pulse-glow" />
          </div>
          <div>
            <h1 className="text-sm font-semibold text-white">Neural Chat</h1>
            <p className="text-[10px] text-slate-500">Memory-augmented AI assistant</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 px-2 py-1 rounded-md bg-emerald-500/10 border border-emerald-500/20">
            <div className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-pulse-glow" />
            <span className="text-[10px] text-emerald-400 font-medium">ONLINE</span>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4 bg-grid">
        <AnimatePresence mode="popLayout">
          {messages.length === 0 ? (
            <WelcomeState key="welcome" />
          ) : (
            messages.map((msg) => (
              <ChatMessage key={msg.id} message={msg} />
            ))
          )}
        </AnimatePresence>

        {/* Typing indicator when loading and no streaming message yet */}
        {isLoading && messages.length > 0 && !messages[messages.length - 1]?.content && (
          <TypingIndicator />
        )}
      </div>

      {/* Input */}
      <ChatInput onSend={onSend} isLoading={isLoading} />
    </div>
  );
}

/** Welcome state shown when no messages exist */
function WelcomeState() {
  const features = [
    { icon: Brain, label: 'Memory-Augmented', desc: 'I remember context from past interactions' },
    { icon: Search, label: 'Semantic Search', desc: 'I find the most relevant memories for you' },
    { icon: Sparkles, label: 'Explainable AI', desc: 'I show why each memory was selected' },
    { icon: Zap, label: 'Real-time Ranking', desc: 'Memories are scored and ranked live' },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
      className="flex flex-col items-center justify-center h-full text-center px-8"
    >
      {/* Logo */}
      <motion.div
        animate={{ y: [0, -8, 0] }}
        transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
        className="mb-6"
      >
        <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-cyan-500/20 to-violet-500/20 border border-cyan-500/20 flex items-center justify-center glow-cyan">
          <Brain className="w-10 h-10 text-cyan-400" />
        </div>
      </motion.div>

      <h2 className="text-2xl font-bold text-white mb-2 glow-text-cyan">
        Memory Intelligence System
      </h2>
      <p className="text-sm text-slate-400 mb-8 max-w-md">
        An AI assistant with an adaptive memory engine. Ask me anything — I'll retrieve
        relevant memories and explain my reasoning.
      </p>

      {/* Feature cards */}
      <div className="grid grid-cols-2 gap-3 max-w-lg">
        {features.map((f, i) => (
          <motion.div
            key={f.label}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 + i * 0.1 }}
            className="glass-card p-3 text-left"
          >
            <f.icon className="w-4 h-4 text-cyan-400 mb-2" />
            <div className="text-xs font-semibold text-white">{f.label}</div>
            <div className="text-[10px] text-slate-500 mt-0.5">{f.desc}</div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
