/**
 * MemoryFeedback Component — 👍/👎 buttons for memory feedback.
 * 
 * Provides optimistic UI with animated state transitions.
 * Feedback is sent to the backend to influence future rankings.
 */
import { useState } from 'react';
import { motion } from 'framer-motion';
import { ThumbsUp, ThumbsDown } from 'lucide-react';

interface MemoryFeedbackProps {
  memoryId: string;
  onFeedback: (memoryId: string, isUseful: boolean) => void;
}

export function MemoryFeedback({ memoryId, onFeedback }: MemoryFeedbackProps) {
  const [voted, setVoted] = useState<'up' | 'down' | null>(null);

  const handleVote = (isUseful: boolean) => {
    const vote = isUseful ? 'up' : 'down';
    if (voted === vote) return; // Already voted this way
    setVoted(vote);
    onFeedback(memoryId, isUseful);
  };

  return (
    <div className="flex items-center gap-1.5 pt-1 border-t border-[var(--color-border)]">
      <span className="text-[9px] text-slate-500 mr-1">Helpful?</span>
      
      <motion.button
        whileHover={{ scale: 1.15 }}
        whileTap={{ scale: 0.9 }}
        onClick={() => handleVote(true)}
        className={`
          p-1 rounded-md transition-all duration-200
          ${voted === 'up'
            ? 'bg-emerald-500/20 text-emerald-400'
            : 'text-slate-500 hover:text-emerald-400 hover:bg-emerald-500/10'
          }
        `}
      >
        <ThumbsUp className="w-3 h-3" />
      </motion.button>

      <motion.button
        whileHover={{ scale: 1.15 }}
        whileTap={{ scale: 0.9 }}
        onClick={() => handleVote(false)}
        className={`
          p-1 rounded-md transition-all duration-200
          ${voted === 'down'
            ? 'bg-rose-500/20 text-rose-400'
            : 'text-slate-500 hover:text-rose-400 hover:bg-rose-500/10'
          }
        `}
      >
        <ThumbsDown className="w-3 h-3" />
      </motion.button>

      {voted && (
        <motion.span
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-[9px] text-slate-500 ml-1"
        >
          {voted === 'up' ? '✓ Thanks!' : '✓ Noted'}
        </motion.span>
      )}
    </div>
  );
}
