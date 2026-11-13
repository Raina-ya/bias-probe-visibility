"""Task 3-1 holdout driver and primary scoring.

Uses split 99 (software_test) records and synthetic rows only; no holdout seed
is instantiated by these tests.
"""

from __future__ import annotations

import csv
import gzip
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "experiments" / "holdout"))
sys.path.insert(0, str(REPO / "experiments" / "development"))

import cells_v4  # noqa: E402
import manifest_v4  # noqa: E402
import run_holdout_v4 as hold  # noqa: E402
import score_primary_v4 as score  # noqa: E402
import split_guard_v4  # noqa: E402
import strength_map  # noqa: E402

RECORDS = manifest_v4.build_manifest("software_test", REPO)
CHOSEN = {(s, "main"): g[-1][0] for s, g in strength_map.GRIDS.items()} | {
    (s, "sensitivity"): g[0][0] for s, g in strength_map.GRIDS.items()
}


class UnitTests(unittest.TestCase):
    def test_guard_free_manifest_equals_registered_manifest(self) -> None:
        self.assertEqual(hold.records_from_base("software_test"), RECORDS)

    def test_unit_counts(self) -> None:
        n = len(RECORDS)
        self.assertEqual(len(hold.main_units(RECORDS, CHOSEN)), 7 * 7 * n)
        self.assertEqual(len(hold.null_units(RECORDS)), 6 * 7 * n)
        self.assertEqual(len(hold.sensitivity_units(RECORDS, CHOSEN)), 6 * 7 * n)
        units = hold.all_units(RECORDS, CHOSEN)
        self.assertEqual(len(units), len(set(units)))

    def test_holdout_has_100_graphs_and_13300_units(self) -> None:
        # Arithmetic only: 4 graphs per stratum x 25 strata.
        graphs = 4 * 25
        self.assertEqual(graphs * (7 * 7 + 6 * 7 + 6 * 7), 13_300)

    def test_sensitivity_uses_smallest_strength(self) -> None:
        for u in hold.sensitivity_units(RECORDS[:1], CHOSEN):
            _, probe, structure, setting, index, _ = u
            self.assertEqual(setting, strength_map.GRIDS[structure][0][0])
            self.assertEqual(index, 0)
            self.assertNotEqual(probe, "P0")

    def test_nulls_use_matched_null_index(self) -> None:
        for u in hold.null_units(RECORDS[:1]):
            _, _, structure, setting, index, _ = u
            self.assertEqual(setting, cells_v4.MATCHED_NULL[structure])
            self.assertEqual(index, len(strength_map.GRIDS[structure]))

    def test_post_run_access_state_aware(self) -> None:
        if not split_guard_v4.marker_path(REPO, "holdout").exists():
            with self.assertRaises(split_guard_v4.LockError):
                hold.records_after_run(REPO)
        else:
            self.assertEqual(len(hold.records_after_run(REPO)), 100)
            with self.assertRaises(split_guard_v4.LockError):  # no second run
                split_guard_v4.require_split(REPO, "holdout")

    def test_lock_strength_map_check(self) -> None:
        chosen = hold.locked_chosen(REPO)
        self.assertEqual(chosen[("E1", "main")], "0.04")


def write(out: Path, phase: str, entries) -> None:
    folder = out / phase
    folder.mkdir(parents=True, exist_ok=True)
    k = len(list(folder.glob("*.gz")))
    with gzip.open(
        folder / f"shard_{k:04d}_of_0001.jsonl.gz", "wt", encoding="utf-8"
    ) as h:
        for e in entries:
            h.write(json.dumps(e) + "\n")


class CompletenessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.records = RECORDS[:2]
        self.units = hold.all_units(self.records, CHOSEN)

    def entries(self, split="holdout"):
        return [
            {"unit": list(u), "status": "ok", "rows": [{"split": split}] * 32}
            for u in self.units
        ]

    def run_check(self, entries_by_phase):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            for phase, entries in entries_by_phase.items():
                write(out, phase, entries)
            return hold.check_complete(out, self.records, CHOSEN)

    def by_phase(self, entries):
        out = {}
        for e in entries:
            out.setdefault(e["unit"][0], []).append(e)
        return out

    def test_complete(self) -> None:
        self.assertTrue(self.run_check(self.by_phase(self.entries()))["complete"])

    def test_missing_unit(self) -> None:
        r = self.run_check(self.by_phase(self.entries()[1:]))
        self.assertFalse(r["complete"])
        self.assertEqual(r["missing"], 1)

    def test_duplicate_unit(self) -> None:
        e = self.entries()
        r = self.run_check(self.by_phase(e + e[:1]))
        self.assertFalse(r["complete"])
        self.assertEqual(r["duplicated"], 1)

    def test_wrong_split(self) -> None:
        self.assertFalse(
            self.run_check(self.by_phase(self.entries("development")))["complete"]
        )

    def test_failed_unit_counts_as_present(self) -> None:
        e = self.entries()
        e[0] = {"unit": e[0]["unit"], "status": "failed", "error": "x"}
        r = self.run_check(self.by_phase(e))
        self.assertTrue(r["complete"])
        self.assertEqual(r["failed_units"], 1)


