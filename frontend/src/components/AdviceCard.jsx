import { motion } from 'framer-motion';
import { entranceVariant, usePrefersReducedMotion } from '../motion';
import './AdviceCard.css';

export default function AdviceCard({ advice, index }) {
  const reduced = usePrefersReducedMotion();
  const variant = entranceVariant(index, reduced);

  return (
    <motion.div
      className={`advice-card ${advice.priority}`}
      style={{ '--catc': `var(--cat-${advice.category}, var(--line))` }}
      initial="hidden"
      animate="show"
      variants={variant}
    >
      <div className="advice-top">
        <span className={`advice-badge ${advice.priority}`}>{advice.priority}</span>
        <span className="advice-title">{advice.title}</span>
        <span className="advice-cat">{advice.category}</span>
      </div>
      <div className="advice-detail">{advice.detail}</div>
    </motion.div>
  );
}
