"""Task 2-1 acceptance tests: probes and execution contract (split 99 only)."""

from __future__ import annotations

import ast
import inspect
import itertools
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

import channels  # noqa: E402
import circuits  # noqa: E402
import execution  # noqa: E402
import manifest  # noqa: E402
import probes  # noqa: E402
import reference  # noqa: E402
import runner  # noqa: E402
import simulate  # noqa: E402
import split_guard  # noqa: E402

TEST = "software_test"
PRIMARY = ("P0", "P1", "P2", "P3", "P4a", "P4b", "P5")
SETTINGS = {
    "E0": "0.0",
    "E1": "0.04",
    "E2": "-0.04",
    "E3": "-0.04",
    "E4": "(0.08,0.12)",
    "E5": "0.01",
    "E5'": "0.015625",
    "E6": "0.03",
}


def _small_records():
    records = manifest.build_manifest(TEST, REPO)
    return [r for r in records if r.width == 4 and r.depth <= 2]


class BudgetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = _small_records()[0]
        cls.cache = execution.SolveCache()

    def test_every_probe_structure_fraction_charges_exactly_16384(self) -> None:
        for probe, structure in itertools.product(PRIMARY + ("P1b",), SETTINGS):
            for fraction in (0.05, 0.10, 0.25):
                row = execution.run_row(
                    split=TEST,
                    record=self.record,
                    probe=probe,
                    structure=structure,
                    setting=SETTINGS[structure],
                    parameter_index=0,
                    repeat=0,
                    fraction=fraction,
                    cache=self.cache,
                )
                with self.subTest(probe=probe, structure=structure, fraction=fraction):
                    self.assertEqual(row.total_shots, 16_384)
                    self.assertEqual(sum(c["shots"] for c in row.circuits), 16_384)
                    self.assertEqual(
                        sum(sum(c["counts"].values()) for c in row.circuits), 16_384
                    )

    def test_main_fraction_allocation(self) -> None:
        condition = channels.parse_condition("E0", "0.0")
        entries = execution.entries_for("P1", TEST, self.record, condition)
        shots = execution.allocate("P1", entries, 0.10)
        self.assertEqual(shots["target0"] + shots["target1"], 14_746)
        self.assertEqual(shots["fold3_0"] + shots["fold3_1"], 1_638)
        zero = execution.allocate(
            "P5", execution.entries_for("P5", TEST, self.record, condition), 0.10
        )
        self.assertEqual(zero, {"target0": 8_192, "target1": 8_192})

    def test_e6_schedule_covers_both_halves(self) -> None:
        condition = channels.parse_condition("E6", "0.03")
        for probe in ("P1", "P2", "P3"):
            entries = execution.entries_for(probe, TEST, self.record, condition)
            shots = execution.allocate(probe, entries, 0.10)
            schedule = execution.e6_schedule(
                probe, entries, shots, np.random.default_rng(0)
            )
            for e in entries:
                blocks = {b for lab, b, n in schedule if lab == e.label and n}
                if shots[e.label] >= 2:
                    self.assertTrue(
                        blocks & {0, 1, 2, 3} and blocks & {4, 5, 6, 7},
                        (probe, e.label),
                    )
        entries = execution.entries_for("P4b", TEST, self.record, condition)
        schedule = execution.e6_schedule(
            "P4b", entries, execution.allocate("P4b", entries, 0.10), None
        )
        for lab, block, _ in schedule:
            self.assertIn(
                block, (1, 2, 3, 4, 5, 6) if lab.startswith("target") else (0, 7)
            )


