"""Protocol v4 tests: cells, components, E2 semantics, v4 lock, decision analysis."""

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

import analysis_v4  # noqa: E402
import cells_v4  # noqa: E402
import channels  # noqa: E402
import circuits  # noqa: E402
import execution  # noqa: E402
import hashing  # noqa: E402
import manifest  # noqa: E402
import manifest_v4  # noqa: E402
import runner  # noqa: E402
import simulate  # noqa: E402
import split_guard_v4  # noqa: E402

TEST = "software_test"


def _record(width=4, index=0):
    return [r for r in manifest.build_manifest(TEST, REPO) if r.width == width][index]


class MatrixTests(unittest.TestCase):
    def test_matrix_has_42_cells_and_frozen_counts(self) -> None:
        matrix = cells_v4.load_matrix()
        self.assertEqual(set(matrix), set(cells_v4.cells()))
        labels = [r["prediction"] for r in matrix.values()]
        self.assertEqual(
            (labels.count("visible"), labels.count("partial"), labels.count("blind")),
            (4, 13, 25),
        )
        strata = [r["stratum"] for r in matrix.values()]
        self.assertEqual(
            (strata.count("invariant"), strata.count("sensitive")), (23, 19)
        )

    def test_matrix_components_match_cell_mapping(self) -> None:
        for (probe, structure), row in cells_v4.load_matrix().items():
            self.assertEqual(row["component"], cells_v4.component(probe, structure))

    def test_p0_and_e0_are_outside_the_matrix(self) -> None:
        cells = cells_v4.cells()
        self.assertFalse(any(p == "P0" or s == "E0" for p, s in cells))

    def test_designated_probes_are_frozen(self) -> None:
        self.assertEqual(
            cells_v4.DESIGNATED,
            {
                "E1": "P1",
                "E2": "P2",
                "E3": "P3",
                "E4": "P4a",
                "E5": "P4a",
                "E5'": "P4a",
                "E6": "P4a",
            },
        )
        matrix = cells_v4.load_matrix()
        # Gate structures: the designated cell is sensitive against its matched null
        # (which is the clean device used for decision calibration).
        for structure in ("E1", "E2", "E3", "E4"):
            self.assertEqual(
                matrix[(cells_v4.DESIGNATED[structure], structure)]["stratum"],
                "sensitive",
            )

    def test_p4a_sees_every_readout_structure_against_clean_null(self) -> None:
        record = _record()
        clean = execution.run_row(
            split=TEST,
            record=record,
            probe="P4a",
            structure="E0",
            setting="0.0",
            parameter_index=0,
            repeat=0,
            population=True,
        )
        self.assertEqual(clean.components["assignment"], 0.0)
        for structure in ("E4", "E5", "E5'", "E6"):
            setting = {"E4": "(0.08,0.12)", "E5": "0.0", "E5'": "0.0", "E6": "0.0"}[
                structure
            ]
            row = execution.run_row(
                split=TEST,
                record=record,
                probe="P4a",
                structure=structure,
                setting=setting,
                parameter_index=0,
                repeat=0,
                population=True,
            )
            self.assertGreater(row.components["assignment"], 0.03, structure)

    def test_semantic_second_pass_has_no_disagreement(self) -> None:
        with (REPO / "experiments" / "semantic" / "semantic_tests_v4.csv").open(
            encoding="utf-8"
        ) as h:
            rows = list(csv.DictReader(h))
        self.assertEqual(len(rows), 42)
        self.assertTrue(all(r["agrees"] == "1" for r in rows))

    def test_protocol_sidecar_matches(self) -> None:
        recorded = (
            (REPO / split_guard_v4.PROTOCOL_HASH_FILE)
            .read_text(encoding="ascii")
            .split()[0]
        )
        self.assertEqual(
            hashing.canonical_sha256(REPO / split_guard_v4.PROTOCOL), recorded
        )

    def test_protocol_quotes_matrix_hash(self) -> None:
        text = (REPO / split_guard_v4.PROTOCOL).read_text(encoding="utf-8")
        self.assertIn(hashing.canonical_sha256(cells_v4.MATRIX), text)


