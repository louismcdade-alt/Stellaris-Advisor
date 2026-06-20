import GoalFilter from './GoalFilter';
import BuildCard from './BuildCard';
import './EmpireBuilder.css';

export default function EmpireBuilder({ data, goal, onGoalChange }) {
  const builds = data?.builds || [];
  const ownedDlc = data?.owned_dlc?.length ? data.owned_dlc.join(', ') : 'Base game';

  return (
    <>
      <div className="builder-head">
        <GoalFilter active={goal} onChange={onGoalChange} />
        <div className="builder-dlc">
          Showing empires you can build with: <b>{ownedDlc}</b>
        </div>
      </div>

      {!data && <div className="builder-empty">Loading builds…</div>}
      {data && !data.ok && <div className="builder-empty err">{data.error || 'error'}</div>}
      {data && data.ok && builds.length === 0 && (
        <div className="builder-empty">No builds match this filter.</div>
      )}
      {data && data.ok && builds.length > 0 && (
        <div className="builds-grid">
          {builds.map((b, i) => (
            <BuildCard key={b.name} build={b} index={i} />
          ))}
        </div>
      )}
    </>
  );
}
