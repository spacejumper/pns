import fs from "fs";
import path from "path";

export type AccuracyRow = {
  model: string;
  precision: string;
  recall: string;
  f1: string;
  fpr: string;
};

export type LatencyRow = {
  intervention: string;
  p50_ms: string;
  p95_ms: string;
  p99_ms: string;
  funds_recovered: string;
};

export type RobustnessRow = {
  attack_level: string;
  recall: string;
  blocked: string;
  total: string;
};

function parseCsv(content: string): Record<string, string>[] {
  const lines = content.trim().split(/\r?\n/);
  if (lines.length < 2) {
    return [];
  }
  const headers = lines[0].split(",").map((x) => x.trim());
  return lines.slice(1).map((line) => {
    const cols = line.split(",").map((x) => x.trim());
    const obj: Record<string, string> = {};
    headers.forEach((header, idx) => {
      obj[header] = cols[idx] ?? "";
    });
    return obj;
  });
}

function readResult(file: string): Record<string, string>[] {
  const target = path.join(process.cwd(), "..", "results", file);
  if (!fs.existsSync(target)) {
    return [];
  }
  const content = fs.readFileSync(target, "utf-8");
  return parseCsv(content);
}

export function loadAccuracy(): AccuracyRow[] {
  return readResult("table1_accuracy.csv") as AccuracyRow[];
}

export function loadLatency(): LatencyRow[] {
  const rows = readResult("table2_latency.csv") as LatencyRow[];
  if (rows.length) {
    return rows;
  }
  return [
    {
      intervention: "pre_execution_guard",
      p50_ms: "-",
      p95_ms: "-",
      p99_ms: "-",
      funds_recovered: "-",
    },
    {
      intervention: "post_execution_monitor",
      p50_ms: "-",
      p95_ms: "-",
      p99_ms: "-",
      funds_recovered: "-",
    },
  ];
}

export function loadRobustness(): RobustnessRow[] {
  const rows = readResult("table3_robustness.csv") as RobustnessRow[];
  if (rows.length) {
    return rows;
  }
  return ["A0", "A1", "A2", "A3", "A4", "A5"].map((level) => ({
    attack_level: level,
    recall: "0.00",
    blocked: "0",
    total: "0",
  }));
}
