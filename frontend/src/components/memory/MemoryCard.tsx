/**
 * MemoryCard Component — Displays a single memory with metadata.
 * 
 * Shows:
 * - Memory text
 * - Type badge with color coding
 * - Importance bar
 * - Confidence indicator
 * - Superseded status
 * - Relative timestamp
 */
import { motion } from 'framer-motion';
import { MEMORY_TYPE_CONFIG } from '@/lib/types';
import type { Memory } from '@/lib/types';
import { Clock, AlertTriangle } from 'lucide-react';

interface MemoryCardProps {
  memory: Memory;
  index: number;
  compact?: boolean;
}

export function MemoryCard({ memory, index, compact = false }: MemoryCardProps) {
  const typeConfig = MEMORY_TYPE_CONFIG[memory.memory_type];
  const isSuperseded = memory.superseded_by !== null;

  // Format relative time
  const timeAgo = getRelativeTime(memory.created_at);

  return (
    <motion.div
      initial={{ opacity: 0, x: -12 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.05, duration: 0.3 }}
      className={`
        glass-card p-3 transition-all duration-300
        ${isSuperseded ? 'opacity-50' : ''}
        ${compact ? '!rounded-lg' : ''}
      `}
    >
      {/* Header: type badge + timestamp */}
      <div className="flex items-center justify-between mb-2">
        <span
          className="text-[10px] font-semibold px-2 py-0.5 rounded-full"
          style={{
            color: typeConfig.color,
            backgroundColor: typeConfig.bgColor,
          }}
        >
          {typeConfig.icon} {typeConfig.label}
        </span>
        <div className="flex items-center gap-1 text-[10px] text-slate-500">
          <Clock className="w-3 h-3" />
          {timeAgo}
        </div>
      </div>

      {/* Memory text */}
      <p className={`text-xs text-slate-300 leading-relaxed ${compact ? 'line-clamp-2' : 'line-clamp-3'}`}>
        {memory.text}
      </p>

      {/* Footer: importance bar + confidence */}
      <div className="mt-2 flex items-center gap-3">
        {/* Importance bar */}
        <div className="flex-1">
          <div className="flex items-center justify-between mb-0.5">
            <span className="text-[9px] text-slate-500 uppercase tracking-wider">Importance</span>
            <span className="text-[9px] text-slate-400">{Math.round(memory.importance * 100)}%</span>
          </div>
          <div className="score-bar">
            <div
              className="score-bar-fill"
              style={{
                width: `${memory.importance * 100}%`,
                background: `linear-gradient(90deg, ${typeConfig.color}88, ${typeConfig.color})`,
              }}
            />
          </div>
        </div>

        {/* Confidence badge */}
        {memory.confidence < 1.0 && (
          <div className="flex items-center gap-1" title={`Confidence: ${Math.round(memory.confidence * 100)}%`}>
            <AlertTriangle className="w-3 h-3 text-amber-400" />
            <span className="text-[9px] text-amber-400">{Math.round(memory.confidence * 100)}%</span>
          </div>
        )}
      </div>

      {/* Superseded indicator */}
      {isSuperseded && (
        <div className="mt-2 flex items-center gap-1 text-[9px] text-amber-400/70">
          <AlertTriangle className="w-3 h-3" />
          Superseded by newer memory
        </div>
      )}
    </motion.div>
  );
}

/** Helper: format ISO timestamp as relative time */
function getRelativeTime(isoString: string): string {
  try {
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  } catch {
    return 'unknown';
  }
}
