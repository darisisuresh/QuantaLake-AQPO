"""Deterministic AQPO trace-replay prototype and evidence validation."""

from __future__ import annotations

import json
import math
import random
import statistics
from collections import Counter, OrderedDict
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

# Byte lengths from NIST FIPS 203 Tables 2-3 and FIPS 204 Tables 1-2.
PQC_PROFILES = {
    "ML-KEM-512+ML-DSA-44": {"kem_public_key": 800, "kem_ciphertext": 768, "dsa_public_key": 1312, "dsa_signature": 2420},
    "ML-KEM-768+ML-DSA-65": {"kem_public_key": 1184, "kem_ciphertext": 1088, "dsa_public_key": 1952, "dsa_signature": 3309},
    "ML-KEM-1024+ML-DSA-87": {"kem_public_key": 1568, "kem_ciphertext": 1568, "dsa_public_key": 2592, "dsa_signature": 4627},
}


def load_results(path: Path | None = None) -> dict:
    source = path or ROOT / "results" / "benchmark_summary.json"
    return json.loads(source.read_text(encoding="utf-8"))


def relative_reduction(baseline: float, candidate: float) -> float:
    if baseline <= 0:
        raise ValueError("baseline must be positive")
    return (baseline - candidate) / baseline


def pqc_envelope_bytes(profile: str, signatures: int = 1, kem_envelopes: int = 1) -> int:
    """Return byte-exact public envelope size, excluding private keys and payload."""
    if signatures < 0 or kem_envelopes < 0:
        raise ValueError("artifact counts must be non-negative")
    p = PQC_PROFILES[profile]
    # KEM public key+ciphertext and DSA public key+signature are retained explicitly.
    return kem_envelopes * (p["kem_public_key"] + p["kem_ciphertext"]) + signatures * (
        p["dsa_public_key"] + p["dsa_signature"]
    )


@dataclass(frozen=True)
class Request:
    object_id: int
    snapshot: int


class RecencyFrequencyPredictor:
    """Transparent recency-frequency ranker used by the prototype.

    score(o,t) = 0.65*exp(-age/12) + 0.35*frequency/window.
    It is selected as an auditable baseline; it is not a neural or semantic model.
    """

    def __init__(self, window: int = 64, recency_weight: float = 0.65, decay: float = 12.0):
        self.window = window
        self.recency_weight = recency_weight
        self.decay = decay

    def scores(self, history: list[int]) -> dict[int, float]:
        recent = history[-self.window :]
        counts = Counter(recent)
        last = {obj: len(recent) - 1 - recent[::-1].index(obj) for obj in counts}
        now = len(recent) - 1
        return {
            obj: self.recency_weight * math.exp(-(now - pos) / self.decay)
            + (1 - self.recency_weight) * counts[obj] / max(1, len(recent))
            for obj, pos in last.items()
        }

    def predict(self, history: list[int], budget: int = 4) -> list[int]:
        return [obj for obj, _ in sorted(self.scores(history).items(), key=lambda item: (-item[1], item[0]))[:budget]]


def generate_trace(seed: int, length: int = 800, objects: int = 96, hot_objects: int = 12, churn_every: int = 100) -> list[Request]:
    rng = random.Random(seed)
    trace: list[Request] = []
    for i in range(length):
        snapshot = i // churn_every
        if rng.random() < 0.78:
            obj = (rng.randrange(hot_objects) + snapshot * 3) % objects
        else:
            obj = rng.randrange(objects)
        trace.append(Request(obj, snapshot))
    return trace


def replay_trace(trace: list[Request], capacity: int = 24, prefetch_budget: int = 4) -> dict[str, float]:
    """Replay requests through passive LRU and guarded predictor-assisted caches."""
    passive: OrderedDict[tuple[int, int], None] = OrderedDict()
    agentic: OrderedDict[tuple[int, int], None] = OrderedDict()
    predictor = RecencyFrequencyPredictor()
    history: list[int] = []
    passive_hits = agentic_hits = stale_blocked = predicted = useful_predictions = 0

    def touch(cache: OrderedDict, key: tuple[int, int]) -> bool:
        hit = key in cache
        if hit:
            cache.move_to_end(key)
        else:
            cache[key] = None
            if len(cache) > capacity:
                cache.popitem(last=False)
        return hit

    for req in trace:
        key = (req.object_id, req.snapshot)
        passive_hits += touch(passive, key)
        agentic_hits += touch(agentic, key)
        # A prior-snapshot match is observable but rejected fail-closed.
        stale_blocked += any(obj == req.object_id and snap != req.snapshot for obj, snap in agentic)
        if len(history) >= 8:
            candidates = predictor.predict(history, prefetch_budget)
            predicted += len(candidates)
            for obj in candidates:
                candidate = (obj, req.snapshot)
                if candidate == key:
                    useful_predictions += 1
                touch(agentic, candidate)
        history.append(req.object_id)

    n = len(trace)
    return {
        "requests": n,
        "passive_hit_ratio": passive_hits / n,
        "agentic_hit_ratio": agentic_hits / n,
        "prefetch_precision": useful_predictions / max(1, predicted),
        "stale_candidates_blocked": stale_blocked,
    }


def run_regression(seeds: int = 30) -> dict:
    runs = [replay_trace(generate_trace(seed)) for seed in range(seeds)]
    summary = {"runs": seeds, "trace_requests_per_run": int(runs[0]["requests"]), "predictor": "recency-frequency-v1"}
    for metric in ("passive_hit_ratio", "agentic_hit_ratio", "prefetch_precision", "stale_candidates_blocked"):
        values = [run[metric] for run in runs]
        summary[metric] = {
            "mean": round(statistics.fmean(values), 6),
            "min": round(min(values), 6),
            "max": round(max(values), 6),
        }
    return summary


def validate_results(data: dict) -> list[str]:
    errors: list[str] = []
    if data.get("production_measurement") is not False:
        errors.append("prototype evidence must not be labeled production data")
    if data.get("prototype_measurement") is not True:
        errors.append("results must identify the trace-replay prototype measurement")

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

    if data["pqc_profile"]["name"] not in PQC_PROFILES:
        errors.append("unknown PQC profile")
    if data["regression"]["runs"] < 30:
        errors.append("fewer than 30 regression runs")
    for policy, metrics in data["cache"].items():
        for name, value in metrics.items():
            if not 0 <= value <= 1:
                errors.append(f"{policy}.{name} is outside [0, 1]")
    return errors
