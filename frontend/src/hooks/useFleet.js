import { useEffect, useState } from 'react';
import { fetchFleet } from '../api';

/** Fetches /api/fleet only while `active` is true (the Fleet tab is open) --
 * the full ship scan behind it is expensive, so we don't run it in the
 * background like the cheap /api/advice poll. Polls every 20s while active,
 * matching the original dashboard's behavior. */
export function useFleet(active, pollMs = 20000) {
  const [data, setData] = useState(null);

  useEffect(() => {
    if (!active) return undefined;
    let cancelled = false;

    async function tick() {
      try {
        const d = await fetchFleet();
        if (!cancelled) setData(d);
      } catch {
        if (!cancelled) setData({ ok: false, error: 'Could not analyze fleet.' });
      }
    }

    tick();
    const id = setInterval(tick, pollMs);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, [active, pollMs]);

  return data;
}
