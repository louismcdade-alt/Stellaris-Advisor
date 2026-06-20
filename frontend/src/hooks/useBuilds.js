import { useEffect, useState } from 'react';
import { fetchBuilds } from '../api';

/** Fetches /api/builds while the Builder tab is active, refetching whenever
 * the goal filter changes. Builds don't change at runtime (no save-polling
 * needed), so there's no interval here -- just fetch-on-demand. */
export function useBuilds(active, goal) {
  const [data, setData] = useState(null);

  useEffect(() => {
    if (!active) return undefined;
    let cancelled = false;

    (async () => {
      try {
        const d = await fetchBuilds(goal);
        if (!cancelled) setData(d);
      } catch {
        if (!cancelled) setData({ ok: false, error: 'Could not load builds.', builds: [] });
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [active, goal]);

  return data;
}