class NoIdealValueTests(unittest.TestCase):
    FORBIDDEN = ("ideal", "truth", "true_gap", "target_reference")

    def test_probe_signatures_accept_no_ideal_value(self) -> None:
        for name, function in inspect.getmembers(probes, inspect.isfunction):
            if function.__module__ != "probes":
                continue
            for parameter in inspect.signature(function).parameters:
                with self.subTest(function=name, parameter=parameter):
                    self.assertFalse(
                        any(word in parameter.lower() for word in self.FORBIDDEN)
                    )

    def _imports(self, module) -> set[str]:
        tree = ast.parse(Path(module.__file__).read_text(encoding="utf-8"))
        names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names |= {a.name for a in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module:
                names.add(node.module)
        return names

    def test_probe_and_execution_modules_never_import_reference(self) -> None:
        self.assertNotIn("reference", self._imports(probes))
        self.assertNotIn("simulate", self._imports(probes))
        self.assertNotIn("reference", self._imports(execution))

    def test_raw_row_contains_no_target_ideal_value(self) -> None:
        record = _small_records()[0]
        row = execution.run_row(
            split=TEST,
            record=record,
            probe="P2",
            structure="E1",
            setting="0.04",
            parameter_index=0,
            repeat=0,
        )
        text = runner.row_json(row).lower()
        self.assertNotIn("ideal", text)
        self.assertIn("twin_reference_gap", text)


class ReproducibilityTests(unittest.TestCase):
    def _row(self, repeat: int) -> dict:
        record = _small_records()[1]
        row = execution.run_row(
            split=TEST,
            record=record,
            probe="P3",
            structure="E3",
            setting="-0.04",
            parameter_index=0,
            repeat=repeat,
        )
        payload = json.loads(runner.row_json(row))
        payload.pop("elapsed_seconds")
        payload.pop("unique_solves")
        return payload

    def test_same_seed_same_row(self) -> None:
        self.assertEqual(self._row(3), self._row(3))

    def test_different_repeat_different_counts(self) -> None:
        self.assertNotEqual(self._row(3)["circuits"], self._row(4)["circuits"])

    def test_e6_row_reproducible(self) -> None:
        record = _small_records()[0]
        rows = [
            runner.row_json(
                execution.run_row(
                    split=TEST,
                    record=record,
                    probe="P1",
                    structure="E6",
                    setting="0.03",
                    parameter_index=7,
                    repeat=1,
                )
            )
            for _ in range(2)
        ]
        a, b = (json.loads(r) for r in rows)
        for payload in (a, b):
            payload.pop("elapsed_seconds")
        self.assertEqual(a, b)


class LockTests(unittest.TestCase):
    def test_runner_refuses_holdout(self) -> None:
        with self.assertRaises(split_guard.LockError):
            runner.preflight("holdout", "anything", True)

    def test_runner_refuses_development_without_owner_confirmation(self) -> None:
        with self.assertRaises(runner.RunRefused):
            runner.preflight("development", "anything", False)

    def test_runner_refuses_development_at_wrong_commit(self) -> None:
        with self.assertRaises(runner.RunRefused):
            runner.preflight("development", "0" * 40, True)

    def test_runner_refuses_development_and_holdout_without_registration(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / "repo"
            shutil.copytree(
                REPO,
                copy,
                ignore=shutil.ignore_patterns(".git", "__pycache__", "results"),
            )
            (copy / split_guard.DEVELOPMENT_REGISTRATION).unlink(missing_ok=True)
            for split in ("development", "holdout"):
                with self.assertRaises(split_guard.LockError):
                    runner.preflight(split, "x", True, repo=copy)

    def test_runner_end_to_end_on_split_99_and_no_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "rows.jsonl"
            args = [
                "--split",
                TEST,
                "--probe",
                "P4a",
                "--structure",
                "E4",
                "--setting",
                "(0.08,0.12)",
                "--parameter-index",
                "6",
                "--repeats",
                "2",
                "--graphs",
                "1",
                "--output",
                str(out),
            ]
            self.assertEqual(runner.main(args), 0)
            rows = [
                json.loads(line)
                for line in out.read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual(len(rows), 2)
            self.assertTrue(
                all(r["total_shots"] == 16_384 and r["split"] == TEST for r in rows)
            )
            with self.assertRaises(FileExistsError):
                runner.main(args)


class CircuitCorrectnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = _small_records()[2]
        cls.targets = execution.target_circuits(
            TEST, cls.record, channels.parse_condition("E0", "0.0")
        )

    def test_compiled_targets_use_only_basis_and_keep_identity_pairs(self) -> None:
        for compiled in self.targets:
            self.assertTrue(
                {op[0] for op in compiled.ops} <= set(circuits.BASIS) | {"barrier"}
            )
        circuits.assert_identity_pairs(
            self.targets[1], self.record.edges[0], self.record.depth
        )

    def test_identity_pairs_do_not_change_the_logical_state(self) -> None:
        plain = [op for op in self.targets[1].ops]
        stripped, skip = [], 0
        for op in plain:
            if skip:
                skip -= 1
                continue
            stripped.append(op)
            if op[0] == "barrier":
                skip = 2
        p_with = simulate.probabilities(self.targets[1])
        p_without = simulate.probabilities(
            circuits.Compiled("t", self.record.width, tuple(stripped))
        )
        np.testing.assert_allclose(p_with, p_without, atol=1e-12)

    def test_fold_frames_are_logically_equivalent_and_twin_is_clifford(self) -> None:
        base = simulate.probabilities(self.targets[0])
        np.testing.assert_allclose(
            simulate.probabilities(circuits.fold(self.targets[0], 3)), base, atol=1e-10
        )
        for row in circuits.frame_rows(self.record.width):
            np.testing.assert_allclose(
                simulate.probabilities(circuits.framed(self.targets[0], row)),
                base,
                atol=1e-10,
            )
        twin = circuits.clifford_twin(self.targets[0])
        for op in twin.ops:
            if op[0] == "rz":
                self.assertAlmostEqual((op[2][0] / (math.pi / 2)) % 1, 0.0, places=12)

    def test_frame_rows_are_strength_two_balanced(self) -> None:
        rows = circuits.frame_rows(8)
        for i, j in itertools.combinations(range(8), 2):
            counts = {(r[i], r[j]) for r in rows}
            self.assertEqual(len(counts), 4)
            for pattern in counts:
                self.assertEqual(sum((r[i], r[j]) == pattern for r in rows), 4)

    def test_nearest_clifford_tie_goes_to_smaller_angle(self) -> None:
        q = math.pi / 2
        self.assertEqual(circuits.nearest_clifford_angle(0.5 * q), 0.0)
        self.assertEqual(circuits.nearest_clifford_angle(0.51 * q), q)
        self.assertEqual(circuits.nearest_clifford_angle(-0.5 * q), -q)

    def test_density_and_state_vector_engines_agree(self) -> None:
        pure = simulate.probabilities(self.targets[0])
        mixed = simulate.probabilities(
            self.targets[0], simulate.GateNoise(depolarizing=1e-300)
        )
        np.testing.assert_allclose(pure, mixed, atol=1e-12)


class ChannelTests(unittest.TestCase):
    def test_uniform_readout_scales_population_gap_by_lambda_squared(self) -> None:
        record = _small_records()[3]
        ref = reference.reference_gap(TEST, record, "E4", "(0.08,0.12)")
        self.assertAlmostEqual(
            ref.noisy_population_gap, 0.64 * ref.ideal_gap, places=12
        )
        self.assertAlmostEqual(ref.harmful_ratio, -0.36, places=10)
        self.assertFalse(ref.flipped)

    def test_e5_prime_preserves_pair_marginals(self) -> None:
        width = 4
        rng = np.random.default_rng(5)
        p = rng.random(16)
        p /= p.sum()
        base = channels.Readout(
            tuple((0.0, 0.0) for _ in range(width)), (0, 1, 2), 0.25, 0.0
        )
        tilted = channels.Readout(base.rates, (0, 1, 2), 0.25, 0.015625)
        a = channels.apply_readout(p, width, base).reshape(2, 2, 2, 2)
        b = channels.apply_readout(p, width, tilted).reshape(2, 2, 2, 2)
        for axes in itertools.combinations(range(4), 2):
            other = tuple(k for k in range(4) if k not in axes)
            np.testing.assert_allclose(a.sum(axis=other), b.sum(axis=other), atol=1e-12)

    def test_p4a_is_exactly_zero_without_readout_error(self) -> None:
        record = _small_records()[0]
        row = execution.run_row(
            split=TEST,
            record=record,
            probe="P4a",
            structure="E1",
            setting="0.04",
            parameter_index=0,
            repeat=0,
        )
        self.assertEqual(row.statistic, 0.0)


if __name__ == "__main__":
    unittest.main()
