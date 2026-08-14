#!/usr/bin/env python3
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from aqpo_evidence import load_results, relative_reduction, validate_results

data = load_results()
errors = validate_results(data)
if errors:
    raise SystemExit("\n".join(errors))

baseline = data["metadata_read_mb"]["baseline_pq"]["16"]
agentic = data["metadata_read_mb"]["aqpo_agentic"]["16"]
print(f"Evidence valid; modeled 16x metadata reduction: {relative_reduction(baseline, agentic):.1%}")

