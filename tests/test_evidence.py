import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from aqpo_evidence import (
    PQC_PROFILES,
    RecencyFrequencyPredictor,
    generate_trace,
    load_results,
    pqc_envelope_bytes,
    relative_reduction,
    replay_trace,
    run_regression,
    validate_results,
)


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.data = load_results()

    def test_prototype_is_not_claimed_as_production_measurement(self):
        self.assertTrue(self.data["prototype_measurement"])
        self.assertFalse(self.data["production_measurement"])

    def test_all_results_are_valid(self):
        self.assertEqual(validate_results(self.data), [])

    def test_nist_parameter_sizes(self):
        self.assertEqual(PQC_PROFILES["ML-KEM-768+ML-DSA-65"]["kem_ciphertext"], 1088)
        self.assertEqual(PQC_PROFILES["ML-KEM-768+ML-DSA-65"]["dsa_signature"], 3309)
        self.assertEqual(pqc_envelope_bytes("ML-KEM-768+ML-DSA-65"), 7533)

    def test_predictor_is_deterministic(self):
        history = [1, 2, 1, 3, 1, 2, 4, 1]
        predictor = RecencyFrequencyPredictor()
        self.assertEqual(predictor.predict(history, 2), predictor.predict(history, 2))
        self.assertEqual(predictor.predict(history, 1), [1])

    def test_trace_replay_is_deterministic(self):
        trace = generate_trace(253, length=200)
        self.assertEqual(replay_trace(trace), replay_trace(trace))

    def test_snapshot_churn_blocks_stale_candidates(self):
        result = replay_trace(generate_trace(7, length=240, churn_every=20))
        self.assertGreater(result["stale_candidates_blocked"], 0)

    def test_agentic_cache_improves_hit_ratio_on_local_trace(self):
        result = replay_trace(generate_trace(11))
        self.assertGreater(result["agentic_hit_ratio"], result["passive_hit_ratio"])

    def test_thirty_seed_regression(self):
        result = run_regression(30)
        self.assertEqual(result["runs"], 30)
        self.assertGreater(result["agentic_hit_ratio"]["mean"], result["passive_hit_ratio"]["mean"])

    def test_reduction_is_bounded(self):
        value = relative_reduction(66.2, 23.8)
        self.assertGreater(value, 0)
        self.assertLess(value, 1)

    def test_invalid_inputs_are_rejected(self):
        with self.assertRaises(ValueError):
            relative_reduction(0, 1)
        with self.assertRaises(ValueError):
            pqc_envelope_bytes("ML-KEM-768+ML-DSA-65", signatures=-1)


if __name__ == "__main__":
    unittest.main()
