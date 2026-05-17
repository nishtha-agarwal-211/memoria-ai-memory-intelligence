/**
 * MetricsPanel Component — Right panel showing system metrics.
 * 
 * Displays:
 * - Animated counter cards for key stats
 * - Token usage info
 * - Latency sparkline
 * - Memory category distribution
 */
import { motion } from 'framer-motion';
import type { SystemMetrics, RetrievalMetrics, MemorySearchResult } from '@/lib/types';
import { MEMORY_TYPE_CONFIG } from '@/lib/types';
import { MemoryExplanation } from '../memory/MemoryExplanation';
import {
  Activity,
  Cpu,
  Database,
  Gauge,
  MessageSquare,
  ThumbsUp,
  Timer,
  Zap,
  BarChart3,
  Search,
} from 'lucide-react';

interface MetricsPanelProps {
  metrics: SystemMetrics | null;
  currentMemories: MemorySearchResult[];
  currentMetrics: RetrievalMetrics | null;
  onFeedback: (memoryId: string, isUseful: boolean) => void;
}

export function MetricsPanel({ metrics, currentMemories, currentMetrics, onFeedback }: MetricsPanelProps) {
  return (
    <div className="panel-right flex flex-col h-full glass-strong overflow-y-auto">
      {/* Header */}
      <div className="px-4 py-3 border-b border-[var(--color-border)] flex-shrink-0">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-emerald-400" />
          <h2 className="text-sm font-semibold text-white">Intelligence Panel</h2>
        </div>
        <p className="text-[10px] text-slate-500 mt-0.5">Memory retrieval & system metrics</p>
      </div>

      {/* Retrieved Memories Section */}
      {currentMemories.length > 0 && (
        <div className="p-3 border-b border-[var(--color-border)] flex-shrink-0">
          <div className="flex items-center gap-2 mb-3">
            <Search className="w-3.5 h-3.5 text-cyan-400" />
            <span className="text-xs font-semibold text-white">Retrieved Memories</span>
            <span className="text-[10px] text-cyan-400 bg-cyan-500/10 px-1.5 py-0.5 rounded-full">
              {currentMemories.length}
            </span>
          </div>
          <div className="space-y-2 max-h-[400px] overflow-y-auto">
            {currentMemories.map((result, i) => (
              <MemoryExplanation
                key={result.memory.id}
                result={result}
                index={i}
                onFeedback={onFeedback}
              />
            ))}
          </div>
        </div>
      )}

      {/* Current Interaction Metrics */}
      {currentMetrics && (
        <div className="p-3 border-b border-[var(--color-border)] flex-shrink-0">
          <div className="flex items-center gap-2 mb-3">
            <Timer className="w-3.5 h-3.5 text-amber-400" />
            <span className="text-xs font-semibold text-white">Last Interaction</span>
          </div>
          <div className="grid grid-cols-2 gap-2">
            <MetricMiniCard
              icon={Zap}
              label="Total Latency"
              value={`${Math.round(currentMetrics.total_latency_ms)}ms`}
              color="#fbbf24"
            />
            <MetricMiniCard
              icon={Cpu}
              label="Tokens Used"
              value={String(currentMetrics.tokens_used)}
              color="#a78bfa"
            />
            <MetricMiniCard
              icon={Search}
              label="Memories Found"
              value={String(currentMetrics.memories_retrieved)}
              color="#22d3ee"
            />
            <MetricMiniCard
              icon={BarChart3}
              label="Compression"
              value={`${Math.round(currentMetrics.compression_ratio * 100)}%`}
              color="#34d399"
            />
          </div>
        </div>
      )}

      {/* System Metrics */}
      {metrics && (
        <div className="p-3 flex-shrink-0">
          <div className="flex items-center gap-2 mb-3">
            <Gauge className="w-3.5 h-3.5 text-violet-400" />
            <span className="text-xs font-semibold text-white">System Overview</span>
          </div>

          <div className="grid grid-cols-2 gap-2 mb-3">
            <MetricMiniCard
              icon={Database}
              label="Total Memories"
              value={String(metrics.total_memories)}
              color="#22d3ee"
            />
            <MetricMiniCard
              icon={MessageSquare}
              label="Total Queries"
              value={String(metrics.total_queries)}
              color="#a78bfa"
            />
            <MetricMiniCard
              icon={Timer}
              label="Avg Latency"
              value={`${Math.round(metrics.avg_retrieval_latency_ms)}ms`}
              color="#fbbf24"
            />
            <MetricMiniCard
              icon={ThumbsUp}
              label="Positive Rate"
              value={`${Math.round(metrics.positive_feedback_ratio * 100)}%`}
              color="#34d399"
            />
          </div>

          {/* Category Distribution */}
          {Object.keys(metrics.memories_by_type).length > 0 && (
            <div className="glass-card p-3">
              <span className="text-[9px] text-slate-500 uppercase tracking-wider font-semibold">
                Memory Distribution
              </span>
              <div className="mt-2 space-y-1.5">
                {Object.entries(metrics.memories_by_type).map(([type, count]) => {
                  const config = MEMORY_TYPE_CONFIG[type as keyof typeof MEMORY_TYPE_CONFIG];
                  if (!config) return null;
                  const total = metrics.total_memories || 1;
                  const pct = (count / total) * 100;
                  return (
                    <div key={type} className="flex items-center gap-2">
                      <span className="text-[9px] w-14 text-right" style={{ color: config.color }}>
                        {config.icon} {config.label.slice(0, 6)}
                      </span>
                      <div className="flex-1 score-bar">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${pct}%` }}
                          transition={{ duration: 0.8, ease: 'easeOut' }}
                          className="score-bar-fill"
                          style={{ background: config.color }}
                        />
                      </div>
                      <span className="text-[9px] text-slate-400 w-5 text-right">{count}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Latency Sparkline */}
          {metrics.recent_latencies.length > 1 && (
            <div className="glass-card p-3 mt-2">
              <span className="text-[9px] text-slate-500 uppercase tracking-wider font-semibold">
                Latency History
              </span>
              <div className="mt-2">
                <LatencySparkline latencies={metrics.recent_latencies} />
              </div>
            </div>
          )}
        </div>
      )}

      {/* Empty state */}
      {!metrics && currentMemories.length === 0 && (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <Activity className="w-8 h-8 text-slate-600 mx-auto mb-2" />
            <p className="text-xs text-slate-500">No data yet</p>
            <p className="text-[10px] text-slate-600">Start chatting to see metrics</p>
          </div>
        </div>
      )}
    </div>
  );
}

/** Mini metric card */
function MetricMiniCard({
  icon: Icon,
  label,
  value,
  color,
}: {
  icon: React.ComponentType<{ className?: string; style?: React.CSSProperties }>;
  label: string;
  value: string;
  color: string;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="glass-card p-2.5 !rounded-lg"
    >
      <div className="flex items-center gap-1.5 mb-1">
        <Icon className="w-3 h-3" style={{ color }} />
        <span className="text-[9px] text-slate-500 uppercase tracking-wider">{label}</span>
      </div>
      <div className="text-sm font-bold" style={{ color }}>
        {value}
      </div>
    </motion.div>
  );
}

/** Simple SVG sparkline for latency history */
function LatencySparkline({ latencies }: { latencies: number[] }) {
  const max = Math.max(...latencies, 1);
  const min = Math.min(...latencies, 0);
  const range = max - min || 1;
  const width = 260;
  const height = 40;
  const padding = 2;

  const points = latencies.map((val, i) => {
    const x = padding + (i / Math.max(latencies.length - 1, 1)) * (width - padding * 2);
    const y = height - padding - ((val - min) / range) * (height - padding * 2);
    return `${x},${y}`;
  });

  const pathD = `M ${points.join(' L ')}`;

  return (
    <svg width="100%" height={height} viewBox={`0 0 ${width} ${height}`} className="opacity-80">
      <defs>
        <linearGradient id="sparkGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#22d3ee" stopOpacity="0.3" />
          <stop offset="100%" stopColor="#22d3ee" stopOpacity="0" />
        </linearGradient>
      </defs>
      {/* Fill area */}
      <path
        d={`${pathD} L ${width - padding},${height - padding} L ${padding},${height - padding} Z`}
        fill="url(#sparkGrad)"
      />
      {/* Line */}
      <path d={pathD} fill="none" stroke="#22d3ee" strokeWidth="1.5" />
      {/* Last point dot */}
      {points.length > 0 && (
        <circle
          cx={points[points.length - 1].split(',')[0]}
          cy={points[points.length - 1].split(',')[1]}
          r="2.5"
          fill="#22d3ee"
          className="animate-pulse-glow"
        />
      )}
    </svg>
  );
}
