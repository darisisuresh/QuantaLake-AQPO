# QuantaLake AQPO

[![Tests](https://github.com/darisisuresh/QuantaLake-AQPO/actions/workflows/ci.yml/badge.svg)](https://github.com/darisisuresh/QuantaLake-AQPO/actions/workflows/ci.yml)
[![Pages](https://img.shields.io/badge/GitHub%20Pages-live-6f42c1)](https://darisisuresh.github.io/QuantaLake-AQPO/)
[![License: MIT](https://img.shields.io/badge/License-MIT-0b7285.svg)](LICENSE)

**QuantaLake AQPO** is an Agentic Query Planner and Optimizer research project for studying post-quantum metadata overhead in open table layouts.

## Research boundary

AQPO models how expanding cryptographic envelopes may affect metadata-intensive planning paths in Apache Iceberg and Delta-style tables. The repository now includes a deterministic trace-replay prototype in addition to analytical scenarios. Neither is a production deployment or a measurement of a live Iceberg catalog.

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

## Research artifacts

- deterministic benchmark dataset covering 1×–16× analytical metadata inflation;
- standard-library trace-replay prototype with 30 seeded regression runs;
- an explicit, auditable recency-frequency predictor and fail-closed snapshot handling;
- byte-exact ML-KEM-768 and ML-DSA-65 envelope accounting from NIST FIPS 203/204;
- validation of latency, metadata-read, cache, and failure-handling trends;
- unit tests for dataset integrity and bounded metrics;
- sanitized AEGIS aggregate status and detector limitations;
- privacy gate that rejects manuscripts, raw reports, local paths, private email, and unauthorized attribution.

## Reproduce

```bash
python3 -m unittest discover -s tests -v
python3 scripts/validate_evidence.py
python3 scripts/privacy_check.py
```

## Prototype configuration and results

`recency-frequency-v1` ranks objects with `0.65 × exp(-age/12) + 0.35 × frequency/window` over a 64-request window. The trace generator uses 96 objects, a 12-object rotating hot set, 800 requests per run, snapshot churn every 100 requests, cache capacity 24, and prefetch budget 4. Across 30 fixed seeds, passive mean hit ratio was 0.706375 (range 0.677500–0.730000) and predictor-assisted mean hit ratio was 0.728542 (range 0.698750–0.755000). The absolute increase was 0.022167, or 3.14% relative to the passive mean; this is a descriptive result, not a claim of statistical or production superiority.

Mean prefetch precision was only 0.054240 (range 0.048927–0.063447), a negative operational signal showing that the transparent baseline predictor is not deployment-ready. Snapshot guards blocked a mean 129.07 stale candidates per run (range 98–160). These are executed trace-replay results. The latency, metadata-volume, and I/O-reduction scenarios remain analytical hypotheses rather than live-system measurements.

The selected byte-accounting profile is ML-KEM-768 plus ML-DSA-65: 1,184-byte KEM public key, 1,088-byte KEM ciphertext, 1,952-byte signature public key, and 3,309-byte signature. The prototype does not execute PQC primitives, so it makes no encryption, decapsulation, signing, or verification timing claim.

## Failure and deployment boundary

Regression coverage includes snapshot churn and stale-candidate rejection. A practical deployment must additionally provide read-only catalog identity, tenant-isolated encrypted cache, deterministic invalidation on snapshot/key/policy change, bypass on proxy failure, bounded prefetch bandwidth, observability, shadow/canary rollout, and rollback thresholds. Catalog outage, corrupt objects, parser mismatch, clock skew, and model drift remain integration-test requirements rather than completed production evidence.

## Integrity interpretation

The 2026-09-02 final scan with AEGIS Integrity 3.0.0 at commit `f850aeb` reported LOW overall risk, a probabilistic AI-content signal of 0.14, IEEE guideline compliance, grammar quality 0.99, and no citation-integrity issue across 15 references. The upstream AEGIS suite passed 192 tests, and this repository passed 10 tests. External plagiarism matching was unavailable because no independent comparison corpus was supplied. The watermark detector was disabled as outside scope. The raw report remains private because it contains manuscript-derived text.

## Privacy boundary

The manuscript, extracted prose, author email, local paths, and raw integrity reports are intentionally excluded. This repository contains only sanitized aggregate evidence, model inputs, validation code, and public project documentation.

## Citation

```bibtex
@misc{darisi2026quantalake,
  author       = {Suresh kumar Darisi},
  title        = {QuantaLake AQPO: Quantum-Safe Metadata Optimization},
  year         = {2026},
  howpublished = {GitHub repository},
  url          = {https://github.com/darisisuresh/QuantaLake-AQPO}
}
```

## Author

**Suresh kumar Darisi**

## License

MIT License. See [LICENSE](LICENSE).
