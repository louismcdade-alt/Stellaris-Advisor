import { motion } from 'framer-motion';
import { SPRING, hoverGlowTransition, pressFeedback, usePrefersReducedMotion } from '../motion';
import './Tabs.css';

const TABS = [
  { id: 'live', label: '📡 Live Advisor' },
  { id: 'fleet', label: '🚀 Fleet Manager' },
  { id: 'builder', label: '🧬 Empire Builder' },
];

export default function Tabs({ active, onChange }) {
  const reduced = usePrefersReducedMotion();

  return (
    <div className="tabs">
      {TABS.map((t) => {
        const isActive = t.id === active;
        return (
          <motion.button
            key={t.id}
            className={`tab${isActive ? ' active' : ''}`}
            onClick={() => onChange(t.id)}
            whileHover={reduced ? undefined : { color: 'var(--text)' }}
            transition={hoverGlowTransition}
            {...pressFeedback(reduced)}
          >
            {t.label}
            {isActive && (
              <motion.span
                className="tab-indicator"
                layoutId="tab-indicator"
                transition={reduced ? { duration: 0 } : SPRING}
              />
            )}
          </motion.button>
        );
      })}
    </div>
  );
}

export { TABS };
