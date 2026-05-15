/**
 * MemoryCategories Component — Interactive type filter chips.
 * Shows count per category and allows filtering.
 */
import { motion } from 'framer-motion';
import { MEMORY_TYPE_CONFIG } from '@/lib/types';
import type { Memory, MemoryType } from '@/lib/types';

interface MemoryCategoriesProps {
  memories: Memory[];
  activeFilter: MemoryType | null;
  onFilterChange: (type: MemoryType | null) => void;
}

export function MemoryCategories({ memories, activeFilter, onFilterChange }: MemoryCategoriesProps) {
  // Count memories by type
  const counts: Record<string, number> = {};
  for (const mem of memories) {
    counts[mem.memory_type] = (counts[mem.memory_type] || 0) + 1;
  }

  const types = Object.keys(MEMORY_TYPE_CONFIG) as MemoryType[];

  return (
    <div className="flex flex-wrap gap-1.5">
      {/* All filter */}
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => onFilterChange(null)}
        className={`
          text-[10px] px-2.5 py-1 rounded-full font-medium transition-all duration-200
          ${activeFilter === null
            ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
            : 'bg-[var(--color-surface-3)] text-slate-400 border border-transparent hover:border-[var(--color-border)]'
          }
        `}
      >
        All ({memories.length})
      </motion.button>

      {types.map((type) => {
        const config = MEMORY_TYPE_CONFIG[type];
        const count = counts[type] || 0;
        const isActive = activeFilter === type;

        return (
          <motion.button
            key={type}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => onFilterChange(isActive ? null : type)}
            className={`
              text-[10px] px-2.5 py-1 rounded-full font-medium transition-all duration-200
              ${isActive
                ? 'border'
                : 'bg-[var(--color-surface-3)] text-slate-400 border border-transparent hover:border-[var(--color-border)]'
              }
            `}
            style={isActive ? {
              color: config.color,
              backgroundColor: config.bgColor,
              borderColor: config.color + '40',
            } : {}}
          >
            {config.icon} {config.label} ({count})
          </motion.button>
        );
      })}
    </div>
  );
}
