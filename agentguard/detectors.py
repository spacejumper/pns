from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from river import anomaly
from river import drift
from sklearn.ensemble import IsolationForest


@dataclass
class DetectionResult:
    anomaly_score: float
    drift_flag: bool


class StreamingDetector:
    def __init__(self, n_trees: int = 25, height: int = 8, window_size: int = 256) -> None:
        self.model = anomaly.HalfSpaceTrees(
            n_trees=n_trees,
            height=height,
            window_size=window_size,
            seed=42,
        )
        self.adwin = drift.ADWIN(delta=0.002)

    def score(self, x: dict[str, float]) -> DetectionResult:
        score = float(self.model.score_one(x))
        self.model.learn_one(x)
        self.adwin.update(score)
        return DetectionResult(anomaly_score=score, drift_flag=bool(self.adwin.drift_detected))


class BatchDetector:
    def __init__(self) -> None:
        self.model = IsolationForest(
            n_estimators=200,
            contamination=0.05,
            random_state=42,
        )
        self.fitted = False
        self.feature_order: list[str] = []

    def fit(self, samples: list[dict[str, float]]) -> None:
        if not samples:
            return
        self.feature_order = sorted(samples[0].keys())
        x = np.array([[s[k] for k in self.feature_order] for s in samples], dtype=float)
        self.model.fit(x)
        self.fitted = True

    def score(self, x: dict[str, float]) -> float:
        if not self.fitted:
            return 0.0
        vec = np.array([[x[k] for k in self.feature_order]], dtype=float)
        # Convert decision function into anomaly-like score where larger = more anomalous.
        raw = float(self.model.decision_function(vec)[0])
        return -raw
