"""Split locks for protocol v4 (Section 10).

v3's ``split_guard.py`` and its registration stay unchanged as the v3 record;
v4 uses its own protocol, registration record, and file list.  Split 99 is the
software-test namespace and is always allowed.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import split_guard as v3  # noqa: E402
from hashing import canonical_sha256  # noqa: E402

LockError = v3.LockError

PROTOCOL = Path("docs/freeze/frozen_protocol_v4.md")
PROTOCOL_HASH_FILE = Path("docs/freeze/frozen_protocol_v4.sha256")
DEVELOPMENT_REGISTRATION = Path("docs/freeze/registration_v4.json")
CONFIRMATORY_LOCK = Path("docs/freeze/confirmatory_lock_v4.json")
CONFIRMATORY_REGISTRATION = Path("docs/freeze/registration_confirmatory_v4.json")

PRE_DEVELOPMENT_FILES_V4 = (
    "docs/freeze/frozen_protocol_v4.md",
    "docs/theory/06_matrix_v4.csv",
    "docs/freeze/pre_data_defect_audit_v3.md",
    "artifact_registry_v1.yaml",
    "artifact_registry_v4.yaml",
    "src/provenance.py",
    "src/provenance_v4.py",
    "src/hashing.py",
    "src/protocol_contract.py",
    "src/manifest.py",
    "src/manifest_v4.py",
    "src/split_guard.py",
    "src/split_guard_v4.py",
    "src/circuits.py",
    "src/simulate.py",
    "src/channels.py",
    "src/probes.py",
    "src/execution.py",
    "src/reference.py",
    "src/cells_v4.py",
    "src/strength_map.py",
    "src/alarm_calibration.py",
    "src/analysis.py",
    "src/analysis_v4.py",
    "src/runner.py",
    "tests/conftest.py",
    "tests/test_design_checks.py",
    "tests/test_execution.py",
    "tests/test_freeze_v3.py",
    "tests/test_power_analysis_v4.py",
    "tests/test_protocol_contract.py",
    "tests/test_protocol_v2.py",
    "tests/test_protocol_v3.py",
    "tests/test_provenance.py",
    "tests/test_registration_state.py",
    "tests/test_v4.py",
    "docs/freeze/power_analysis_v5.md",
    "docs/part2/execution_contract_v4.md",
    "experiments/audit/p0_unresolved_audit.py",
    "experiments/audit/p4_construction_audit.py",
    "experiments/semantic/semantic_tests_v4.py",
    "experiments/semantic/semantic_tests_v4.csv",
    "experiments/semantic/semantic_tests_v4_first_pass.csv",
    "experiments/power/decision_design_inputs_v5.py",
    "experiments/power/decision_design_inputs_v5.csv",
    "experiments/power/run_power_analysis_v5.py",
    "experiments/power/power_analysis_summary_v5.csv",
)

SOFTWARE_TEST = v3.SOFTWARE_TEST
DEVELOPMENT = v3.DEVELOPMENT
CONFIRMATORY = v3.CONFIRMATORY
SINGLE_RUN = v3.SINGLE_RUN


def check_protocol_hash_file(repo: Path) -> None:
    recorded = (repo / PROTOCOL_HASH_FILE).read_text(encoding="utf-8").split()[0]
    actual = canonical_sha256(repo / PROTOCOL)
    if recorded != actual:
        raise LockError(
            f"v4 protocol hash file {recorded} does not match protocol {actual}"
        )


def require_development_lock(repo: Path) -> dict:
    check_protocol_hash_file(repo)
    record = v3._read_registration(repo, DEVELOPMENT_REGISTRATION)
    v3._check_hashes(repo, record, PRE_DEVELOPMENT_FILES_V4)
    return record


def require_confirmatory_lock(repo: Path) -> dict:
    require_development_lock(repo)
    if not (repo / CONFIRMATORY_LOCK).is_file():
        raise LockError(f"missing confirmatory lock: {CONFIRMATORY_LOCK.as_posix()}")
    record = v3._read_registration(repo, CONFIRMATORY_REGISTRATION)
    v3._check_hashes(repo, record, (CONFIRMATORY_LOCK.as_posix(),))
    return record


def marker_path(repo: Path, split: str) -> Path:
    return repo / "results" / "run_markers_v4" / f"{split}.success"


def require_split(repo: Path, split: str) -> None:
    if split == SOFTWARE_TEST:
        return
    if split == DEVELOPMENT:
        require_development_lock(repo)
        return
    if split in CONFIRMATORY or split == "prop1_pilot":
        require_confirmatory_lock(repo)
        if split in SINGLE_RUN and marker_path(repo, split).exists():
            raise LockError(
                f"{split} already has a successful v4 run; refusing a rerun"
            )
        return
    raise LockError(f"unknown or unsupported split: {split}")
