# AQPO Evidence

[![Tests](https://github.com/darisisuresh/quantum-safe-metadata-aqpo-evidence/actions/workflows/ci.yml/badge.svg)](https://github.com/darisisuresh/quantum-safe-metadata-aqpo-evidence/actions/workflows/ci.yml)
[![Pages](https://img.shields.io/badge/GitHub%20Pages-live-6f42c1)](https://darisisuresh.github.io/quantum-safe-metadata-aqpo-evidence/)
[![License: MIT](https://img.shields.io/badge/License-MIT-0b7285.svg)](LICENSE)

Privacy-preserving evidence for **AQPO — Agentic Query Planner and Optimizer**, a research architecture for studying post-quantum metadata overhead in open table layouts.

## Research boundary

AQPO models how expanding cryptographic envelopes may affect metadata-intensive planning paths in Apache Iceberg and Delta-style tables. The included values are analytical benchmark scenarios, not production measurements. They are intended to make the assumptions and trend calculations inspectable.

```text
Query engines
     │
     ▼
AQPO metadata proxy
 ├─ workload predictor
 ├─ verified segment materializer
 ├─ seek-aware cache
 └─ compaction scheduler
     │
     ▼
REST catalog and object storage
```

## Evidence included

- deterministic benchmark dataset covering 1×–16× metadata inflation;
- standard-library Python validation of latency, metadata-read, and cache trends;
- unit tests for dataset integrity and bounded metrics;
- sanitized AEGIS aggregate status and detector limitations;
- privacy gate that rejects manuscripts, raw reports, local paths, private email, and unauthorized attribution.

## Reproduce

```bash
python3 -m unittest discover -s tests -v
python3 scripts/validate_evidence.py
python3 scripts/privacy_check.py
```

## Integrity interpretation

The local final scan reported LOW overall risk, a probabilistic AI-content signal of 0.17 classified as HUMAN, and no flagged citation mismatch. External plagiarism matching was unavailable because no independent comparison corpus was supplied. The raw report remains private because it contains manuscript-derived text.

## Privacy boundary

The manuscript, extracted prose, author email, local paths, and raw integrity reports are intentionally excluded. This repository contains only sanitized aggregate evidence, model inputs, validation code, and public project documentation.

## Citation

```bibtex
@misc{darisi2026aqpoevidence,
  author       = {Suresh kumar Darisi},
  title        = {AQPO Evidence: Quantum-Safe Metadata Optimization},
  year         = {2026},
  howpublished = {GitHub repository},
  url          = {https://github.com/darisisuresh/quantum-safe-metadata-aqpo-evidence}
}
```

## Author

**Suresh kumar Darisi**

## License

MIT License. See [LICENSE](LICENSE).

