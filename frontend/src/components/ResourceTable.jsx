import { motion } from 'framer-motion';
import { useCountUp, usePrefersReducedMotion } from '../motion';
import './DataTable.css';

const RES_ORDER = [
  ['energy', 'Energy'],
  ['minerals', 'Minerals'],
  ['food', 'Food'],
  ['consumer_goods', 'Consumer Goods'],
  ['alloys', 'Alloys'],
  ['influence', 'Influence'],
  ['unity', 'Unity'],
  ['physics_research', 'Physics'],
  ['society_research', 'Society'],
  ['engineering_research', 'Engineering'],
  ['rare_crystals', 'Rare Crystals'],
];

function fmt(n) {
  if (n === undefined || n === null) return '—';
  return Math.abs(n) >= 10 ? Math.round(n).toLocaleString() : (Math.round(n * 10) / 10).toString();
}
function flowClass(n) {
  return n > 0.5 ? 'pos' : n < -0.5 ? 'neg' : 'zero';
}
function flowStr(n) {
  if (n === undefined) return '';
  return (n > 0 ? '+' : '') + fmt(n);
}

function ResourceRow({ label, stock, flow }) {
  const reduced = usePrefersReducedMotion();
  const display = useCountUp(stock ?? 0, { reduced, format: fmt });
  return (
    <tr>
      <td>{label}</td>
      <td className="num">
        <motion.span>{display}</motion.span>
      </td>
      <td className={`num ${flowClass(flow || 0)}`}>{flowStr(flow)}</td>
    </tr>
  );
}

export default function ResourceTable({ resources, balance }) {
  const res = resources || {};
  const bal = balance || {};
  const rows = RES_ORDER.filter(([k]) => res[k] !== undefined);

  return (
    <table className="data-table">
      <thead>
        <tr>
          <th>Resource</th>
          <th className="num">Stock</th>
          <th className="num">/mo</th>
        </tr>
      </thead>
      <tbody>
        {rows.map(([k, label]) => {
          let flow = bal[k];
          if (k === 'energy' && bal.trade !== undefined) flow = (bal.energy || 0) + (bal.trade || 0);
          return <ResourceRow key={k} label={label} stock={res[k]} flow={flow} />;
        })}
      </tbody>
    </table>
  );
}
