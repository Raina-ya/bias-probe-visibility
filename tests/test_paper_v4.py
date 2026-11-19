"""Claim-ledger checks for the final manuscript paper/main_v4.tex."""

from __future__ import annotations

import csv
import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "experiments" / "synthesis"))

import hw_paper_v4_1 as hw_numbers  # noqa: E402
import paper_numbers_v4 as numbers  # noqa: E402

TEX = REPO / "paper" / "main_v4.tex"
NUMBERS = REPO / "paper" / "numbers_v4.tex"
HW_NUMBERS = REPO / "paper" / "numbers_hw_v4_1.tex"


class PaperLedger(unittest.TestCase):
    def test_numbers_file_matches_results(self) -> None:
        expected = {k: v for k, (v, _) in numbers.numbers().items()}
        found = dict(
            re.findall(
                r"\\newcommand\{\\num(\w+'?)\}\{([^}]*)\}",
                NUMBERS.read_text(encoding="utf-8"),
            )
        )
        self.assertEqual(found, expected)

    def test_hardware_numbers_match_records(self) -> None:
        expected = {k: v for k, (v, _) in hw_numbers.numbers().items()}
        found = dict(re.findall(r"\\newcommand\{\\num(\w+)\}\{([^}]*)\}",
                                HW_NUMBERS.read_text(encoding="utf-8")))
        self.assertEqual(found, expected)

    def test_hardware_figure_matches_records(self) -> None:
        figure = (REPO / "paper" / "hw_figure_v4_1.tex").read_text(encoding="utf-8")
        self.assertEqual(figure, hw_numbers.figure(hw_numbers.load()))

    def test_hardware_macros_do_not_collide(self) -> None:
        self.assertEqual(set(numbers.numbers()) & set(hw_numbers.numbers()), set())

    def test_every_macro_used_is_defined(self) -> None:
        used = set(re.findall(r"\\num([A-Za-z]+)", TEX.read_text(encoding="utf-8")))
        defined = set(numbers.numbers()) | set(hw_numbers.numbers())
        self.assertEqual(used - defined, set())

    def test_citations_are_in_bib_and_verified(self) -> None:
        text = TEX.read_text(encoding="utf-8")
        keys = {
            k.strip()
            for group in re.findall(r"\\cite\{([^}]*)\}", text)
            for k in group.split(",")
        }
        bib = set(
            re.findall(
                r"@\w+\{([^,]+),",
                (REPO / "paper" / "references.bib").read_text(encoding="utf-8"),
            )
        )
        self.assertEqual(keys - bib, set())
        with (REPO / "docs" / "literature" / "library.csv").open(
            encoding="utf-8-sig", newline=""
        ) as h:
            status = {r["key"]: r["status"] for r in csv.DictReader(h)}
        allowed = {"verified", "verified-preprint", "verified (previous project)"}
        self.assertEqual({k for k in keys if status.get(k) not in allowed}, set())

    def test_required_method_and_limit_citations(self) -> None:
        """QEM cost bounds, the Wilson interval and the cluster bootstrap are cited."""

        text = TEX.read_text(encoding="utf-8")
        keys = {
            k.strip()
            for group in re.findall(r"\\cite\{([^}]*)\}", text)
            for k in group.split(",")
        }
        required = {
            "takagi2022", "takagi2023", "tsubouchi2023", "quek2024",
            "wilson1927", "field2007",
        }
        self.assertEqual(required - keys, set())

    def test_no_draft_markers(self) -> None:
        text = TEX.read_text(encoding="utf-8")
        for marker in ("TODO", "Pre-results", "Affiliation"):
            self.assertNotIn(marker, text)


if __name__ == "__main__":
    unittest.main()
