"""Task 3-2 secondary scorer.  No holdout row is read by these tests.

The dry run uses the development rows (split 10, already reported in
docs/freeze/dev_mismatch_v4.md) and is skipped when the gitignored development
shards are absent (for example on CI).
"""

from __future__ import annotations

import csv
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "experiments" / "holdout"))

import channels  # noqa: E402
import score_secondary_v4 as sec  # noqa: E402

DEV = REPO / "results" / "development_v4"


class EventModelTests(unittest.TestCase):
    def test_p4a_events_under_e4(self) -> None:
        ro = channels.readout_for(
            channels.parse_condition("E4", "(0.08,0.12)"), 4, (0, 1), (0, 1, 2)
        )
        p = sec.predicted_events("P4a", 4, ro)
        self.assertEqual(len(p), 8)
        np.testing.assert_allclose(p[:4], 0.08)
        np.testing.assert_allclose(p[4:], 0.88)

    def test_p4b_events_under_e5(self) -> None:
        ro = channels.readout_for(
            channels.parse_condition("E5", "-0.01"), 4, (0, 2), (0, 1, 2)
        )
        p = sec.predicted_events("P4b", 4, ro)
        self.assertEqual(len(p), 6 * 4 * 3)
        pairs = [(i, j) for i in range(4) for j in range(i + 1, 4)]
        k = pairs.index((0, 2)) * 12  # prep 00 of pair (0, 2): outcomes 01, 10, 11
        np.testing.assert_allclose(p[k + 2], 0.10 * 0.10 - 0.01, atol=1e-12)
        np.testing.assert_allclose(p[k], 0.10 * 0.90 + 0.01, atol=1e-12)
        k = pairs.index((1, 3)) * 12  # untouched pair
        np.testing.assert_allclose(p[k : k + 3], 0.0, atol=1e-12)

    def test_observed_events_match_layout(self) -> None:
        row = {
            "circuits": [
                {
                    "role": "probe",
                    "label": "prep0",
                    "shots": 10,
                    "counts": {"0000": 8, "1000": 2},
                },
                {
                    "role": "probe",
                    "label": "prep1",
                    "shots": 10,
                    "counts": {"1111": 9, "1110": 1},
                },
            ]
        }
        self.assertEqual(
            sec.probe_events("P4a", row, 4),
            [(2, 10), (0, 10), (0, 10), (0, 10), (10, 10), (10, 10), (10, 10), (9, 10)],
        )

    def test_intervals_are_simultaneous(self) -> None:
        lo, hi = sec.intervals([(0, 100), (100, 100), (50, 100)])
        self.assertEqual((lo[0], hi[1]), (0.0, 1.0))
        self.assertLess(lo[2], 0.5)
        self.assertGreater(hi[2], 0.5)


@unittest.skipUnless(
    (DEV / "main").is_dir() and any((DEV / "main").glob("*.gz")),
    "development shards absent",
)
class DevelopmentDryRun(unittest.TestCase):
    def test_reproduces_development_agreement(self) -> None:
        chosen = {}
        with (DEV / "strength_map_v4.csv").open(encoding="utf-8") as h:
            for r in csv.DictReader(h):
                if r["chosen"] == "1":
                    chosen[(r["structure"], r["point"])] = r["setting"]
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            for name, src in (
                ("main", "main"),
                ("nulls", "nulls"),
                ("sensitivity", "main"),
            ):
                (out / name).mkdir()
                for p in (DEV / src).glob("*.gz"):
                    try:
                        os.symlink(p, out / name / p.name)
                    except OSError:  # Windows without symlink rights
                        (out / name / p.name).write_bytes(p.read_bytes())
            (out / "reference").mkdir()
            with (
                (DEV / "reference" / "dev_reference_v4.csv").open(
                    encoding="utf-8"
                ) as h,
                (out / "reference" / "holdout_reference_v4.csv").open(
                    "w", encoding="utf-8", newline=""
                ) as o,
            ):
                w = csv.writer(o)
                w.writerow(
                    [
                        "graph_id",
                        "width",
                        "depth",
                        "structure",
                        "point",
                        "setting",
                        "ideal_gap",
                        "noisy_population_gap",
                        "ideal_tie",
                        "flipped",
                    ]
                )
                for r in csv.DictReader(h):
                    for point in ("main", "sensitivity"):
                        if chosen.get((r["structure"], point)) == r["setting"]:
                            w.writerow(
                                [
                                    r["graph_id"],
                                    r["width"],
                                    r["depth"],
                                    r["structure"],
                                    point,
                                    r["setting"],
                                    r["ideal_gap"],
                                    r["noisy_population_gap"],
                                    r["ideal_tie"],
                                    r["flipped"],
                                ]
                            )
            code = sec.main(
                [
                    "--out",
                    str(out),
                    "--report",
                    str(out / "r.md"),
                    "--skip-input-check",
                    "--records-split",
                    "development",
                    "--expected-split",
                    "development",
                ]
            )
            self.assertEqual(code, 0)
            result = json.loads(
                (out / "secondary_endpoints_v4.json").read_text(encoding="utf-8")
            )
        agree = result["visibility"]["agreement"]
        # docs/freeze/dev_mismatch_v4.md: invariant 22/23, sensitive 11/19.
        self.assertAlmostEqual(agree["invariant"]["point"], 22 / 23)
        self.assertAlmostEqual(agree["sensitive"]["point"], 11 / 19)
        self.assertEqual(
            set(result["readout_certificate"]), {"P4a/E4", "P4b/E4", "P4b/E5"}
        )


if __name__ == "__main__":
    unittest.main()
