import { motion } from 'framer-motion';
import Logo from './Logo';
import { DUR, EASE, entranceVariant, hoverGlowTransition, usePrefersReducedMotion } from '../motion';
import './Header.css';

const STATUS = {
  connecting: { label: 'connecting…', dot: 'var(--muted)' },
  live: { label: 'live', dot: 'var(--good)' },
  error: { label: 'server unreachable', dot: 'var(--crit)' },
  warn: { label: '', dot: 'var(--warn)' }, // label filled in per-error below
};

export default function Header({ advice, campaigns, selected, onSelect }) {
  const reduced = usePrefersReducedMotion();

  let status;
  let statusLabel;
  if (advice === null) {
    status = STATUS.connecting;
    statusLabel = status.label;
  } else if (advice.ok === false && advice.error === undefined) {
    status = STATUS.error;
    statusLabel = status.label;
  } else if (advice.ok === false) {
    status = STATUS.warn;
    statusLabel = advice.error || 'no data';
  } else {
    status = STATUS.live;
    statusLabel = status.label;
  }

  const empireName = advice?.ok ? advice.player?.name || '—' : '—';
  const date = advice?.ok ? advice.date || '—' : '—';
  const profileTitle = advice?.ok ? advice.profile?.title || '' : '';
  const profileTraits = advice?.ok && advice.profile?.traits?.length
    ? `Traits: ${advice.profile.traits.join(', ')}`
    : '';

  return (
    <motion.header
      className="header"
      initial={reduced ? false : { opacity: 0, y: -16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: DUR.relaxed, ease: EASE.out }}
    >
      <Logo size={40} />
      <h1>
        STELLARIS <span className="lit">LIVE ADVISOR</span>
      </h1>
      <span className="empire">{empireName}</span>

      {profileTitle && (
        <motion.span
          className="profile"
          title={profileTraits}
          initial={reduced ? false : entranceVariant(0, reduced).hidden}
          animate={entranceVariant(0, reduced).show}
        >
          {profileTitle}
        </motion.span>
      )}

      <span className="date">⟢ {date}</span>
      <span className="spacer" />

      <motion.select
        title="Choose which game to watch"
        value={selected}
        onChange={(e) => onSelect(e.target.value)}
        whileHover={reduced ? undefined : { borderColor: 'var(--accent)' }}
        transition={hoverGlowTransition}
      >
        <option value="">Auto — newest save</option>
        {campaigns.map((c) => (
          <option key={c.folder} value={c.folder}>
            {c.empire} — {c.date}
          </option>
        ))}
      </motion.select>

      <span className="status">
        <span className="dot" style={{ '--dot-color': status.dot }} />
        <span>{statusLabel}</span>
      </span>
    </motion.header>
  );
}
