"""Correctness checks for the design-check simulators (no protocol data)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "experiments" / "design_checks"))
sys.path.insert(0, str(REPO / "src"))

import gate_ratio_check as gate  # noqa: E402
import readout_ratio_check as readout  # noqa: E402


class DesignCheckTests(unittest.TestCase):
    def test_noiseless_density_matrix_matches_statevector(self) -> None:
        edges = ((0, 1), (1, 2), (0, 2), (2, 3))
        candidate = {"gamma": [0.7, 1.9], "beta": [0.4, 2.1], "identity_pairs": True}
        dm = gate.cut_value(4, edges, candidate, "none", 0.0)
        # The design-check gate convention RZ(theta) inside CX-RZ-CX equals
        # exp(-i theta/2 Z_i Z_j), i.e. QAOA angle gamma_sv = -theta up to phase.
        probs, _, score = readout.qaoa_probabilities(4, edges, [-0.7, -1.9], [0.4, 2.1])
        self.assertAlmostEqual(dm, float(probs @ score), places=12)

    def test_full_depolarization_mixes_the_pair(self) -> None:
        state = gate.DensityMatrix(3)
        state.depolarize(0, 2, 1.0)
        self.assertAlmostEqual(float(np.trace(state.rho).real), 1.0, places=12)
        p = state.probabilities().reshape(2, 2, 2)
        np.testing.assert_allclose(p.sum(axis=1), np.full((2, 2), 0.25), atol=1e-12)

    def test_uniform_readout_scales_gap_by_lambda_squared(self) -> None:
        edges = ((0, 1), (1, 2), (2, 3), (0, 3), (0, 2))
        pa, _, s = readout.qaoa_probabilities(4, edges, [0.9], [0.3])
        pb, _, _ = readout.qaoa_probabilities(4, edges, [2.2], [1.1])
        gap = pa @ s - pb @ s
        rates = [(0.08, 0.12)] * 4
        noisy = (
            readout.tensor_readout(pa, 4, rates) @ s
            - readout.tensor_readout(pb, 4, rates) @ s
        )
        self.assertAlmostEqual(noisy, 0.8**2 * gap, places=12)


if __name__ == "__main__":
    unittest.main()
