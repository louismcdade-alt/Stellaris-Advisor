import { useCallback, useEffect, useState } from 'react';
import { fetchCampaigns, selectCampaign } from '../api';

/** Polls /api/campaigns on an interval (30s, like the original dashboard)
 * and provides a select() that calls /api/select and returns the fresh
 * advice payload it responds with. */
export function useCampaigns(pollMs = 30000) {
  const [campaigns, setCampaigns] = useState([]);
  const [selected, setSelected] = useState('');

  const refresh = useCallback(async () => {
    try {
      const d = await fetchCampaigns();
      if (d.ok) {
        setCampaigns(d.campaigns);
        setSelected((cur) => cur || d.selected || '');
      }
    } catch {
      // The advice poll already surfaces connectivity errors; stay quiet here.
    }
  }, []);

  useEffect(() => {
    // Standard fetch-on-mount-then-poll pattern: refresh() is async, so the
    // actual setState happens after an await, not synchronously in the
    // effect body -- the lint rule can't see that through the indirection.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    refresh();
    const id = setInterval(refresh, pollMs);
    return () => clearInterval(id);
  }, [refresh, pollMs]);

  const select = useCallback(async (campaign) => {
    setSelected(campaign);
    return selectCampaign(campaign);
  }, []);

  return { campaigns, selected, select };
}
