"""Checks for the hardware readout power-check statistics (split 99 planning only)."""

import importlib.util
import math
from pathlib import Path

import numpy as np
import pytest

_PATH = Path(__file__).resolve().parents[1] / "experiments" / "hardware" / "readout_power_v1.py"
_spec = importlib.util.spec_from_file_location("readout_power_v1", _PATH)
rp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rp)


def test_fisher_matches_lady_tasting_tea():
    # Fisher's 4-of-8 design, table [[3,1],[1,3]]: two-sided p = 34/70.
    assert rp.fisher_two_sided(3, 1, 1, 3) == pytest.approx(34 / 70, abs=1e-12)


def test_fisher_extreme_table():
    # [[4,0],[0,4]]: two-sided p = 2/70.
    assert rp.fisher_two_sided(4, 0, 0, 4) == pytest.approx(2 / 70, abs=1e-12)


def test_fisher_degenerate_margin_is_one():
    assert rp.fisher_two_sided(100, 0, 0, 0) == 1.0


@pytest.mark.parametrize("qi,qj", [(0.01, 0.01), (0.02, 0.05), (0.1, 0.1)])
def test_cstar_equalises_raw_and_independent_model_error(qi, qj):
    c = rp.c_star(qi, qj)
    assert 0 < c <= rp.c_max(qi, qj)
    r = rp.r_ind(qi, qj) - 2 * c
    raw = 2 * r
    mitigated = abs(1 - (1 - 2 * r) / (1 - 2 * rp.r_ind(qi, qj)))
    assert raw == pytest.approx(mitigated, rel=1e-12)


def test_negative_covariance_never_makes_independent_model_worse():
    q = 0.02
    for c in np.linspace(-rp.c_max(q, q) * 0.999, 0, 50):
        r = rp.r_ind(q, q) - 2 * c
        mitigated = abs(1 - (1 - 2 * r) / (1 - 2 * rp.r_ind(q, q)))
        assert mitigated <= 2 * r + 1e-15


def test_e5_grid_is_below_relevance_threshold():
    # Protocol v4 E5: marginal 0.10, |tau| <= 0.01.
    assert 0.01 < rp.c_star(0.10, 0.10) / 3


def test_joint_has_requested_marginals_and_covariance():
    p = rp.joint(0.02, 0.05, 0.003)
    qi, qj, c = rp.estimates(p[None, :] * 1.0)
    assert (qi[0], qj[0], c[0]) == pytest.approx((0.02, 0.05, 0.003), abs=1e-15)


def test_relevance_bootstrap_rarely_rejects_at_boundary():
    rng = np.random.default_rng(np.random.SeedSequence([rp.ROOT_SEED, 99, 6, 5, 40, 8, 0, 9, 9, 9, 9]))
    q, s = 0.02, 3000
    tables = rng.multinomial(s, rp.joint(q, q, rp.c_star(q, q)), size=200)
    p = np.array([rp.relevance_p(t, rng, 499) for t in tables])
    assert (p <= 0.05).mean() <= 0.10


def test_level_is_holm_first_step():
    assert rp.M_TESTS == 2 * math.comb(8, 2) == 56
    assert rp.LEVEL == pytest.approx(0.05 / 56)


def test_seed_streams_are_distinct():
    a = rp.stream(0, 0, 0, 0).integers(0, 2**63, 4)
    b = rp.stream(0, 0, 0, 1).integers(0, 2**63, 4)
    assert not np.array_equal(a, b)
