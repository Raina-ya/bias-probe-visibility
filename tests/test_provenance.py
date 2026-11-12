from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

import provenance  # noqa: E402


class ProvenanceTests(unittest.TestCase):
    def test_registered_artifacts_and_generators_verify(self) -> None:
        registry = provenance.load_registry(REPO)
        self.assertEqual(provenance.check(REPO, registry), [])


if __name__ == "__main__":
    unittest.main()

