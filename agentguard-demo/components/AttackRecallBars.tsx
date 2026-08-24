import type { RobustnessRow } from "@/lib/results";

type Props = {
  rows: RobustnessRow[];
};

export default function AttackRecallBars({ rows }: Props) {
  return (
    <div className="bar-wrap">
      {rows.map((row) => {
        const value = Math.max(0, Math.min(1, Number(row.recall || 0)));
        const pct = Math.round(value * 100);
        return (
          <div className="bar-row" key={row.attack_level}>
            <strong>{row.attack_level}</strong>
            <div className="bar">
              <span style={{ width: `${pct}%` }} />
            </div>
            <span>{pct}%</span>
          </div>
        );
      })}
    </div>
  );
}
