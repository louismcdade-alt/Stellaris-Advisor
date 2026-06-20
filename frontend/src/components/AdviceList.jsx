import AdviceCard from './AdviceCard';
import './AdviceList.css';

export default function AdviceList({ items, emptyText = 'No advice — all clear.' }) {
  if (!items.length) {
    return <div className="advice-empty">{emptyText}</div>;
  }
  return (
    <div className="advice-list">
      {items.map((a, i) => (
        <AdviceCard key={`${a.category}:${a.title}`} advice={a} index={i} />
      ))}
    </div>
  );
}
