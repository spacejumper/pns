const steps = [
  {
    title: "1) User-Mandat wird signiert",
    body: "EIP-712 Mandat definiert Limits, Budgetfenster, erlaubte Empfaenger und Ablaufzeit.",
  },
  {
    title: "2) Agent sammelt Kontext",
    body: "Tools wie invoice/search koennen untrusted Inhalte liefern (Injection-Kanal).",
  },
  {
    title: "3) Guard evaluiert vor Broadcast",
    body: "S0 Signatur/Expiry, S1 Policy, S2 Taint, S3 Anomaly, S4 Fusion -> ALLOW/ALERT/BLOCK.",
  },
  {
    title: "4) Nur ALLOW geht on-chain",
    body: "Geblockte Transfers werden verworfen, optional Circuit Breaker am GuardedWallet wird gesetzt.",
  },
  {
    title: "5) Post-Execution Monitor als Baseline",
    body: "Detektor auf bestaetigten Events zeigt denselben Ansatz nach Settlement (zu spaet fuer Recovery).",
  },
];

export default function FlowTimeline() {
  return (
    <div className="timeline">
      {steps.map((step) => (
        <div className="timeline-step" key={step.title}>
          <strong>{step.title}</strong>
          <p>{step.body}</p>
        </div>
      ))}
    </div>
  );
}
