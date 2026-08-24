type Props = {
  title: string;
  value: string;
  detail?: string;
};

export default function MetricCard({ title, value, detail }: Props) {
  return (
    <div className="card">
      <div className="metric-label">{title}</div>
      <div className="metric">{value}</div>
      {detail ? <div className="small">{detail}</div> : null}
    </div>
  );
}
