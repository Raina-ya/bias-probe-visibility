from __future__ import annotations

import hashlib
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
PROTOCOL = REPO / "docs" / "freeze" / "frozen_protocol_v2.md"
SCHEDULE = REPO / "docs" / "inventory_20_step4_schedule.md"
PROTOCOL_HASH = REPO / "docs" / "freeze" / "frozen_protocol_v2.sha256"


class ProtocolV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = PROTOCOL.read_text(encoding="utf-8")
        cls.normalized = " ".join(cls.text.split())
        cls.schedule = SCHEDULE.read_text(encoding="utf-8")

    def test_protocol_is_self_contained_candidate(self) -> None:
        self.assertIn("only normative protocol for v2", self.text)
        self.assertIn(
            "No noisy development simulation is authorized", self.normalized
        )
        self.assertNotIn("All other probe statistics remain as in v1", self.text)
        self.assertNotIn("Every v1 rule not mentioned here remains unchanged", self.text)

    def test_repaired_matrix_contract_is_embedded(self) -> None:
        self.assertIn(
            "7a8e3a56e6f48d8a29c3643c1c2e24f46bce6a54c674d6b1937dbdcd041d8995",
            self.text,
        )
        self.assertIn("committed as `c839b95`", self.text)
        self.assertIn("35 blind, 15 partial, and 6 visible", self.normalized)
        self.assertNotIn("2148b957", self.text)
        self.assertNotIn("30 blind, 20 partial", self.text)

    def test_repaired_operational_rules_are_present(self) -> None:
        required = (
            "max(T_marg,T_corr)",
            "bitwise_not(z)",
            "A confidently wrong winner remains blind",
            "eight equal temporal blocks",
            "design-distribution visibility",
            "strength_map_v2.csv",
            "confirmatory_lock_v2.json",
            "10,000 stratified graph-cluster bootstrap",
            "B(D_P)=+infinity",
            "For P0 and P5, test `f=0`",
        )
        for phrase in required:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.normalized)

    def test_resource_and_hardware_limits_are_present(self) -> None:
        required = (
            "deterministic conservative upper-bound dry run",
            "1,231,200 unique cached circuit/channel probability solves",
            "16,389,242,880 projected uncompressed raw bytes",
            "20 GiB raw output",
            "at most 360 seconds",
            "Fewer than 100 shots per circuit is no-go",
        )
        for phrase in required:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.normalized)

    def test_confirmatory_seed_remains_locked(self) -> None:
        self.assertIn(
            "Only after this second lock may split 20 be instantiated",
            self.normalized,
        )
        self.assertIn("The holdout is read once", self.normalized)

    def test_future_schedule_uses_v2_lock(self) -> None:
        self.assertNotIn("docs/freeze/frozen_protocol_v1.md", self.schedule)
        self.assertNotIn("docs/dev/thresholds_v1.md", self.schedule)
        self.assertIn("docs/freeze/frozen_protocol_v2.md", self.schedule)
        self.assertIn("docs/freeze/confirmatory_lock_v2.json", self.schedule)
        self.assertIn(
            "complete section-10.1 implementation have been committed and "
            "independently timestamped",
            " ".join(self.schedule.split()),
        )

    def test_protocol_hash_sidecar_matches_exact_bytes(self) -> None:
        expected = PROTOCOL_HASH.read_text(encoding="ascii").split()[0]
        actual = hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
