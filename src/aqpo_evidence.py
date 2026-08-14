"""Validation helpers for AQPO analytical evidence."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_results(path: Path | None = None) -> dict:
    source = path or ROOT / "results" / "benchmark_summary.json"
    return json.loads(source.read_text(encoding="utf-8"))


def relative_reduction(baseline: float, candidate: float) -> float:
    if baseline <= 0:
        raise ValueError("baseline must be positive")
    return (baseline - candidate) / baseline


def validate_results(data: dict) -> list[str]:
    errors: list[str] = []
    if data.get("production_measurement") is not False:
        errors.append("analytical evidence must not be labeled production data")

    for factor in ("2", "4", "8", "16"):
        baseline = data["latency_p95_ms"]["baseline_pq"][factor]
        passive = data["latency_p95_ms"]["aqpo_passive"][factor]
        agentic = data["latency_p95_ms"]["aqpo_agentic"][factor]
        if not agentic <= passive <= baseline:
            errors.append(f"latency ordering fails at {factor}x")

        baseline_mb = data["metadata_read_mb"]["baseline_pq"][factor]
        passive_mb = data["metadata_read_mb"]["aqpo_passive"][factor]
        agentic_mb = data["metadata_read_mb"]["aqpo_agentic"][factor]
        if not agentic_mb <= passive_mb <= baseline_mb:
            errors.append(f"metadata-read ordering fails at {factor}x")

    for policy, metrics in data["cache"].items():
        for name, value in metrics.items():
            if not 0 <= value <= 1:
                errors.append(f"{policy}.{name} is outside [0, 1]")
    return errors

