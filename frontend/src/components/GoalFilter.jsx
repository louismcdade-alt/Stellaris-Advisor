import { motion } from 'framer-motion';
import { hoverGlowTransition, pressFeedback, usePrefersReducedMotion } from '../motion';
import './GoalFilter.css';

const GOAL_OPTIONS = ['All', 'Tall', 'Wide', 'Tech', 'Military', 'Trade', 'Economy', 'Bio', 'Gestalt'];

export default function GoalFilter({ active, onChange }) {
  const reduced = usePrefersReducedMotion();

  return (
    <div className="goalfilter">
      {GOAL_OPTIONS.map((g) => {
        const isActive = (active === null && g === 'All') || active === g;
        return (
          <motion.button
            key={g}
            className={`gbtn${isActive ? ' active' : ''}`}
            onClick={() => onChange(g === 'All' ? null : g)}
            whileHover={reduced || isActive ? undefined : { borderColor: 'var(--accent)' }}
            transition={hoverGlowTransition}
            {...pressFeedback(reduced)}
          >
            {g}
          </motion.button>
        );
      })}
    </div>
  );
}
