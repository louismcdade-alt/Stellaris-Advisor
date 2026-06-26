import './Panel.css';

/** Reusable section chrome: corner-cut Stellaris panel with a scan-sweep
 * highlight and an optional title bar. Shared by every tab (Live Advisor,
 * Fleet Manager, Empire Builder) so the chrome stays consistent.
 *
 * `flashKey`, when it changes, briefly re-triggers an inset glow over the
 * panel body -- the "new data just landed" cue, ported from the original
 * dashboard's scan-flash effect. Pass a value derived from the data's
 * signature (e.g. a JSON.stringify of what's rendered) so it only fires
 * when content actually changes, not on every poll.
 */
export default function Panel({ title, count, flashKey, children, className = '' }) {
  return (
    <section className={`panel ${className}`}>
      {title && (
        <h2>
          {title}
          {count ? <span className="panel-count">{count}</span> : null}
        </h2>
      )}
      <div className="panel-body">
        {children}
        {flashKey !== undefined && <span key={flashKey} className="panel-flash" />}
      </div>
    </section>
  );
}
