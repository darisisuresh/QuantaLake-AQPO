#!/usr/bin/env python3
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from aqpo_evidence import load_results, pqc_envelope_bytes, relative_reduction, run_regression, validate_results

data = load_results()
regression = run_regression(30)
if regression != data["regression"]:
    raise SystemExit("stored regression summary differs from deterministic replay")
errors = validate_results(data)
if errors:
    raise SystemExit("\n".join(errors))

profile = data["pqc_profile"]["name"]
baseline = data["metadata_read_mb"]["baseline_pq"]["16"]
agentic = data["metadata_read_mb"]["aqpo_agentic"]["16"]
print(json.dumps({
    "status": "valid",
    "regression_runs": regression["runs"],
    "predictor": regression["predictor"],
    "pqc_profile": profile,
    "pqc_envelope_bytes": pqc_envelope_bytes(profile),
    "modeled_16x_metadata_reduction": round(relative_reduction(baseline, agentic), 6),
}, indent=2))
