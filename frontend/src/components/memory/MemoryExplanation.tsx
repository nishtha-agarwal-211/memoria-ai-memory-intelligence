/**
 * MemoryExplanation Component — Shows WHY a memory was retrieved.
 * 
 * Displays:
 * - Score breakdown bars (semantic, recency, importance, feedback, contextual)
 * - Human-readable reasons
 * - Final ranking score
 * - Memory type and rank position
 */
import { motion } from 'framer-motion';
import type { MemorySearchResult } from '@/lib/types';
import { MEMORY_TYPE_CONFIG } from '@/lib/types';
import { MemoryFeedback } from './MemoryFeedback';
import { Target, TrendingUp } from 'lucide-react';

interface MemoryExplanationProps {
  result: MemorySearchResult;
  index: number;
  onFeedback: (memoryId: string, isUseful: boolean) => void;
}

export function MemoryExplanation({ result, index, onFeedback }: MemoryExplanationProps) {
  const { memory, explanation } = result;
  const { score_breakdown, reasons, rank } = explanation;
  const typeConfig = MEMORY_TYPE_CONFIG[memory.memory_type];

  // Score bars configuration
  const scoreItems = [
    { label: 'Semantic', value: score_breakdown.semantic_similarity, color: '#22d3ee' },
    { label: 'Recency', value: score_breakdown.recency_score, color: '#34d399' },
    { label: 'Importance', value: score_breakdown.importance_score, color: '#a78bfa' },
    { label: 'Feedback', value: score_breakdown.feedback_score, color: '#fbbf24' },
    { label: 'Contextual', value: score_breakdown.contextual_match, color: '#fb7185' },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, x: 12 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.08, duration: 0.3 }}
      className="glass-card p-3 space-y-3"
    >
      {/* Header: rank + type + score */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-5 h-5 rounded-full bg-gradient-to-br from-cyan-500/30 to-blue-500/30 flex items-center justify-center">
            <span className="text-[9px] font-bold text-cyan-300">#{rank}</span>
          </div>
          <span
            className="text-[10px] font-semibold px-2 py-0.5 rounded-full"
            style={{ color: typeConfig.color, backgroundColor: typeConfig.bgColor }}
          >
            {typeConfig.icon} {typeConfig.label}
          </span>
        </div>
        <div className="flex items-center gap-1">
          <Target className="w-3 h-3 text-cyan-400" />
          <span className="text-xs font-bold text-cyan-300">
            {Math.round(score_breakdown.final_score * 100)}%
          </span>
        </div>
      </div>

      {/* Memory text */}
      <p className="text-[11px] text-slate-300 leading-relaxed line-clamp-2">
        "{memory.text}"
      </p>

      {/* Score breakdown bars */}
      <div className="space-y-1.5">
        <div className="flex items-center gap-1 mb-1">
          <TrendingUp className="w-3 h-3 text-slate-500" />
          <span className="text-[9px] text-slate-500 uppercase tracking-wider font-semibold">Score Breakdown</span>
        </div>
        {scoreItems.map(item => (
          <div key={item.label} className="flex items-center gap-2">
            <span className="text-[9px] text-slate-500 w-16 text-right">{item.label}</span>
            <div className="flex-1 score-bar">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${item.value * 100}%` }}
                transition={{ delay: index * 0.08 + 0.3, duration: 0.6, ease: 'easeOut' }}
                className="score-bar-fill"
                style={{ background: item.color }}
              />
            </div>
            <span className="text-[9px] text-slate-400 w-7 text-right">
              {Math.round(item.value * 100)}%
            </span>
          </div>
        ))}
      </div>

      {/* Reasons */}
      <div className="space-y-1">
        <span className="text-[9px] text-slate-500 uppercase tracking-wider font-semibold">Retrieved because:</span>
        <div className="flex flex-wrap gap-1">
          {reasons.slice(0, 3).map((reason, i) => (
            <span
              key={i}
              className="text-[9px] px-2 py-0.5 rounded-full bg-[var(--color-surface-3)] text-slate-400 border border-[var(--color-border)]"
            >
              {reason}
            </span>
          ))}
        </div>
      </div>

      {/* Feedback buttons */}
      <MemoryFeedback memoryId={memory.id} onFeedback={onFeedback} />
    </motion.div>
  );
}
