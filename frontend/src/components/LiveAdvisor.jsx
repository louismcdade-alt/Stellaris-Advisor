import Panel from './Panel';
import AdviceList from './AdviceList';
import ResourceTable from './ResourceTable';
import PowerTable from './PowerTable';
import './LiveAdvisor.css';

export default function LiveAdvisor({ advice }) {
  if (!advice) {
    return <div className="live-empty">Waiting for save data…</div>;
  }
  if (!advice.ok) {
    return <div className="live-empty err">{advice.error || 'No save loaded yet.'}</div>;
  }

  const allAdvice = advice.advice || [];
  const ascList = allAdvice.filter((a) => a.category === 'ascension');
  const mainList = allAdvice.filter((a) => a.category !== 'ascension');
  const res = advice.player?.resources || {};
  const bal = advice.player?.balance || {};
  const empires = advice.empires || [];
  const playerId = advice.player?.id;
  const dlc = advice.dlc?.names ? advice.dlc.names.join(', ') : '—';

  return (
    <>
      <div className="live-grid">
        <div className="live-col">
          <Panel
            title="Recommendations"
            count={mainList.length ? `${mainList.length} tips` : ''}
            flashKey={JSON.stringify(mainList)}
          >
            <AdviceList items={mainList} />
          </Panel>
          {ascList.length > 0 && (
            <Panel
              title="✦ Ascension & Traditions"
              count={`${ascList.length} tips`}
              flashKey={JSON.stringify(ascList)}
            >
              <AdviceList items={ascList} />
            </Panel>
          )}
        </div>
        <div className="live-col">
          <Panel title="Resources & Net Flow">
            <ResourceTable resources={res} balance={bal} />
          </Panel>
          <Panel title="Empire Power — Military">
            <PowerTable empires={empires} playerId={playerId} field="military_power" label="Fleet power" />
          </Panel>
          <Panel title="Empire Power — Economy">
            <PowerTable empires={empires} playerId={playerId} field="economy_power" label="Economy power" />
          </Panel>
          <Panel title="Empire Power — Technology">
            <PowerTable empires={empires} playerId={playerId} field="tech_power" label="Tech power" />
          </Panel>
        </div>
      </div>
      <div className="live-footer">
        Campaign: {advice.campaign || '?'} · save {advice.save_file || '?'} · DLC detected: {dlc} · updates
        automatically on each autosave.
      </div>
    </>
  );
}
