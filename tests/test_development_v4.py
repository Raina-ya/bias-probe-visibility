"""Tests for the v4 development driver.  No development unit is executed here:
work lists are built from software-test records and shards run on split 99."""

from __future__ import annotations

import gzip
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "experiments" / "development"))

import cells_v4  # noqa: E402
import manifest  # noqa: E402
import run_development_v4 as dev  # noqa: E402
import strength_map  # noqa: E402

RECORDS = manifest.build_manifest("software_test", REPO)
CHOSEN = {(s, "main"): grid[-1][0] for s, grid in strength_map.GRIDS.items()}


class WorkListTests(unittest.TestCase):
    def test_counts(self) -> None:
        nulls = dev.null_units(RECORDS)
        mains = dev.main_units(RECORDS, CHOSEN)
        self.assertEqual(len(nulls), 7 * 7 * 50 + 6 * 7 * 50)
        self.assertEqual(len(mains), 7 * 7 * 50)
        self.assertEqual(len(set(nulls)), len(nulls))
        self.assertEqual(len(set(mains)), len(mains))

    def test_matched_null_parameter_index_follows_grid(self) -> None:
        for unit in dev.null_units(RECORDS):
            _, probe, structure, setting, index, _ = unit
            if structure != "E0":
                self.assertEqual(setting, cells_v4.MATCHED_NULL[structure])
                self.assertEqual(index, len(strength_map.GRIDS[structure]))
                self.assertNotEqual(probe, "P0")

    def test_main_uses_chosen_setting(self) -> None:
        for _, _, structure, setting, index, _ in dev.main_units(RECORDS, CHOSEN):
            self.assertEqual(setting, CHOSEN[(structure, "main")])
            self.assertEqual(strength_map.GRIDS[structure][index][0], setting)

    def test_pilot_is_every_hundredth_unit(self) -> None:
        full = dev.null_units(RECORDS) + dev.main_units(RECORDS, CHOSEN)
        pilot = dev.pilot_units(RECORDS, CHOSEN)
        self.assertEqual(len(pilot), len(full[:: dev.PILOT_STRIDE]))
        self.assertEqual(
            [u[1:] for u in pilot], [u[1:] for u in full[:: dev.PILOT_STRIDE]]
        )

    def test_shards_partition_the_work_list(self) -> None:
        units = dev.main_units(RECORDS, CHOSEN)
        parts = [dev.shard(units, k, 7) for k in range(7)]
        self.assertEqual(sorted(u for p in parts for u in p), sorted(units))


class ShardTests(unittest.TestCase):
    def test_shard_is_written_once_with_all_repeats(self) -> None:
        record = [r for r in RECORDS if r.width == 4][0]
        units = [("main", "P4a", "E4", "(0.08,0.12)", 7, record.graph_id)]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "s.jsonl.gz"
            summary = dev.write_shard(
                path,
                units,
                {record.graph_id: record},
                "test",
                "x",
                split="software_test",
            )
            self.assertEqual((summary["units"], summary["failed"]), (1, 0))
            with gzip.open(path, "rt", encoding="utf-8") as h:
                entry = json.loads(h.readline())
            self.assertEqual(len(entry["rows"]), dev.REPEATS)
            self.assertTrue(
                all(
                    r["total_shots"] == 16384 and r["split"] == "software_test"
                    for r in entry["rows"]
                )
            )
            with self.assertRaises(FileExistsError):
                dev.write_shard(
                    path,
                    units,
                    {record.graph_id: record},
                    "test",
                    "x",
                    split="software_test",
                )

    def test_failed_unit_is_kept(self) -> None:
        record = [r for r in RECORDS if r.width == 4][0]
        units = [("main", "P4a", "E4", "not-a-setting", 0, record.graph_id)]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "s.jsonl.gz"
            summary = dev.write_shard(
                path,
                units,
                {record.graph_id: record},
                "test",
                "x",
                split="software_test",
            )
            self.assertEqual(summary["failed"], 1)
            with gzip.open(path, "rt", encoding="utf-8") as h:
                entry = json.loads(h.readline())
            self.assertEqual(entry["status"], "failed")
            self.assertIn("Traceback", entry["error"])


class RefusalTests(unittest.TestCase):
    def test_refuses_without_previous_project_confirmation(self) -> None:
        self.assertEqual(dev.main(["plan", "--commit", "0" * 40]), 2)

    def test_refuses_at_wrong_commit(self) -> None:
        self.assertEqual(
            dev.main(["plan", "--commit", "0" * 40, "--previous-project-closed"]), 2
        )

    def test_driver_never_mentions_holdout_split(self) -> None:
        text = (
            REPO / "experiments" / "development" / "run_development_v4.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn('"holdout"', text)
        self.assertEqual(dev.SPLIT, "development")


if __name__ == "__main__":
    unittest.main()
