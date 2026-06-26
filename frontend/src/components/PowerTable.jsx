import { motion } from 'framer-motion';
import { DUR, EASE, usePrefersReducedMotion } from '../motion';
import './DataTable.css';

function fmt(n) {
  if (n === undefined || n === null) return '—';
  return Math.abs(n) >= 10 ? Math.round(n).toLocaleString() : (Math.round(n * 10) / 10).toString();
}

/** Ranked horizontal-bar comparison table -- reused for military, economy
 * and tech power so the three Empire Power panels share one implementation. */
export default function PowerTable({ empires, playerId, field, label }) {
  const reduced = usePrefersReducedMotion();
  const emp = (empires || [])
    .filter((e) => e.type === 'default')
    .slice()
    .sort((a, b) => (b[field] || 0) - (a[field] || 0));
  const max = emp.length ? emp[0][field] || 0 : 1;

  return (
    <table className="data-table">
      <thead>
        <tr>
          <th>Empire</th>
          <th>{label}</th>
          <th className="num">Score</th>
        </tr>
      </thead>
      <tbody>
        {emp.map((e) => {
          const you = e.id === playerId;
          const frac = Math.max(0.02, (e[field] || 0) / (max || 1));
          return (
            <tr key={e.id} className={you ? 'you' : ''}>
              <td className="name">
                {e.name}
                {you ? ' ◄ you' : ''}
              </td>
              <td style={{ width: '46%' }}>
                <div className="bar-track">
                  <motion.span
                    className="bar-fill"
                    initial={reduced ? false : { scaleX: 0 }}
                    animate={{ scaleX: frac }}
                    transition={{ duration: DUR.relaxed, ease: EASE.out }}
                  />
                </div>
              </td>
              <td className="num">{fmt(e[field])}</td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}
