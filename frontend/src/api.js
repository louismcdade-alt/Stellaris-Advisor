const BASE = '/api';

async function getJson(url) {
  const res = await fetch(url, { cache: 'no-store' });
  return res.json();
}

export const fetchAdvice = () => getJson(`${BASE}/advice`);
export const fetchCampaigns = () => getJson(`${BASE}/campaigns`);
export const selectCampaign = (campaign) => getJson(`${BASE}/select?campaign=${encodeURIComponent(campaign)}`);
export const fetchFleet = () => getJson(`${BASE}/fleet`);
export const fetchBuilds = (goal) => getJson(goal ? `${BASE}/builds?goal=${encodeURIComponent(goal)}` : `${BASE}/builds`);
