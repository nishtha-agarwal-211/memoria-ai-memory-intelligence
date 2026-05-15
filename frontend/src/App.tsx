/**
 * AI Memory Intelligence System — Main Application
 * 
 * 3-panel layout:
 * - Left: Memory Bank (timeline, categories, add form)
 * - Center: Neural Chat (AI chat with streaming)
 * - Right: Intelligence Panel (retrieved memories, metrics)
 * 
 * Orchestrates all hooks and component communication.
 */
import { TooltipProvider } from '@/components/ui/tooltip';
import { ChatPanel } from '@/components/chat/ChatPanel';
import { MemoryTimeline } from '@/components/memory/MemoryTimeline';
import { MetricsPanel } from '@/components/dashboard/MetricsPanel';
import { useChat } from '@/hooks/useChat';
import { useMemories } from '@/hooks/useMemories';
import { useMetrics } from '@/hooks/useMetrics';
import { motion } from 'framer-motion';
import { Brain, Sparkles } from 'lucide-react';

function App() {
  const chat = useChat();
  const memories = useMemories();
  const metricsHook = useMetrics();

  const handleFeedback = async (memoryId: string, isUseful: boolean) => {
    await memories.sendFeedback(memoryId, isUseful);
  };

  return (
    <TooltipProvider>
      <div className="flex flex-col h-screen overflow-hidden">
        {/* Top Bar */}
        <TopBar totalMemories={memories.memories.length} />

        {/* 3-Panel Layout */}
        <div className="flex flex-1 overflow-hidden">
          {/* Left Panel: Memory Bank */}
          <MemoryTimeline
            memories={memories.memories}
            onAddMemory={memories.addMemory}
          />

          {/* Center Panel: Chat */}
          <ChatPanel
            messages={chat.messages}
            isLoading={chat.isLoading}
            onSend={chat.sendMessage}
          />

          {/* Right Panel: Intelligence Dashboard */}
          <MetricsPanel
            metrics={metricsHook.metrics}
            currentMemories={chat.currentMemories}
            currentMetrics={chat.currentMetrics}
            onFeedback={handleFeedback}
          />
        </div>
      </div>
    </TooltipProvider>
  );
}

/** Top navigation bar */
function TopBar({ totalMemories }: { totalMemories: number }) {
  return (
    <motion.header
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex items-center justify-between px-5 py-2.5 border-b border-[var(--color-border)] glass-strong flex-shrink-0 z-10"
    >
      {/* Logo & Title */}
      <div className="flex items-center gap-3">
        <div className="relative">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-500/20 to-violet-500/20 border border-cyan-500/20 flex items-center justify-center">
            <Brain className="w-5 h-5 text-cyan-400" />
          </div>
          <motion.div
            animate={{ scale: [1, 1.4, 1], opacity: [0.5, 1, 0.5] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 bg-cyan-400 rounded-full"
          />
        </div>
        <div>
          <h1 className="text-sm font-bold text-white tracking-tight">
            <span className="glow-text-cyan">Memoria</span>
            <span className="text-slate-400 font-normal ml-1.5 text-xs">AI Memory Engine</span>
          </h1>
        </div>
      </div>

      {/* Status indicators */}
      <div className="flex items-center gap-4">
        {/* Memory count */}
        <div className="flex items-center gap-1.5">
          <Sparkles className="w-3.5 h-3.5 text-violet-400" />
          <span className="text-[10px] text-slate-400">
            <span className="text-violet-400 font-semibold">{totalMemories}</span> memories loaded
          </span>
        </div>

        {/* Engine status */}
        <div className="flex items-center gap-2 px-2.5 py-1 rounded-full bg-[var(--color-surface-3)] border border-[var(--color-border)]">
          <div className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-pulse-glow" />
          <span className="text-[10px] text-slate-400">Engine Active</span>
        </div>
      </div>
    </motion.header>
  );
}

export default App;
