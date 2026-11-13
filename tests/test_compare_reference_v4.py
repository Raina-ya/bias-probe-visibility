"""Tests for the CI reference comparison (no development data needed)."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "experiments" / "development"))

import compare_reference_v4 as cmp  # noqa: E402

REF_HEADER = "graph_id,width,depth,structure,setting,ideal_gap,noisy_population_gap,ideal_tie,harmful_ratio,flipped\n"
MAP_HEADER = "structure,point,setting,magnitude,development_median,chosen,graphs_used,ties_omitted,input_sha256\n"


def write(root: Path, ref_rows, map_rows) -> Path:
    (root / "reference").mkdir(parents=True)
    (root / cmp.REFERENCE).write_text(REF_HEADER + "".join(ref_rows), encoding="utf-8")
    (root / cmp.STRENGTH_MAP).write_text(
        MAP_HEADER + "".join(map_rows), encoding="utf-8"
    )
    return root


REF = ["g0,4,1,E1,0.04,0.1,0.09,0,-0.1,0\n", "g1,4,1,E1,0.04,0.2,0.15,0,-0.25,0\n"]
MAP = [
    "E1,main,0.04,0.04,-0.2,1,2,0,x\n",
    "E1,sensitivity,0.0025,0.0025,-0.01,1,2,0,x\n",
]


class CompareTests(unittest.TestCase):
    def run_case(self, ref_b, map_b):
        with tempfile.TemporaryDirectory() as tmp:
            a = write(Path(tmp) / "a", REF, MAP)
            b = write(Path(tmp) / "b", ref_b, map_b)
            return cmp.compare(a, b)

    def test_identical(self) -> None:
        r = self.run_case(REF, MAP)
        self.assertFalse(r["decision_changed"])
        self.assertEqual(r["reference_columns"]["harmful_ratio"]["rows_differing"], 0)

    def test_float_difference_is_reported_not_failed(self) -> None:
        r = self.run_case([REF[0], "g1,4,1,E1,0.04,0.2,0.15,0,-0.2500000001,0\n"], MAP)
        self.assertFalse(r["decision_changed"])
        self.assertEqual(r["reference_columns"]["harmful_ratio"]["rows_differing"], 1)
        self.assertGreater(
            r["reference_columns"]["harmful_ratio"]["max_abs_difference"], 0
        )

    def test_flag_change_is_a_decision_change(self) -> None:
        r = self.run_case([REF[0], "g1,4,1,E1,0.04,0.2,0.15,0,-0.25,1\n"], MAP)
        self.assertTrue(r["decision_changed"])

    def test_chosen_change_is_a_decision_change(self) -> None:
        r = self.run_case(REF, [MAP[0], "E1,sensitivity,0.0025,0.0025,-0.01,0,2,0,x\n"])
        self.assertTrue(r["decision_changed"])

    def test_missing_row_is_a_decision_change(self) -> None:
        r = self.run_case(REF[:1], MAP)
        self.assertTrue(r["decision_changed"])


if __name__ == "__main__":
    unittest.main()
