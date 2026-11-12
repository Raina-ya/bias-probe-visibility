from __future__ import annotations

import sys
import unittest
from collections import Counter
from pathlib import Path

import numpy as np


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "experiments" / "power"))

import run_power_analysis_v4 as power_v4  # noqa: E402


class PowerAnalysisV4Tests(unittest.TestCase):
    def test_repaired_matrix_contract(self) -> None:
        labels, digest = power_v4.load_labels(REPO / "docs" / "theory" / "06_matrix.csv")
        self.assertEqual(digest, power_v4.MATRIX_SHA256)
        self.assertEqual(Counter(labels), power_v4.EXPECTED_COUNTS)

    def test_bootstrap_weights_resample_within_strata(self) -> None:
        rng = np.random.default_rng(123)
        weights = power_v4.stratified_bootstrap_weights(rng, resamples=25)
        self.assertEqual(weights.shape, (25, 100))
        self.assertTrue(np.all(weights.sum(axis=1) == 100))
        for start in range(0, 100, 4):
            self.assertTrue(np.all(weights[:, start : start + 4].sum(axis=1) == 4))

    def test_observed_label_precedence(self) -> None:
        labels = power_v4.observed_labels(
            np.asarray([0.85, 0.85, 0.05, 0.50]),
            np.asarray([0.05, 0.20, 0.05, 0.05]),
        )
        self.assertEqual(labels.tolist(), ["visible", "partial", "blind", "partial"])

    def test_graph_rate_means_remain_in_unit_interval(self) -> None:
        rng = np.random.default_rng(456)
        means = np.asarray([0.05, 0.45, 0.85])
        shared = rng.uniform(-1.0, 1.0, size=100)
        rates = power_v4.graph_rates(rng, means, shared)
        self.assertTrue(np.all((rates >= 0) & (rates <= 1)))


if __name__ == "__main__":
    unittest.main()

