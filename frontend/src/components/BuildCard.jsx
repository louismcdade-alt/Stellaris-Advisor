import { motion } from 'framer-motion';
import { entranceVariant, usePrefersReducedMotion } from '../motion';
import './BuildCard.css';

function BoldJoin({ items }) {
  return items.map((item, i) => (
    <span key={item}>
      {i > 0 && ', '}
      <b>{item}</b>
    </span>
  ));
}

export default function BuildCard({ build, index }) {
  const reduced = usePrefersReducedMotion();
  const variant = entranceVariant(index, reduced);
  const isDlc = build.dlc_label !== 'Base game';

  return (
    <motion.div
      className="build-card"
      initial="hidden"
      animate="show"
      variants={variant}
      whileHover={reduced ? undefined : { y: -3 }}
      transition={{ duration: 0.18 }}
    >
      <div className="build-top">
        <span className="build-name">{build.name}</span>
        <span className={`dlcbadge${isDlc ? ' dlc' : ''}`}>{build.dlc_label}</span>
      </div>
      <div className="gchips">
        {build.goals.map((g) => (
          <span className="gchip" key={g}>
            {g}
          </span>
        ))}
      </div>
      <table className="build-table">
        <tbody>
          <tr>
            <th>Ethics</th>
            <td>
              <BoldJoin items={build.ethics} />
            </td>
          </tr>
          <tr>
            <th>Authority</th>
            <td>{build.authority}</td>
          </tr>
          <tr>
            <th>Civics</th>
            <td>{build.civics.join(', ')}</td>
          </tr>
          <tr>
            <th>Origin</th>
            <td>
              <b>{build.origin}</b>
            </td>
          </tr>
          <tr>
            <th>Traits</th>
            <td>{build.traits.join(', ')}</td>
          </tr>
          <tr>
            <th>Ascension</th>
            <td>{build.ascension}</td>
          </tr>
        </tbody>
      </table>
      <div className="build-why">{build.why}</div>
      {build.checked
        && (build.verified ? (
          <div className="vbadge ok">✓ Verified usable in your game</div>
        ) : (
          <div className="vbadge bad">⚠ Not fully usable: {(build.issues || []).join('; ')}</div>
        ))}
    </motion.div>
  );
}
