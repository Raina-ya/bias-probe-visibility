"""Contract tests for the protocol v3 freeze candidate."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

import hashing  # noqa: E402

PROTOCOL = REPO / "docs" / "freeze" / "frozen_protocol_v3.md"
SIDECAR = REPO / "docs" / "freeze" / "frozen_protocol_v3.sha256"
MATRIX_SHA256 = "7a8e3a56e6f48d8a29c3643c1c2e24f46bce6a54c674d6b1937dbdcd041d8995"


class ProtocolV3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = PROTOCOL.read_text(encoding="utf-8")

    def test_sidecar_matches_lf_normalized_hash(self) -> None:
        recorded = SIDECAR.read_text(encoding="ascii").split()[0]
        self.assertEqual(hashing.canonical_sha256(PROTOCOL), recorded)

    def test_all_sections_present_in_order(self) -> None:
        positions = [self.text.index(f"\n## {n}. ") for n in range(1, 19)]
        self.assertEqual(positions, sorted(positions))

    def test_matrix_hash_and_counts_unchanged(self) -> None:
        self.assertIn(MATRIX_SHA256, self.text)
        self.assertIn("35 blind, 15 partial, and\n6 visible", self.text)

    def test_median_ratio_target_is_gone(self) -> None:
        self.assertNotIn("Main design ratio", self.text)
        self.assertNotIn("declared unattainable before holdout", self.text)
        self.assertIn("Largest frozen strength", self.text)

    def test_budget_and_sample_size_unchanged(self) -> None:
        for fragment in ("N=16,384", "100 independently generated graph", "32 repeats"):
            self.assertIn(fragment, self.text)

    def test_v2_retained_unchanged_for_audit(self) -> None:
        v2 = REPO / "docs" / "freeze" / "frozen_protocol_v2.md"
        recorded = (
            (REPO / "docs" / "freeze" / "frozen_protocol_v2.sha256")
            .read_text()
            .split()[0]
        )
        self.assertEqual(hashing.canonical_sha256(v2), recorded)

    def test_e7_is_not_in_the_main_run(self) -> None:
        self.assertIn("E7 (fake backend) stays exploratory", self.text)


if __name__ == "__main__":
    unittest.main()
