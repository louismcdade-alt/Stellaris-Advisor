import { motion } from 'framer-motion';
import Panel from './Panel';
import { DUR, EASE, usePrefersReducedMotion } from '../motion';
import './DataTable.css';
import './FleetManager.css';

function fmt(n) {
  if (n === undefined || n === null) return '—';
  return Math.round(n).toLocaleString();
}

function ActionBadge({ delta }) {
  if (delta > 0) return <span className="fleet-act build">Build +{delta}</span>;
  if (delta < 0) return <span className="fleet-act cut">Retire/upgrade {-delta}</span>;
  return <span className="fleet-act ok">OK</span>;
}

function RecBar({ value, max, reduced }) {
  const frac = max > 0 ? value / max : 0;
  return (
    <div className="fleet-recbar">
      <motion.span
        initial={reduced ? false : { scaleX: 0 }}
        animate={{ scaleX: frac }}
        transition={{ duration: DUR.base, ease: EASE.out }}
      />
    </div>
  );
}

// Purely a build-queue readability split -- groups the recommended totals
// into batches of roughly CHUNK_SIZE ships each. This is NOT a naval
// capacity calculation: the only capacity figure we can read from the save
// is the empire-wide `used_naval_capacity`, and on real saves it includes
// things this tool doesn't otherwise track (e.g. strike craft squadrons),
// so it can't safely be used to size how many fleets a given hull mix
// "fits" into. Chunking is an honest stand-in that makes no capacity claim.
const FLEET_CHUNK_SIZE = 20;

function chunkIntoFleets(rows, chunkSize = FLEET_CHUNK_SIZE) {
  const fleets = [];
  let current = {};
  let used = 0;
  for (const r of rows) {
    let remaining = r.recommended;
    while (remaining > 0) {
      const take = Math.min(chunkSize - used, remaining);
      if (take > 0) {
        current[r.class] = (current[r.class] || 0) + take;
        used += take;
        remaining -= take;
      }
      if (used >= chunkSize) {
        fleets.push(current);
        current = {};
        used = 0;
      }
    }
  }
  if (used > 0) fleets.push(current);
  return fleets;
}

export default function FleetManager({ data }) {
  const reduced = usePrefersReducedMotion();

  if (!data) {
    return (
      <div className="fleet-empty">Analyzing your fleet… (scanning every ship can take a few seconds)</div>
    );
  }
  if (!data.ok) {
    return <div className="fleet-empty err">{data.error || 'No fleet data.'}</div>;
  }

  const rows = data.rows || [];
  const specials = data.specials || [];
  const notes = data.notes || [];
  const maxRec = Math.max(1, ...rows.map((r) => Math.max(r.current, r.recommended)));
  const totalRecommended = rows.reduce((sum, r) => sum + r.recommended, 0);
  const fleetGroups = totalRecommended > FLEET_CHUNK_SIZE ? chunkIntoFleets(rows) : [];

  return (
    <>
      <div className="fleet-head">
        <div className="fleet-doctrine">{data.doctrine}</div>
        <div className="fleet-stat">
          Tier: <b>{data.tier}</b>
          &nbsp;·&nbsp; Warships: <b>{data.warships}</b>
          &nbsp;·&nbsp; Naval capacity in use: <b>{fmt(data.used_naval_capacity)}</b>
          &nbsp;·&nbsp; This family: <b>{fmt(data.current_naval_capacity)}</b> used /{' '}
          <b>{fmt(data.recommended_naval_capacity)}</b> recommended
          &nbsp;·&nbsp; costs from <b>{data.data_source}</b>
        </div>
      </div>

      <Panel className="fleet-panel">
        <table className="data-table fleet-table">
          <thead>
            <tr>
              <th>Hull class</th>
              <th className="num">You have</th>
              <th className="num">Recommended</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.class}>
                <td className="hull">{r.class}</td>
                <td className="num">{r.current}</td>
                <td className="num">
                  {r.recommended}
                  <RecBar value={r.recommended} max={maxRec} reduced={reduced} />
                </td>
                <td>
                  <ActionBadge delta={r.delta} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Panel>

      {fleetGroups.length > 1 && (
        <Panel
          className="fleet-panel"
          title="Suggested fleet groupings"
          count={`${fleetGroups.length} fleets`}
        >
          <div className="fleet-groups">
            {fleetGroups.map((g, i) => (
              <div className="fleet-group" key={i}>
                <span className="fleet-group-label">Fleet {i + 1}</span>
                <span className="fleet-group-mix">
                  {Object.entries(g).map(([cls, n]) => `${n} ${cls}`).join(', ')}
                </span>
              </div>
            ))}
          </div>
          <div className="fleet-group-note">
            Batches of ~{FLEET_CHUNK_SIZE} ships for manageable fleet sizes — not a capacity
            limit, just a practical split for your build queue.
          </div>
        </Panel>
      )}

      {specials.length > 0 && (
        <Panel className="fleet-panel">
          <table className="data-table fleet-table">
            <thead>
              <tr>
                <th>Special hull</th>
                <th className="num">You have</th>
                <th className="num">Recommended</th>
                <th>Naval cap</th>
              </tr>
            </thead>
            <tbody>
              {specials.map((s) => (
                <tr key={s.class}>
                  <td className="hull">{s.class}</td>
                  <td className="num">{s.count}</td>
                  <td className="num">—</td>
                  <td>
                    <span className="fleet-act ok">{s.naval_capacity} cap</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Panel>
      )}

      {notes.map((n) => (
        <div className="fleet-note" key={n}>
          {n}
        </div>
      ))}
    </>
  );
}
