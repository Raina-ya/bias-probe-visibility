"""Post-registration state of protocol v4 (OSF registration r63vn)."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

import hashing  # noqa: E402
import runner  # noqa: E402
import split_guard  # noqa: E402
import split_guard_v4  # noqa: E402

RECORD = REPO / split_guard_v4.DEVELOPMENT_REGISTRATION


class RegistrationStateV4Tests(unittest.TestCase):
    def test_record_names_the_registration(self) -> None:
        record = json.loads(RECORD.read_text(encoding="utf-8"))
        self.assertEqual(record["registry"], "OSF")
        self.assertEqual(record["url"], "https://osf.io/r63vn/")
        self.assertEqual(record["timestamp_utc"], "2026-11-13T01:45:49Z")
        self.assertEqual(record["commit"], "e3908dbdc9e73b3f5269195bf1839d74756e32e8")
        self.assertEqual(
            record["supersedes"], "OSF j67wy (protocol v3, commit e8b5300)"
        )

    def test_record_files_match_template_and_lock_list(self) -> None:
        record = json.loads(RECORD.read_text(encoding="utf-8"))
        template = json.loads(
            (REPO / "docs/freeze/registration_v4.template.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(record["files"], template["files"])
        self.assertEqual(
            set(record["files"]), set(split_guard_v4.PRE_DEVELOPMENT_FILES_V4)
        )

    def test_every_registered_file_is_unchanged(self) -> None:
        record = json.loads(RECORD.read_text(encoding="utf-8"))
        for relative, digest in record["files"].items():
            self.assertEqual(
                hashing.canonical_sha256(REPO / relative), digest, relative
            )

    def test_development_admitted_and_confirmatory_splits_state_aware(self) -> None:
        # Implementation error 3: confirmatory splits are refused only until the
        # confirmatory registration record exists.
        split_guard_v4.require_split(REPO, "development")
        if not (REPO / split_guard_v4.CONFIRMATORY_REGISTRATION).exists():
            for split in ("holdout", "prop1_pilot", "prop1_scoring"):
                with self.assertRaises(split_guard_v4.LockError):
                    split_guard_v4.require_split(REPO, split)
        else:
            split_guard_v4.require_confirmatory_lock(REPO)

    def test_runner_still_requires_previous_project_closure_and_clean_commit(
        self,
    ) -> None:
        with self.assertRaises(runner.RunRefused):
            runner.preflight("development", "0" * 40, False)
        with self.assertRaises(runner.RunRefused):
            runner.preflight("development", "0" * 40, True)

    def test_confirmatory_lock_state(self) -> None:
        # State-aware (implementation error 3): before the lock exists, no
        # confirmatory registration may exist either; once it exists, it must
        # record split-20 non-instantiation and every hashed product unchanged.
        lock_path = REPO / split_guard_v4.CONFIRMATORY_LOCK
        registration = REPO / split_guard_v4.CONFIRMATORY_REGISTRATION
        if not lock_path.exists():
            self.assertFalse(registration.exists())
            return
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
        self.assertTrue(lock["split_20_evidence"]["split_20_never_instantiated"])
        for item in lock["products"].values():
            self.assertEqual(
                hashing.canonical_sha256(REPO / item["path"]),
                item["sha256"],
                item["path"],
            )

    def test_v3_record_unchanged(self) -> None:
        split_guard.require_development_lock(REPO)


if __name__ == "__main__":
    unittest.main()
