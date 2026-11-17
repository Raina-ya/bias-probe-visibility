"""Task 4-1 synthesis: cause rules and deterministic figure (no raw rows needed)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "experiments" / "synthesis"))

import boundary_synthesis_v4 as syn  # noqa: E402


def cell(stratum, predicted, observed, power, fa):
    return {
        "stratum": stratum,
        "predicted": predicted,
        "observed": observed,
        "power": power,
        "false_alarm": fa,
        "agree": predicted == observed,
        "smallest_strength_power": power / 2,
        "smallest_strength_label": observed,
    }


class CauseRules(unittest.TestCase):
    def test_rules(self) -> None:
        self.assertEqual(
            syn.classify_cell(cell("invariant", "blind", "partial", 0.13, 0.13))[0],
            "design",
        )
        self.assertEqual(
            syn.classify_cell(cell("invariant", "blind", "partial", 0.19, 0.05))[0],
            "method",
        )
        self.assertEqual(
            syn.classify_cell(cell("sensitive", "visible", "partial", 0.4, 0.05))[0],
            "resources",
        )
        self.assertEqual(
            syn.classify_cell(cell("sensitive", "partial", "blind", 0.05, 0.05))[0],
            "resources",
        )
        self.assertEqual(
            syn.classify_cell(cell("sensitive", "partial", "visible", 0.98, 0.05))[0],
            "model",
        )

    def test_figure_is_deterministic(self) -> None:
        cells = {
            f"{p}/{s}": cell("sensitive", "partial", "partial", 0.3, 0.05)
            for p in syn.PROBES
            for s in syn.cells_v4.STRUCTURES
        }
        bd = {
            f"{s}|main": {"median": -0.1, "flipped_graphs": 0}
            for s in syn.cells_v4.STRUCTURES
        }
        self.assertEqual(syn.svg(cells, bd), syn.svg(cells, bd))
        self.assertTrue(syn.svg(cells, bd).startswith("<svg"))

    def test_development_labels_parse(self) -> None:
        labels = syn.dev_labels(REPO / syn.DEV_MISMATCH)
        self.assertEqual(len(labels), 42)
        self.assertEqual(labels["P1/E1"], "partial")


if __name__ == "__main__":
    unittest.main()
