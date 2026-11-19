"""Cross-platform check of the committed hardware dry run (replaces byte identity on Windows).

The registered test tests/test_hw_readout_v1.py::test_committed_dry_run_reproduces
requires the dry-run summary to be byte-identical to the Linux-produced one.  On
Windows one analysis-file hash differs (docs/hardware/implementation_error_log_hw_v1.md,
entry 2).  This test reruns the dry run on any platform and compares it with the
committed outputs field by field: every non-float value exactly (decisions,
rejections, shots, selected qubits, raw-record hashes), every float to a relative
tolerance of 1e-9.  On a mismatch it reports the differing fields.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "experiments" / "hardware"))

import hw_analysis_v1 as ha  # noqa: E402
import hw_dry_run_v1 as hd  # noqa: E402

DRY = REPO / "experiments" / "hardware" / "dry_run"
REL_TOL = 1e-9


def differences(a, b, path="") -> list[str]:
    if isinstance(a, dict) and isinstance(b, dict):
        out = [f"{path}: keys {sorted(set(a) ^ set(b))}"] if set(a) != set(b) else []
        for k in sorted(set(a) & set(b)):
            out += differences(a[k], b[k], f"{path}.{k}")
        return out
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [f"{path}: length {len(a)} != {len(b)}"]
        return [d for i, (x, y) in enumerate(zip(a, b)) for d in differences(x, y, f"{path}[{i}]")]
    if isinstance(a, float) and isinstance(b, float):
        ok = math.isclose(a, b, rel_tol=REL_TOL, abs_tol=1e-300)
        return [] if ok else [f"{path}: {a!r} != {b!r}"]
    return [] if a == b else [f"{path}: {a!r} != {b!r}"]


@pytest.mark.skipif(np.__version__ != "2.3.4", reason="dry-run random streams are for NumPy 2.3.4")
def test_dry_run_matches_committed_outputs_field_by_field(tmp_path):
    fresh = hd.run(REPO, tmp_path / "dry")
    committed = json.loads((DRY / "dry_run_v1_summary.json").read_text(encoding="utf-8"))
    for scenario in hd.SCENARIOS:
        fresh["scenarios"][scenario].pop("analysis_sha256")
        committed["scenarios"][scenario].pop("analysis_sha256")
    problems = differences(fresh, committed, "summary")
    for scenario in hd.SCENARIOS:
        name = f"{scenario}_analysis/{ha.OUTPUTS[0]}"
        problems += differences(
            json.loads((tmp_path / "dry" / name).read_text(encoding="utf-8")),
            json.loads((DRY / name).read_text(encoding="utf-8")),
            name,
        )
    assert problems == [], "\n".join(problems[:40])