class E2SemanticsTests(unittest.TestCase):
    def test_cost_rotations_are_tagged_and_counted(self) -> None:
        record = _record()
        for compiled in execution.target_circuits(
            TEST, record, channels.parse_condition("E0", "0.0")
        ):
            n = sum(op[0] == circuits.COST_RZ for op in compiled.ops)
            self.assertEqual(n, len(record.edges) * record.depth)

    def test_folding_cancels_symmetric_over_rotation_exactly(self) -> None:
        record = _record()
        target = execution.target_circuits(
            TEST, record, channels.parse_condition("E0", "0.0")
        )[0]
        noise = simulate.GateNoise(over_rotation=0.04)
        np.testing.assert_allclose(
            simulate.probabilities(circuits.fold(target, 3), noise),
            simulate.probabilities(target, noise),
            atol=1e-12,
        )

    def test_over_rotation_changes_target_and_twin(self) -> None:
        record = _record()
        target = execution.target_circuits(
            TEST, record, channels.parse_condition("E0", "0.0")
        )[0]
        noise = simulate.GateNoise(over_rotation=0.04)
        self.assertGreater(
            np.abs(
                simulate.probabilities(target, noise) - simulate.probabilities(target)
            ).max(),
            1e-6,
        )

    def test_e2_target_equals_scaled_logical_rzz(self) -> None:
        record = _record()
        cand = dict(record.candidates[0])
        scaled = {**cand, "gamma": [1.04 * g for g in cand["gamma"]]}
        seed = execution.transpiler_seed(TEST, record, 0)
        a = simulate.probabilities(
            circuits.compile_target(record.width, record.edges, cand, seed),
            simulate.GateNoise(over_rotation=0.04),
        )
        b = simulate.probabilities(
            circuits.compile_target(record.width, record.edges, scaled, seed)
        )
        np.testing.assert_allclose(a, b, atol=1e-12)


class ComponentTests(unittest.TestCase):
    def test_p4_components_and_e6_contrast_present(self) -> None:
        record = _record()
        row = execution.run_row(
            split=TEST,
            record=record,
            probe="P4b",
            structure="E6",
            setting="0.03",
            parameter_index=0,
            repeat=0,
        )
        for key in ("t_marg", "t_corr", "temporal_contrast"):
            self.assertIn(key, row.components)
        row = execution.run_row(
            split=TEST,
            record=record,
            probe="P4a",
            structure="E6",
            setting="0.03",
            parameter_index=0,
            repeat=0,
        )
        self.assertIn("temporal_contrast", row.components)

    def test_population_e6_contrast_matches_drift(self) -> None:
        record = _record()
        row = execution.run_row(
            split=TEST,
            record=record,
            probe="P4a",
            structure="E6",
            setting="0.03",
            parameter_index=0,
            repeat=0,
            population=True,
        )
        self.assertAlmostEqual(
            row.components["temporal_contrast"], 0.03 * (15 - 1) / 16, places=12
        )

    def test_matched_nulls_parse(self) -> None:
        for structure, setting in cells_v4.MATCHED_NULL.items():
            channels.parse_condition(structure, setting)


class ProvenanceV4Tests(unittest.TestCase):
    def test_v4_registry_verifies(self) -> None:
        import provenance
        import provenance_v4

        self.assertEqual(provenance.check(REPO, provenance_v4.load_registry(REPO)), [])

    def test_v3_registry_unchanged(self) -> None:
        import split_guard

        split_guard.require_development_lock(REPO)


