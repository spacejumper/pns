import AttackRecallBars from "@/components/AttackRecallBars";
import FlowTimeline from "@/components/FlowTimeline";
import MetricCard from "@/components/MetricCard";
import { loadAccuracy, loadLatency, loadRobustness } from "@/lib/results";

function toPct(value: string | undefined): string {
  if (!value || value === "-") {
    return "-";
  }
  const n = Number(value);
  if (Number.isNaN(n)) {
    return value;
  }
  return `${(n * 100).toFixed(1)}%`;
}

export default function HomePage() {
  const accuracy = loadAccuracy();
  const latency = loadLatency();
  const robustness = loadRobustness();

  const mainAcc = accuracy[0];

  return (
    <main>
      <section className="hero">
        <div className="badge">AgentGuard Demonstrator · PNS 2026</div>
        <h1>Intent-Schutz fuer agentische Stablecoin-Zahlungen</h1>
        <p>
          Diese Demo zeigt, wie ein kryptografisch gueltiger Transfer trotzdem
          gegen den Nutzerwillen verstossen kann und wie ein Pre-Execution Guard
          das in Echtzeit erkennt.
        </p>
        <div className="legend">
          <span className="dot ok" /> ALLOW
        </div>
        <div className="legend">
          <span className="dot alert" /> ALERT
        </div>
        <div className="legend">
          <span className="dot block" /> BLOCK
        </div>
      </section>

      <section className="section">
        <h2>Top-Level Ergebnisse</h2>
        <div className="kpi-grid">
          <MetricCard
            title="Precision"
            value={mainAcc ? toPct(mainAcc.precision) : "-"}
            detail="C1 Detection"
          />
          <MetricCard
            title="Recall"
            value={mainAcc ? toPct(mainAcc.recall) : "-"}
            detail="C1 Detection"
          />
          <MetricCard
            title="F1"
            value={mainAcc ? toPct(mainAcc.f1) : "-"}
            detail="Balance"
          />
          <MetricCard
            title="False Positive Rate"
            value={mainAcc ? toPct(mainAcc.fpr) : "-"}
            detail="Benign Blocking"
          />
        </div>
      </section>

      <div className="grid">
        <section className="section" style={{ gridColumn: "span 7" }}>
          <h2>Wie der Demonstrator funktioniert</h2>
          <FlowTimeline />
        </section>

        <section className="section" style={{ gridColumn: "span 5" }}>
          <h2>Attackenleiter (C3)</h2>
          <p className="small">
            Recall pro Angriffslevel A0-A5. Erwartet: sinkende Erkennung bei
            adaptiven Angreifern.
          </p>
          <AttackRecallBars rows={robustness} />
        </section>
      </div>

      <div className="grid">
        <section className="section" style={{ gridColumn: "span 6" }}>
          <h2>Tests / Experiment-Status</h2>
          <table className="table">
            <thead>
              <tr>
                <th>Test</th>
                <th>Ziel</th>
                <th>Output</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>C1 Accuracy</td>
                <td>Unauthorized unter valider Autorisierung erkennen</td>
                <td>results/table1_accuracy.csv</td>
              </tr>
              <tr>
                <td>C4 Latency</td>
                <td>Pre vs Post Intervention Latenz vergleichen</td>
                <td>results/table2_latency.csv</td>
              </tr>
              <tr>
                <td>C3 Robustness</td>
                <td>Recall-Verlust unter A0-A5 messen</td>
                <td>results/table3_robustness.csv</td>
              </tr>
              <tr>
                <td>Elliptic Baseline</td>
                <td>Offline Plausibilitaets-Benchmark</td>
                <td>results/elliptic_baseline.csv</td>
              </tr>
            </tbody>
          </table>
        </section>

        <section className="section" style={{ gridColumn: "span 6" }}>
          <h2>Interventionslatenz (C4)</h2>
          <table className="table">
            <thead>
              <tr>
                <th>Intervention</th>
                <th>p50</th>
                <th>p95</th>
                <th>p99</th>
                <th>Funds Recovered</th>
              </tr>
            </thead>
            <tbody>
              {latency.map((row) => (
                <tr key={row.intervention}>
                  <td>{row.intervention}</td>
                  <td>{row.p50_ms} ms</td>
                  <td>{row.p95_ms} ms</td>
                  <td>{row.p99_ms} ms</td>
                  <td>{toPct(row.funds_recovered)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <p className="small">
            Interpretation: Bei Post-Execution ist das Ereignis zwar erkennbar,
            aber Settlement ist schon erfolgt.
          </p>
        </section>
      </div>
    </main>
  );
}
