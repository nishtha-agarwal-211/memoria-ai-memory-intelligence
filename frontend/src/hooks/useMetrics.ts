/**
 * useMetrics Hook — Polls system metrics for the dashboard.
 * 
 * Auto-refreshes every 5 seconds to keep the dashboard live.
 */
import { useState, useCallback, useEffect, useRef } from 'react';
import type { SystemMetrics } from '@/lib/types';
import { getMetrics } from '@/lib/api';

interface UseMetricsReturn {
  metrics: SystemMetrics | null;
  isLoading: boolean;
  refresh: () => Promise<void>;
}

const POLL_INTERVAL = 5000; // 5 seconds

export function useMetrics(): UseMetricsReturn {
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const refresh = useCallback(async () => {
    try {
      setIsLoading(true);
      const data = await getMetrics();
      setMetrics(data);
    } catch {
      // Silently fail — metrics are non-critical
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();

    // Poll for updates
    intervalRef.current = setInterval(refresh, POLL_INTERVAL);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [refresh]);

  return { metrics, isLoading, refresh };
}