class LockV4Tests(unittest.TestCase):
    def test_v4_refuses_development_and_holdout_without_registration(self) -> None:
        for split in ("development", "holdout"):
            with self.assertRaises(split_guard_v4.LockError):
                split_guard_v4.require_split(REPO, split)
        with self.assertRaises(split_guard_v4.LockError):
            manifest_v4.build_manifest("development", REPO)
        with self.assertRaises(split_guard_v4.LockError):
            runner.preflight("development", "x", True)

    def test_v4_registration_admits_development_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / "repo"
            shutil.copytree(
                REPO,
                copy,
                ignore=shutil.ignore_patterns(".git", "__pycache__", "results"),
            )
            files = {
                f: hashing.canonical_sha256(copy / f)
                for f in split_guard_v4.PRE_DEVELOPMENT_FILES_V4
            }
            record = {
                "registry": "OSF",
                "url": "https://example.invalid/v4-test",
                "timestamp_utc": "2000-01-01T00:00:00Z",
                "commit": "test",
                "files": files,
            }
            (copy / split_guard_v4.DEVELOPMENT_REGISTRATION).write_text(
                json.dumps(record), encoding="utf-8"
            )
            split_guard_v4.require_split(copy, "development")
            with self.assertRaises(split_guard_v4.LockError):
                split_guard_v4.require_split(copy, "holdout")
            target = copy / "src" / "probes.py"
            target.write_text(
                target.read_text(encoding="utf-8") + "\n# edit\n", encoding="utf-8"
            )
            with self.assertRaises(split_guard_v4.LockError):
                split_guard_v4.require_split(copy, "development")

    def test_every_locked_file_exists(self) -> None:
        for f in split_guard_v4.PRE_DEVELOPMENT_FILES_V4:
            self.assertTrue((REPO / f).is_file(), f)


class DecisionAnalysisTests(unittest.TestCase):
    def setUp(self) -> None:
        self.strata = [
            (w, d) for w in range(4, 9) for d in range(1, 6) for _ in range(4)
        ]
        self.g = len(self.strata)

    def test_false_certification_rules(self) -> None:
        certified = np.array([[True, True, False]])
        winner = np.array([[1, -1, -1]])
        ideal = np.array([1])
        np.testing.assert_array_equal(
            analysis_v4.false_certification(certified, winner, ideal),
            [[False, True, False]],
        )
        tie = analysis_v4.false_certification(
            np.array([[True]]), np.array([[1]]), np.array([0])
        )
        self.assertTrue(tie[0, 0])

    def test_no_problem_outcome_when_ci_never_wrong(self) -> None:
        zeros = {s: np.zeros((self.g, 32)) for s in cells_v4.STRUCTURES}
        ones = {s: np.ones((self.g, 32)) for s in cells_v4.STRUCTURES}
        res = analysis_v4.primary_decision(
            zeros,
            zeros,
            ones,
            ones,
            self.strata,
            np.random.default_rng(0),
            resamples=200,
        )
        self.assertEqual(res.outcome, "no_problem")
        self.assertEqual(res.dfc, 0.0)

    def test_improvement_outcome_when_probe_removes_errors(self) -> None:
        rng = np.random.default_rng(1)
        fc0 = {
            s: (rng.random((self.g, 32)) < 0.2).astype(float)
            for s in cells_v4.STRUCTURES
        }
        fc1 = {s: np.zeros((self.g, 32)) for s in cells_v4.STRUCTURES}
        cov = {s: np.ones((self.g, 32)) for s in cells_v4.STRUCTURES}
        res = analysis_v4.primary_decision(
            fc0, fc1, cov, cov, self.strata, np.random.default_rng(2), resamples=200
        )
        self.assertEqual(res.outcome, "improvement")
        self.assertGreater(res.dfc_lower, 0)

    def test_interception_needs_five_units(self) -> None:
        value, units = analysis_v4.interception(
            np.array([1, 0, 0]), np.array([False, True, True])
        )
        self.assertTrue(math.isnan(value))
        self.assertEqual(units, 1)
        value, units = analysis_v4.interception(
            np.ones(6), np.array([False] * 3 + [True] * 3)
        )
        self.assertEqual((value, units), (0.5, 6))

    def test_stratified_agreement_is_not_pooled(self) -> None:
        predicted = {("P1", "E1"): "visible", ("P3", "E1"): "blind"}
        strata_of = {("P1", "E1"): "sensitive", ("P3", "E1"): "invariant"}
        alarms = {
            ("P1", "E1"): np.ones((self.g, 4)),
            ("P3", "E1"): np.zeros((self.g, 4)),
        }
        nulls = {c: np.zeros((self.g, 4)) for c in alarms}
        out = analysis_v4.stratified_agreement(
            predicted,
            strata_of,
            alarms,
            nulls,
            self.strata,
            np.random.default_rng(3),
            resamples=50,
        )
        self.assertEqual(set(out), {"invariant", "sensitive"})
        self.assertEqual(out["sensitive"][0], 1.0)
        self.assertEqual(out["invariant"][0], 1.0)


if __name__ == "__main__":
    unittest.main()
