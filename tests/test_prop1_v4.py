"""Task 3-3 Proposition-1 pilot, prediction rule and scorer.

Split 99 (software_test) records and synthetic inputs only; splits 30 and 31
are never instantiated here.
"""

from __future__ import annotations

import argparse
import sys
import unittest
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
for sub in (
    "src",
    "experiments/prop1",
    "experiments/holdout",
    "experiments/development",
):
    sys.path.insert(0, str(REPO / sub))

import execution  # noqa: E402
import prop1_v4 as p  # noqa: E402
import score_prop1_v4 as sp  # noqa: E402
from scipy.stats import multivariate_normal as mvn  # noqa: E402

RECORDS = p.records("software_test")


class BudgetTests(unittest.TestCase):
    def test_zne_weights_are_the_ols_intercept(self) -> None:
        x = np.array([[1, 1], [1, 3], [1, 5]], float)
        weights = np.linalg.pinv(x)[0]
        np.testing.assert_allclose(weights, p.WEIGHTS, atol=1e-12)

    def test_total_charged_cost(self) -> None:
        total = (
            p.PILOT_BLOCKS * 2 * p.PILOT_SHOTS + p.SCORING_REPEATS * 2 * p.SCORING_SHOTS
        )
        self.assertEqual(total, 1_310_720)

    def test_block_allocations(self) -> None:
        r = RECORDS[0]
        probs = [[np.full(2**r.width, 2.0**-r.width)] * 3 for _ in range(p.K)]
        for shots in (p.PILOT_SHOTS, p.SCORING_SHOTS):
            counts = p.draw_block(np.random.default_rng(0), probs, r.width, shots)
            raw = sum(sum(counts[f"raw_c{k}"].values()) for k in range(4))
            zne = sum(
                sum(c.values()) for name, c in counts.items() if name.startswith("zne")
            )
            self.assertEqual((raw, zne, len(counts)), (shots, shots, 16))

    def test_header_matches_protocol(self) -> None:
        self.assertEqual(len(p.FIELDS), 20)
        self.assertEqual(p.FIELDS[0], "graph_id")
        self.assertEqual(p.FIELDS[-1], "protocol_sha256")

    def test_candidates(self) -> None:
        c = p.candidates("software_test", RECORDS[0])
        self.assertEqual(len(c), 4)
        self.assertFalse(any(x["identity_pairs"] for x in c))
        self.assertEqual(c, p.candidates("software_test", RECORDS[0]))


class OrthantTests(unittest.TestCase):
    def test_bvn_against_scipy(self) -> None:
        rng = np.random.default_rng(3)
        h, k, r = (
            rng.normal(size=40) * 2,
            rng.normal(size=40) * 2,
            rng.uniform(-0.99, 0.99, 40),
        )
        h[:3] = 0.0
        ref = [
            mvn.cdf([a, b], mean=[0, 0], cov=[[1, c], [c, 1]])
            for a, b, c in zip(h, k, r, strict=True)
        ]
        np.testing.assert_allclose(p.bvn_cdf(h, k, r), ref, atol=1e-12)

    def test_independent_case_is_exact(self) -> None:
        from scipy.special import ndtr

        mu = np.array([[0.3, -0.5, 1.2]])
        cov = np.diag([0.5, 2.0, 1.5])[None]
        value, ok = p.orthant_converged(mu, cov)
        self.assertTrue(ok[0])
        self.assertAlmostEqual(
            value[0], float(np.prod(ndtr(mu[0] / np.sqrt(np.diag(cov[0]))))), places=12
        )

    def test_correlated_against_scipy(self) -> None:
        rng = np.random.default_rng(4)
        a = rng.normal(size=(10, 3, 3))
        cov = a @ a.transpose(0, 2, 1) + 0.05 * np.eye(3)
        mu = rng.normal(size=(10, 3))
        value, ok = p.orthant_converged(mu, cov)
        ref = [mvn.cdf(mu[i], mean=np.zeros(3), cov=cov[i]) for i in range(10)]
        self.assertTrue(ok.all())
        np.testing.assert_allclose(
            value, ref, atol=1e-4
        )  # scipy's QMC default is the looser one


class RuleTests(unittest.TestCase):
    def test_prediction_is_deterministic_and_ideal_free(self) -> None:
        r = RECORDS[0]
        entry = p.pilot_graph(r, execution.SolveCache(), "software_test")
        rb, zb = p.block_estimates(entry, r)
        a = p.predict_graph(r, rb, zb, resamples=500)
        b = p.predict_graph(r, rb, zb, resamples=500)
        self.assertEqual(a, b)
        self.assertIn(
            a["diagnostic_reason"],
            {
                "zne_separated",
                "raw_separated",
                "uncertified_raw_default",
                "unstable_attenuation",
                "unresolved_anchor",
                "numerical_failure",
            },
        )
        self.assertEqual(
            a["prediction"] == "zne", a["diagnostic_reason"] == "zne_separated"
        )
        total = sum(sum(c.values()) for blk in entry["blocks"] for c in blk.values())
        self.assertEqual(total, p.PILOT_BLOCKS * 2 * p.PILOT_SHOTS)

    def test_unresolved_anchor_defaults_raw(self) -> None:
        r = RECORDS[0]
        zne = np.zeros((32, 4)) + np.random.default_rng(0).normal(0, 1e-3, (32, 4))
        out = p.predict_graph(r, zne.copy(), zne, resamples=200)
        self.assertEqual(
            (out["prediction"], out["diagnostic_reason"]), ("raw", "unresolved_anchor")
        )

    def test_selection_errors(self) -> None:
        self.assertEqual(sp.selection_errors(np.array([0.1, 0.3, 0.2, 0.0]), 1), 0)
        self.assertEqual(sp.selection_errors(np.array([0.3, 0.3, 0.2, 0.0]), 1), 1)
        self.assertEqual(sp.selection_errors(np.array([0.1, 0.3, 0.2, 0.0]), None), 1)

    def test_scoring_refused_without_registration(self) -> None:
        if (REPO / p.REGISTRATION).exists():
            self.skipTest("predictions already registered")
        with self.assertRaises(SystemExit):
            sp.check_registration(p.OUT)
        args = argparse.Namespace(out=p.OUT, commit="x")
        with self.assertRaises(SystemExit):
            sp.run(args)


if __name__ == "__main__":
    unittest.main()