# ---------------------------------------------------------------- scoring


def row(repeat, gap, alarm_p0, statistic=0.0, components=None):
    return {
        "split": "holdout",
        "repeat": repeat,
        "alarm_p0": alarm_p0,
        "statistic": statistic,
        "components": {"gap_target": gap, **(components or {})},
    }


class ScoringTests(unittest.TestCase):
    """25 graphs, one per stratum; ideal winner A (+1) everywhere.

    Under E2 only, P0 certifies the wrong winner on graph 0 in every repeat and
    the designated probe P2 alarms there, so R1 does not certify: dFC > 0.
    """

    def build(self, out: Path, fail_one=False):
        graphs = [f"holdout-w{w}-p{d}-g0" for w in range(4, 9) for d in range(1, 6)]
        (out / "reference").mkdir(parents=True)
        with (out / "reference" / "holdout_reference_v4.csv").open(
            "w", newline=""
        ) as h:
            w = csv.writer(h)
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
            for g in graphs:
                w.writerow([g, 0, 0, "E1", "main", "0.04", "0.1", "0.1", 0, 0])
        entries = []
        probes = {"P0", "P2"} | set(cells_v4.DESIGNATED.values())
        for s in cells_v4.STRUCTURES:
            for p in sorted(probes):
                for k, g in enumerate(graphs):
                    wrong = s == "E2" and k == 0
                    comps = {}
                    comp = cells_v4.component(p, s)
                    if comp != "statistic":
                        comps[comp] = 1e9 if (wrong and p == "P2") else 0.0
                    stat = 1e9 if (wrong and p == "P2" and comp == "statistic") else 0.0
                    rows = [
                        row(r, -0.05 if wrong else 0.05, False, stat, comps)
                        for r in range(32)
                    ]
                    entries.append(
                        {
                            "unit": ["main", p, s, "x", 0, g],
                            "status": "ok",
                            "rows": rows,
                        }
                    )
        if fail_one:
            entries[0] = {"unit": entries[0]["unit"], "status": "failed", "error": "x"}
        write(out, "main", entries)

    def run_score(self, fail_one=False):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            self.build(out, fail_one)
            score.main(
                [
                    "--out",
                    str(out),
                    "--report",
                    str(out / "report.md"),
                    "--skip-input-check",
                ]
            )
            result = json.loads((out / "primary_endpoint_v4.json").read_text())
            text = (out / "report.md").read_text()
            with self.assertRaises(FileExistsError):  # written once
                score.main(
                    [
                        "--out",
                        str(out),
                        "--report",
                        str(out / "report.md"),
                        "--skip-input-check",
                    ]
                )
            return result, text

    def test_interception_gives_positive_dfc(self) -> None:
        result, text = self.run_score()
        main = result["primary_designated"]["main"]
        per = result["primary_designated"]["per_structure"]
        self.assertEqual(per["E2"]["R0_false_certifications"], 32)
        self.assertEqual(per["E2"]["R1_false_certifications"], 0)
        self.assertAlmostEqual(per["E2"]["FC_R0"], 1 / 25)
        self.assertAlmostEqual(main["dFC"], (1 / 25) / 7)
        self.assertEqual(per["E2"]["intercepted"], 1.0)
        self.assertIn("Outcome:", text)
        self.assertIn(main["outcome"], {"improvement", "inconclusive", "no_problem"})

    def test_failed_unit_makes_primary_not_evaluable(self) -> None:
        result, _ = self.run_score(fail_one=True)
        primary = result["primary_designated"]
        self.assertEqual(primary["outcome"], "not_evaluable")
        self.assertEqual(primary["complete_case_graphs"], 24)
        self.assertNotIn(
            "complete_case_sensitivity", primary
        )  # a stratum lost its graph

    def test_strict_alarm(self) -> None:
        taus = {("P2", "E2", 4, 1): 0.5}
        rows = {"holdout-w4-p1-g0": [row(0, 0.1, False, statistic=0.5)]}
        cert, _ = score.decisions(rows, ["holdout-w4-p1-g0"], "P2", "E2", taus, True)
        self.assertTrue(cert[0, 0])
        rows = {"holdout-w4-p1-g0": [row(0, 0.1, False, statistic=0.5000001)]}
        cert, _ = score.decisions(rows, ["holdout-w4-p1-g0"], "P2", "E2", taus, True)
        self.assertFalse(cert[0, 0])

    def test_scoring_refused_before_marker(self) -> None:
        if split_guard_v4.marker_path(REPO, "holdout").exists():
            score.check_inputs(REPO)  # admitted after the single run
        else:
            with self.assertRaises(SystemExit):
                score.check_inputs(REPO)


if __name__ == "__main__":
    unittest.main()
