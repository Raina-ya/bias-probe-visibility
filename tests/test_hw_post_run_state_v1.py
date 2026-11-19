"""Post-run state of the registered hardware readout run (OSF wh5rs).

Replaces the pre-run assertion of
tests/test_hw_readout_v1.py::test_real_mode_refuses_without_registration
once the run exists (docs/hardware/implementation_error_log_hw_v1.md, entry 1).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "experiments" / "hardware"))

import hw_dry_run_v1 as hd  # noqa: E402
import hw_rawio_v1 as rio  # noqa: E402
import hw_runner_v1 as hr  # noqa: E402

RUN = REPO / hr.REAL_OUT
pytestmark = pytest.mark.skipif(not (RUN / "markers" / "main.success").exists(),
                                reason="hardware run not present")


def _snapshot() -> list[tuple[str, str]]:
    return sorted((p.relative_to(RUN).as_posix(), rio.canonical_sha256(p))
                  for p in RUN.rglob("*") if p.is_file())


def test_all_stages_succeeded_and_records_intact():
    for stage in hr.STAGES:
        assert (RUN / "markers" / f"{stage}.success").is_file()
    assert rio.verify_index(RUN) == []
    assert not list((RUN / "raw").glob("*_failed.json"))


def test_any_new_real_run_is_refused_and_writes_nothing():
    before = _snapshot()
    ctx = hr.Context(repo=REPO, out=RUN, adapter=hd.FakeAdapter("null"), real=True,
                     today=hd.FAKE_DATE, clock=hd.fixed_clock, inputs=hd.inputs())
    for stage in (hr.preflight, hr.pilot, hr.allocate, hr.main_stage):
        with pytest.raises(hr.Refused):
            stage(ctx)
    assert _snapshot() == before


def test_reported_seconds_within_cap():
    import json

    used = sum(float(json.loads(p.read_text())["usage_seconds"])
               for p in (RUN / "raw").glob("*_job*.json"))
    assert used <= hr.CAP_SECONDS
