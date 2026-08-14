import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from aqpo_evidence import load_results, relative_reduction, validate_results


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.data = load_results()

    def test_model_is_not_claimed_as_production_measurement(self):
        self.assertFalse(self.data["production_measurement"])

    def test_all_modeled_trends_are_valid(self):
        self.assertEqual(validate_results(self.data), [])

    def test_agentic_cache_has_higher_hit_ratio(self):
        cache = self.data["cache"]
        self.assertGreater(cache["aqpo_agentic"]["hit_ratio"], cache["aqpo_passive"]["hit_ratio"])

    def test_reduction_is_bounded(self):
        value = relative_reduction(66.2, 23.8)
        self.assertGreater(value, 0)
        self.assertLess(value, 1)

    def test_invalid_baseline_is_rejected(self):
        with self.assertRaises(ValueError):
            relative_reduction(0, 1)


if __name__ == "__main__":
    unittest.main()

