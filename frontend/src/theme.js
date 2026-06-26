// Empire-flavored color theme: the dashboard's accent shifts to match the
// player's authority/dominant ethic, like Stellaris' own ethic colors.

const THEMES = {
  hive: { accent: '#ff5b6e', accent2: '#ff8a3c', rgb: '255,91,110' },
  machine: { accent: '#8be9fd', accent2: '#5fa8ff', rgb: '139,233,253' },
  megacorp: { accent: '#46e0a0', accent2: '#ffd166', rgb: '70,224,160' },
  militarist: { accent: '#ff7a4d', accent2: '#ff5b6e', rgb: '255,122,77' },
  pacifist: { accent: '#46e0a0', accent2: '#5fa8ff', rgb: '70,224,160' },
  xenophobe: { accent: '#ff8a3c', accent2: '#ff5b6e', rgb: '255,138,60' },
  xenophile: { accent: '#46e0c6', accent2: '#46c6ff', rgb: '70,224,198' },
  materialist: { accent: '#46c6ff', accent2: '#6a7bff', rgb: '70,198,255' },
  spiritualist: { accent: '#c98cff', accent2: '#9a6bff', rgb: '201,140,255' },
  authoritarian: { accent: '#ffd166', accent2: '#ffb454', rgb: '255,209,102' },
  egalitarian: { accent: '#5fa8ff', accent2: '#46c6ff', rgb: '95,168,255' },
  default: { accent: '#46c6ff', accent2: '#6a7bff', rgb: '70,198,255' },
};

const ETHIC_ORDER = [
  'militarist', 'pacifist', 'xenophobe', 'xenophile', 'materialist',
  'spiritualist', 'authoritarian', 'egalitarian',
];

function pickTheme(identity) {
  if (!identity) return ['default', THEMES.default];
  if (identity.authority === 'auth_hive_mind') return ['hive', THEMES.hive];
  if (identity.authority === 'auth_machine_intelligence') return ['machine', THEMES.machine];
  if (identity.authority === 'auth_corporate') return ['megacorp', THEMES.megacorp];
  const ethics = identity.ethics || [];
  for (const key of ETHIC_ORDER) if (ethics.includes(`ethic_fanatic_${key}`)) return [key, THEMES[key]];
  for (const key of ETHIC_ORDER) if (ethics.includes(`ethic_${key}`)) return [key, THEMES[key]];
  return ['default', THEMES.default];
}

let lastThemeKey = '';

/** Sets --accent/--accent2/--accent-rgb on the document root to match the
 * player's empire identity. No-ops if the theme hasn't changed, so it's
 * safe to call on every advice poll. */
export function applyEmpireTheme(identity) {
  const [key, t] = pickTheme(identity);
  if (key === lastThemeKey) return;
  lastThemeKey = key;
  const root = document.documentElement.style;
  root.setProperty('--accent', t.accent);
  root.setProperty('--accent2', t.accent2);
  root.setProperty('--accent-rgb', t.rgb);
}
