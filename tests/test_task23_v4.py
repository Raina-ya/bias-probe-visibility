"""Task 2-3 tools: thresholds, development labels, and the confirmatory lock builder.

Synthetic inputs only; no development or holdout rows are read.
"""

from __future__ import annotations

import gzip
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "experiments" / "development"))
sys.path.insert(0, str(REPO / "src"))

import build_confirmatory_lock_v4 as lock  # noqa: E402
import calibrate_v4 as cal  # noqa: E402


def entry(stratum, value, key="statistic"):
    return (stratum, "g", 0, {key: value})


class ThresholdTests(unittest.TestCase):
    def test_rank_and_value_follow_section_6_3(self) -> None:
        scores = [entry((4, 1), float(k)) for k in range(64)]
        out = cal.thresholds_for(scores, "P1", "E1")[(4, 1)]
        tau, n, degenerate, note = out["0.05"]
        # rank min(64, ceil(65 * 0.95)) = 62 -> the 62nd smallest value, 61.0
        self.assertEqual((tau, n, degenerate, note), (61.0, 64, False, ""))
        self.assertEqual(out["0.01"][0], 63.0)  # rank min(64, 65) = 64
        self.assertEqual(out["0.10"][0], 58.0)  # rank ceil(58.5) = 59

    def test_degenerate_null_gives_zero(self) -> None:
        scores = [entry((4, 1), 0.0, "assignment") for _ in range(10)]
        tau, _, degenerate, note = cal.thresholds_for(scores, "P4a", "E4")[(4, 1)][
            "0.05"
        ]
        self.assertEqual((tau, degenerate, note), (0.0, True, "degenerate"))

    def test_component_missing_in_e0_is_flagged_degenerate(self) -> None:
        scores = [entry((4, 1), 0.0, "assignment") for _ in range(10)]
        tau, n, degenerate, note = cal.thresholds_for(scores, "P4a", "E6")[(4, 1)][
            "0.05"
        ]
        self.assertEqual(
            (tau, n, degenerate, note), (0.0, 10, True, "not_recorded_in_e0")
        )

    def test_partly_missing_component_is_an_error(self) -> None:
        scores = [
            entry((4, 1), 0.0, "assignment"),
            entry((4, 1), 0.1, "temporal_contrast"),
        ]
        with self.assertRaises(ValueError):
            cal.thresholds_for(scores, "P4a", "E6")

    def test_alarm_is_strict(self) -> None:
        taus = {("P1", "E1", (4, 1)): 0.5}
        rate, n = cal.alarm_rate(
            [entry((4, 1), 0.5), entry((4, 1), 0.6)], "P1", "E1", taus
        )
        self.assertEqual((rate, n), (0.5, 2))

    def test_labels_follow_section_8(self) -> None:
        self.assertEqual(cal.label(0.80, 0.10), "visible")
        self.assertEqual(cal.label(0.80, 0.11), "partial")
        self.assertEqual(cal.label(0.10, 0.0), "blind")
        self.assertEqual(cal.label(0.11, 0.0), "partial")
        self.assertEqual(cal.label(0.12, 0.0, blind=0.15), "blind")


def write_shard(root: Path, phase: str, split: str) -> None:
    folder = root / lock.DEV / phase
    folder.mkdir(parents=True, exist_ok=True)
    with gzip.open(folder / "shard_0000_of_0001.jsonl.gz", "wt", encoding="utf-8") as h:
        h.write(json.dumps({"rows": [{"split": split}]}) + "\n")


class LockEvidenceTests(unittest.TestCase):
    def test_development_only_rows_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_shard(root, "main", "development")
            evidence = lock.split_evidence(root)
            self.assertEqual(evidence["raw_row_splits"], ["development"])
            self.assertTrue(evidence["holdout_refused_by_split_guard_v4"])
            self.assertTrue(evidence["split_20_never_instantiated"])

    def test_holdout_row_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_shard(root, "main", "holdout")
            self.assertFalse(lock.split_evidence(root)["split_20_never_instantiated"])

    def test_holdout_named_path_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_shard(root, "main", "development")
            (root / "results" / "holdout_v4").mkdir()
            self.assertFalse(lock.split_evidence(root)["split_20_never_instantiated"])

    def test_lock_lists_every_section_10_2_product(self) -> None:
        names = set(lock.PRODUCTS)
        for required in (
            "strength_map",
            "thresholds_csv",
            "thresholds_md",
            "dev_mismatch",
            "implementation_error_log",
            "timing_projection_stratified",
        ):
            self.assertIn(required, names)

    def test_tools_never_build_a_holdout_manifest(self) -> None:
        for name in (
            "calibrate_v4.py",
            "build_confirmatory_lock_v4.py",
            "p5_e1_diagnostic_v4.py",
        ):
            text = (REPO / "experiments" / "development" / name).read_text(
                encoding="utf-8"
            )
            self.assertNotIn("build_manifest", text, name)


if __name__ == "__main__":
    unittest.main()
