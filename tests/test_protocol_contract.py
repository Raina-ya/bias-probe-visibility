from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

import protocol_contract as contract  # noqa: E402


class ProtocolContractTests(unittest.TestCase):
    def test_matrix_hash_and_counts(self) -> None:
        counts = contract.validate_matrix(REPO / "docs" / "theory" / "06_matrix.csv")
        self.assertEqual(counts, contract.EXPECTED_PRIMARY_COUNTS)

    def test_shot_allocation_is_exact(self) -> None:
        labels = tuple(f"circuit-{index}" for index in range(34))
        allocation = contract.split_even(contract.TOTAL_SHOTS, labels)
        self.assertEqual(sum(allocation.values()), contract.TOTAL_SHOTS)
        self.assertLessEqual(max(allocation.values()) - min(allocation.values()), 1)

    def test_holdout_seed_is_locked(self) -> None:
        with self.assertRaises(PermissionError):
            contract.seed_key(
                split="holdout",
                artifact_code=1,
                structure_code=1,
                probe_code=1,
                width=4,
                depth=1,
                graph_index=0,
                candidate_index=0,
                repeat_index=0,
                parameter_index=0,
            )

    def test_development_seed_is_deterministic(self) -> None:
        arguments = dict(
            split="development",
            artifact_code=1,
            structure_code=1,
            probe_code=1,
            width=4,
            depth=1,
            graph_index=0,
            candidate_index=0,
            repeat_index=0,
            parameter_index=0,
        )
        self.assertEqual(contract.seed_key(**arguments), contract.seed_key(**arguments))

    def test_p0_lcb_decreases_near_tie(self) -> None:
        decisive = contract.hoeffding_selected_lcb(0.20, 8192, 8192)
        near_tie = contract.hoeffding_selected_lcb(0.01, 8192, 8192)
        self.assertGreater(decisive, near_tie)
        self.assertLess(near_tie, 0.0)

    def test_p5_complement_invariance(self) -> None:
        symmetric = {"00": 0.4, "01": 0.1, "10": 0.1, "11": 0.4}
        asymmetric = {"00": 0.5, "01": 0.1, "10": 0.2, "11": 0.2}
        self.assertTrue(math.isclose(contract.complement_asymmetry(symmetric), 0.0))
        self.assertGreater(contract.complement_asymmetry(asymmetric), 0.0)

    def test_p4b_detects_marginal_and_correlation_components(self) -> None:
        independent_assignment = {
            (0, 0): {"00": 81, "01": 9, "10": 9, "11": 1},
            (0, 1): {"00": 9, "01": 81, "10": 1, "11": 9},
            (1, 0): {"00": 9, "01": 1, "10": 81, "11": 9},
            (1, 1): {"00": 1, "01": 9, "10": 9, "11": 81},
        }
        marginal, correlation = contract.p4b_components(independent_assignment)
        self.assertTrue(math.isclose(marginal, 0.1, abs_tol=1e-12))
        self.assertTrue(math.isclose(correlation, 0.0, abs_tol=1e-12))

        correlated = dict(independent_assignment)
        correlated[(0, 0)] = {"00": 90, "01": 0, "10": 0, "11": 10}
        marginal, correlation = contract.p4b_components(correlated)
        self.assertGreaterEqual(marginal, 0.1)
        self.assertGreater(correlation, 0.0)
        self.assertEqual(contract.p4b_score(correlated), max(marginal, correlation))

    def test_strength_map_tie_breaks_by_absolute_strength(self) -> None:
        selected = contract.choose_strength(
            [(-0.04, -1.4), (0.02, -1.6), (-0.01, -1.4)], -1.5
        )
        self.assertEqual(selected, (-0.01, -1.4))

    def test_full_design_fits_structural_caps(self) -> None:
        estimate = contract.estimate_resources()
        self.assertEqual(estimate.graphs, 150)
        self.assertEqual(estimate.parameter_conditions, 60)
        self.assertEqual(estimate.aggregate_rows, 2_016_000)
        self.assertTrue(estimate.within_structural_caps, estimate.to_dict())


if __name__ == "__main__":
    unittest.main()
