import { useEffect, useState } from 'react';
import { fetchAdvice } from '../api';

/** Polls /api/advice on an interval, like the original dashboard's 5s tick.
 * Exposes a setter too, so selecting a campaign can apply the payload that
 * /api/select already returns without waiting for the next poll. */
export function useAdvice(pollMs = 5000) {
  const [data, setData] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function tick() {
      try {
        const d = await fetchAdvice();
        if (!cancelled) setData(d);
      } catch {
        if (!cancelled) setData({ ok: false, error: 'server unreachable' });
      }
    }

    tick();
    const id = setInterval(tick, pollMs);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, [pollMs]);

  return [data, setData];
}
