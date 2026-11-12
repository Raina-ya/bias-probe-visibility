"""Tests for the pre-development freeze code of protocol v3."""

from __future__ import annotations

import csv
import json
import math
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

import alarm_calibration as alarms  # noqa: E402
import analysis  # noqa: E402
import hashing  # noqa: E402
import manifest  # noqa: E402
import protocol_contract as contract  # noqa: E402
import split_guard  # noqa: E402
import strength_map  # noqa: E402


class HashingTests(unittest.TestCase):
    def test_crlf_and_lf_copies_hash_identically(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            lf = Path(tmp) / "a.csv"
            crlf = Path(tmp) / "b.csv"
            lf.write_bytes(b"x,y\n1,2\n")
            crlf.write_bytes(b"x,y\r\n1,2\r\n")
            self.assertEqual(
                hashing.canonical_sha256(lf), hashing.canonical_sha256(crlf)
            )

    def test_binary_files_are_not_normalised(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.png"
            b = Path(tmp) / "b.png"
            a.write_bytes(b"\x89PNG\r\n")
            b.write_bytes(b"\x89PNG\n")
            self.assertNotEqual(
                hashing.canonical_sha256(a), hashing.canonical_sha256(b)
            )

    def test_protocol_hash_file_matches_protocol(self) -> None:
        split_guard.check_protocol_hash_file(REPO)


def _locked_copy(tmp: Path) -> Path:
    copy = tmp / "repo"
    shutil.copytree(REPO, copy, ignore=shutil.ignore_patterns(".git", "__pycache__"))
    files = {
        relative: hashing.canonical_sha256(copy / relative)
        for relative in split_guard.PRE_DEVELOPMENT_FILES
    }
    record = {
        "registry": "OSF",
        "url": "https://example.invalid/test-only",
        "timestamp_utc": "2000-01-01T00:00:00Z",
        "commit": "test-only",
        "files": files,
    }
    (copy / split_guard.DEVELOPMENT_REGISTRATION).write_text(
        json.dumps(record), encoding="utf-8"
    )
    return copy


class SplitGuardTests(unittest.TestCase):
    def test_software_test_split_is_always_allowed(self) -> None:
        split_guard.require_split(REPO, "software_test")

    def test_locked_splits_refused_in_this_repository(self) -> None:
        for split in ("development", "holdout", "prop1_pilot", "prop1_scoring"):
            with self.assertRaises(split_guard.LockError):
                split_guard.require_split(REPO, split)

    def test_no_registration_record_is_shipped(self) -> None:
        self.assertFalse((REPO / split_guard.DEVELOPMENT_REGISTRATION).exists())
        self.assertFalse((REPO / split_guard.CONFIRMATORY_REGISTRATION).exists())

    def test_valid_registration_admits_development_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            copy = _locked_copy(Path(tmp))
            split_guard.require_split(copy, "development")
            with self.assertRaises(split_guard.LockError):
                split_guard.require_split(copy, "holdout")

    def test_edit_after_registration_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            copy = _locked_copy(Path(tmp))
            target = copy / "src" / "analysis.py"
            target.write_text(
                target.read_text(encoding="utf-8") + "\n# edit\n", encoding="utf-8"
            )
            with self.assertRaises(split_guard.LockError):
                split_guard.require_split(copy, "development")

    def test_single_run_marker_cannot_be_written_twice(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            split_guard.record_successful_run(repo, "holdout", "first")
            with self.assertRaises(FileExistsError):
                split_guard.record_successful_run(repo, "holdout", "second")


class ManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.records = manifest.build_manifest("software_test", REPO)

    def test_development_manifest_refused_without_lock(self) -> None:
        with self.assertRaises(split_guard.LockError):
            manifest.build_manifest("development", REPO)

    def test_grid_and_family_totals(self) -> None:
        self.assertEqual(len(self.records), 50)
        strata = {(r.width, r.depth) for r in self.records}
        self.assertEqual(len(strata), 25)
        families = [r.family for r in self.records]
        self.assertEqual(families.count("erdos_renyi"), 17)
        self.assertEqual(families.count("watts_strogatz"), 17)
        self.assertEqual(families.count("barabasi_albert"), 16)

    def test_graphs_are_simple_connected_and_sorted(self) -> None:
        for record in self.records:
            self.assertTrue(manifest.is_connected(record.width, record.edges))
            self.assertEqual(list(record.edges), sorted(set(record.edges)))
            self.assertTrue(all(i < j < record.width for i, j in record.edges))
            self.assertEqual(record.first_edge, record.edges[0])

    def test_family_edge_counts(self) -> None:
        for record in self.records:
            if record.family == "barabasi_albert":
                self.assertEqual(len(record.edges), 2 + 2 * (record.width - 3))
            if record.family == "watts_strogatz":
                k = 2 if record.width == 4 else 4
                self.assertEqual(len(record.edges), record.width * k // 2)

    def test_candidates_follow_frozen_ranges(self) -> None:
        for record in self.records:
            self.assertEqual(len(record.candidates), 2)
            for index, candidate in enumerate(record.candidates):
                self.assertEqual(len(candidate["gamma"]), record.depth)
                self.assertTrue(all(0 <= g < 2 * math.pi for g in candidate["gamma"]))
                self.assertTrue(all(0 <= b < math.pi for b in candidate["beta"]))
                self.assertEqual(candidate["identity_pairs"], index == 1)

    def test_manifest_is_deterministic(self) -> None:
        again = manifest.build_manifest("software_test", REPO)
        self.assertEqual(
            manifest.manifest_sha256(self.records), manifest.manifest_sha256(again)
        )

    def test_manifest_matches_cross_platform_golden_hash(self) -> None:
        # Recorded on Linux, NumPy 2.5.3.  A mismatch on another platform is a
        # cross-platform finding to report, never a reason to edit this value.
        self.assertEqual(
            manifest.manifest_sha256(self.records),
            "b93abe7292735353fe4c6d9f092c20adc62acabde0ca7465aa578115e1d0d311",
        )

    def test_manifest_contains_no_ideal_values(self) -> None:
        text = manifest.manifest_json(self.records).lower()
        for forbidden in ("ideal", "delta", "expectation", "counts"):
            self.assertNotIn(f'"{forbidden}', text)


class AlarmCalibrationTests(unittest.TestCase):
    def test_exact_rank_avoids_float_rounding(self) -> None:
        # 20 * 0.95 is 18.999999999999996 in binary floating point.
        self.assertEqual(alarms.order_rank(19, "0.05"), 19)
        self.assertEqual(alarms.order_rank(100, "0.05"), 96)
        self.assertEqual(alarms.order_rank(3, "0.05"), 3)

    def test_strict_alarm_and_ties(self) -> None:
        scores = [float(value) for value in range(1, 101)]
        tau = alarms.threshold(scores, "0.05")
        self.assertEqual(tau, 96.0)
        thresholds = {(4, 1): tau}
        self.assertFalse(alarms.alarm(96.0, (4, 1), thresholds))
        self.assertTrue(alarms.alarm(96.000001, (4, 1), thresholds))

    def test_calibrate_is_per_stratum(self) -> None:
        rows = [((4, 1), 1.0), ((4, 1), 2.0), ((5, 2), 10.0)]
        self.assertEqual(alarms.calibrate(rows), {(4, 1): 2.0, (5, 2): 10.0})


class StrengthMapTests(unittest.TestCase):
    def _rows(self, overrides=None) -> list[strength_map.ReferenceRow]:
        overrides = overrides or {}
        rows = []
        for structure, grid in strength_map.GRIDS.items():
            for label, _ in grid:
                ratio = overrides.get((structure, label), -0.1)
                for graph in range(3):
                    rows.append(
                        strength_map.ReferenceRow(
                            structure, label, f"g{graph}", ratio, False
                        )
                    )
            rows.append(
                strength_map.ReferenceRow(structure, grid[-1][0], "tie", 99.0, True)
            )
        return rows

    def test_main_uses_largest_and_sensitivity_smallest_magnitude(self) -> None:
        chosen = strength_map.chosen_settings(strength_map.choose(self._rows()))
        self.assertEqual(chosen[("E1", "main")], "0.04")
        self.assertEqual(chosen[("E1", "sensitivity")], "0.0025")
        self.assertEqual(chosen[("E2", "main")], "-0.04")  # exact tie -> negative sign
        self.assertEqual(chosen[("E4", "main")], "(0.08,0.12)")  # tie -> listed first
        self.assertEqual(chosen[("E4", "sensitivity")], "(0.01,0.02)")
        self.assertEqual(chosen[("E6", "sensitivity")], "-0.005")
        self.assertEqual(len(chosen), 14)

    def test_more_harmful_sign_wins_and_tiny_differences_tie(self) -> None:
        rows = self._rows({("E3", "0.04"): -0.5, ("E2", "0.04"): -0.1 - 1e-13})
        chosen = strength_map.chosen_settings(strength_map.choose(rows))
        self.assertEqual(chosen[("E3", "main")], "0.04")
        self.assertEqual(chosen[("E2", "main")], "-0.04")

    def test_ideal_ties_are_omitted_from_medians(self) -> None:
        summaries = strength_map.choose(self._rows())
        e1_main = [s for s in summaries if s.structure == "E1" and s.point == "main"][0]
        self.assertEqual(e1_main.ties_omitted, 1)
        self.assertEqual(e1_main.development_median, -0.1)

    def test_missing_setting_is_an_error(self) -> None:
        rows = [
            r for r in self._rows() if not (r.structure == "E5" and r.setting == "0.01")
        ]
        with self.assertRaises(ValueError):
            strength_map.choose(rows)


class AnalysisTests(unittest.TestCase):
    def test_classification_rules(self) -> None:
        self.assertEqual(analysis.classify(0.80, 0.10), "visible")
        self.assertEqual(analysis.classify(0.95, 0.11), "partial")
        self.assertEqual(analysis.classify(0.10, 0.0), "blind")
        self.assertEqual(analysis.classify(0.5, 0.05), "partial")
        self.assertEqual(analysis.classify(math.nan, 0.05), analysis.NOT_EVALUABLE)

    def test_missing_cells_are_disagreements(self) -> None:
        predicted = {(f"P{i}", f"E{j}"): "blind" for i in range(7) for j in range(8)}
        observed = dict(predicted)
        observed.pop(("P0", "E0"))
        self.assertAlmostEqual(analysis.agreement(predicted, observed), 55 / 56)

    def test_primary_endpoint_shares_graph_indices(self) -> None:
        rng = np.random.default_rng(0)
        strata = [
            (w, d) for w in contract.WIDTHS for d in contract.DEPTHS for _ in range(4)
        ]
        graphs = len(strata)
        predicted, observed_alarms = {}, {}
        for i, probe in enumerate(contract.PRIMARY_PROBES):
            for j, structure in enumerate(contract.PRIMARY_STRUCTURES):
                label = ("blind", "partial", "visible")[(i + j) % 3]
                predicted[(probe, structure)] = label
                rate = {"blind": 0.02, "partial": 0.45, "visible": 0.97}[label]
                observed_alarms[(probe, structure)] = (
                    rng.random((graphs, 32)) < rate
                ).astype(float)
        e0 = {
            probe: (rng.random((graphs, 224)) < 0.02).astype(float)
            for probe in contract.PRIMARY_PROBES
        }
        result = analysis.primary_endpoint(
            predicted,
            observed_alarms,
            e0,
            strata,
            np.random.default_rng(1),
            resamples=200,
        )
        self.assertEqual(result.point, 1.0)
        self.assertTrue(result.success)

    def test_wilson_matches_power_summary(self) -> None:
        lower, upper = analysis.wilson_interval(250, 250)
        self.assertAlmostEqual(
            lower, 0.9848661527503766, places=12
        )  # same z=1.96 as power v4
        self.assertEqual(upper, 1.0)

    def test_readout_bias_bound_and_certificate_envelope(self) -> None:
        score = np.array([0.0, 1.0, 1.0, 0.0])
        identity = np.eye(4)
        self.assertEqual(analysis.readout_bias_bound(score, identity), 0.0)
        flip = np.array([[0.9, 0.1], [0.1, 0.9]])
        channel = np.kron(flip, flip)
        bound = analysis.certificate_bound(("P4b", "E5"), score, ["c"], {"c": channel})
        self.assertGreater(bound, 0.0)
        self.assertEqual(
            analysis.certificate_bound(("P1", "E1"), score, ["c"], {"c": channel}),
            math.inf,
        )
        self.assertEqual(
            analysis.certificate_bound(("P4b", "E5"), score, [], {"c": channel}),
            math.inf,
        )
        self.assertFalse(analysis.certify(0.1, math.inf))

    def test_simultaneous_intervals_cover_point_estimate(self) -> None:
        intervals = analysis.simultaneous_intervals([(10, 100), (0, 50), (50, 50)])
        self.assertLess(intervals[0][0], 0.1)
        self.assertGreater(intervals[0][1], 0.1)
        self.assertEqual(intervals[1][0], 0.0)
        self.assertEqual(intervals[2][1], 1.0)
        kept = analysis.retained_channels(
            intervals, {"a": [0.1, 0.0, 1.0], "b": [0.9, 0.0, 1.0]}
        )
        self.assertEqual(kept, ["a"])


class DryRunTests(unittest.TestCase):
    def test_every_ledger_row_conserves_budget(self) -> None:
        path = REPO / "experiments" / "dry_run" / "dry_run_ledger_v2.csv"
        with path.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 85)
        for row in rows:
            self.assertEqual(
                int(row["target_shots"]) + int(row["probe_shots"]), contract.TOTAL_SHOTS
            )
            self.assertEqual(row["budget_conserved"], "1")


if __name__ == "__main__":
    unittest.main()
