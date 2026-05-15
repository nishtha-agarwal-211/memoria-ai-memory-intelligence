/**
 * MemoryTimeline Component — Left panel showing all memories.
 * 
 * Features:
 * - Memory timeline with animated cards
 * - Category filter chips
 * - Add new memory form
 * - Filtered view by type
 */
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MemoryCard } from './MemoryCard';
import { MemoryCategories } from './MemoryCategories';
import type { Memory, MemoryType, MemoryCreate } from '@/lib/types';
import { Database, Plus, X, Loader2 } from 'lucide-react';

interface MemoryTimelineProps {
  memories: Memory[];
  onAddMemory: (memory: MemoryCreate) => Promise<void>;
}

export function MemoryTimeline({ memories, onAddMemory }: MemoryTimelineProps) {
  const [activeFilter, setActiveFilter] = useState<MemoryType | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newText, setNewText] = useState('');
  const [newType, setNewType] = useState<MemoryType>('long_term');
  const [newImportance, setNewImportance] = useState(0.5);
  const [isAdding, setIsAdding] = useState(false);

  // Filter memories
  const filtered = activeFilter
    ? memories.filter(m => m.memory_type === activeFilter)
    : memories;

  const handleAdd = async () => {
    if (!newText.trim() || isAdding) return;
    setIsAdding(true);
    try {
      await onAddMemory({
        text: newText.trim(),
        memory_type: newType,
        importance: newImportance,
      });
      setNewText('');
      setShowAddForm(false);
    } catch {
      // Error handled by hook
    } finally {
      setIsAdding(false);
    }
  };

  return (
    <div className="panel-left flex flex-col h-full glass-strong">
      {/* Header */}
      <div className="px-4 py-3 border-b border-[var(--color-border)]">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Database className="w-4 h-4 text-violet-400" />
            <h2 className="text-sm font-semibold text-white">Memory Bank</h2>
            <span className="text-[10px] text-slate-500 bg-[var(--color-surface-3)] px-1.5 py-0.5 rounded-full">
              {memories.length}
            </span>
          </div>
          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={() => setShowAddForm(!showAddForm)}
            className="w-6 h-6 rounded-md bg-violet-500/20 border border-violet-500/30 flex items-center justify-center hover:bg-violet-500/30 transition-colors"
          >
            {showAddForm ? (
              <X className="w-3 h-3 text-violet-400" />
            ) : (
              <Plus className="w-3 h-3 text-violet-400" />
            )}
          </motion.button>
        </div>

        {/* Category filters */}
        <MemoryCategories
          memories={memories}
          activeFilter={activeFilter}
          onFilterChange={setActiveFilter}
        />
      </div>

      {/* Add Memory Form */}
      <AnimatePresence>
        {showAddForm && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="border-b border-[var(--color-border)] overflow-hidden"
          >
            <div className="p-4 space-y-3">
              <textarea
                value={newText}
                onChange={e => setNewText(e.target.value)}
                placeholder="What should I remember?"
                className="w-full bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-2.5 text-xs text-slate-200 placeholder:text-slate-500 resize-none h-16 outline-none focus:border-violet-500/50 transition-colors"
              />
              <div className="flex gap-2">
                <select
                  value={newType}
                  onChange={e => setNewType(e.target.value as MemoryType)}
                  className="flex-1 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg px-2 py-1.5 text-[10px] text-slate-300 outline-none"
                >
                  <option value="preference">💜 Preference</option>
                  <option value="long_term">🧠 Long Term</option>
                  <option value="session">⚡ Session</option>
                  <option value="episodic">📅 Episodic</option>
                  <option value="semantic">📚 Semantic</option>
                </select>
                <div className="flex items-center gap-1.5">
                  <span className="text-[9px] text-slate-500">IMP</span>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={newImportance}
                    onChange={e => setNewImportance(parseFloat(e.target.value))}
                    className="w-16 h-1 accent-violet-500"
                  />
                  <span className="text-[9px] text-violet-400 w-6">{Math.round(newImportance * 100)}%</span>
                </div>
              </div>
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={handleAdd}
                disabled={!newText.trim() || isAdding}
                className="w-full py-1.5 rounded-lg bg-gradient-to-r from-violet-500 to-purple-600 text-white text-xs font-medium disabled:opacity-30 flex items-center justify-center gap-1.5"
              >
                {isAdding ? (
                  <Loader2 className="w-3 h-3 animate-spin" />
                ) : (
                  <Plus className="w-3 h-3" />
                )}
                Store Memory
              </motion.button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Memory List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        <AnimatePresence mode="popLayout">
          {filtered.length === 0 ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center py-8"
            >
              <Database className="w-8 h-8 text-slate-600 mx-auto mb-2" />
              <p className="text-xs text-slate-500">No memories yet</p>
              <p className="text-[10px] text-slate-600">Add some to get started</p>
            </motion.div>
          ) : (
            filtered.map((memory, i) => (
              <MemoryCard key={memory.id} memory={memory} index={i} compact />
            ))
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
