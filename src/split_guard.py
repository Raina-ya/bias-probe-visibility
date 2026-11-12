"""Refuse to instantiate locked seed splits.

Protocol v3, Sections 9--10.  Split 10 (development) needs the pre-development
lock: the reviewed protocol, matrix, and freeze artifacts must match the hashes
recorded in an owner-written registration record that carries an independent
OSF or AsPredicted timestamp.  Splits 20 and 31 additionally need the
confirmatory lock and refuse a second successful run.  Split 99 is a software
test namespace that never produces reported results.

This module only checks files.  It never creates a registration record; the
project owner writes that file after registering.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Iterable

sys.path.insert(0, str(Path(__file__).resolve().parent))

from hashing import canonical_sha256  # noqa: E402


PROTOCOL = Path("docs/freeze/frozen_protocol_v3.md")
PROTOCOL_HASH_FILE = Path("docs/freeze/frozen_protocol_v3.sha256")
MATRIX = Path("docs/theory/06_matrix.csv")
DEVELOPMENT_REGISTRATION = Path("docs/freeze/registration_v3.json")
CONFIRMATORY_LOCK = Path("docs/freeze/confirmatory_lock_v3.json")
CONFIRMATORY_REGISTRATION = Path("docs/freeze/registration_confirmatory_v3.json")
RUN_MARKER_DIR = Path("results/run_markers")

ALLOWED_REGISTRIES = frozenset({"OSF", "AsPredicted"})
REQUIRED_REGISTRATION_FIELDS = (
    "registry",
    "url",
    "timestamp_utc",
    "commit",
    "files",
)

# Files whose hashes the pre-development registration record must list.
PRE_DEVELOPMENT_FILES = (
    "docs/freeze/frozen_protocol_v3.md",
    "docs/theory/06_matrix.csv",
    "artifact_registry_v1.yaml",
    "src/hashing.py",
    "src/protocol_contract.py",
    "src/split_guard.py",
    "src/manifest.py",
    "src/strength_map.py",
    "src/alarm_calibration.py",
    "src/analysis.py",
    "tests/test_freeze_v3.py",
    "tests/test_protocol_v3.py",
)

SOFTWARE_TEST = "software_test"
DEVELOPMENT = "development"
CONFIRMATORY = frozenset({"holdout", "prop1_scoring"})
UNLOCKED_ONLY_AFTER_DEVELOPMENT = frozenset({"prop1_pilot"})
SINGLE_RUN = frozenset({"holdout", "prop1_scoring"})


class LockError(PermissionError):
    """Raised when a split may not be instantiated."""


def _read_registration(repo: Path, relative: Path) -> dict[str, object]:
    path = repo / relative
    if not path.is_file():
        raise LockError(f"missing owner registration record: {relative.as_posix()}")
    record = json.loads(path.read_text(encoding="utf-8"))
    missing = [field for field in REQUIRED_REGISTRATION_FIELDS if not record.get(field)]
    if missing:
        raise LockError(f"registration record lacks fields: {missing}")
    if record["registry"] not in ALLOWED_REGISTRIES:
        raise LockError(f"registry must be one of {sorted(ALLOWED_REGISTRIES)}")
    if not isinstance(record["files"], dict):
        raise LockError("registration 'files' must map path to SHA-256")
    return record


def _check_hashes(
    repo: Path, record: dict[str, object], required: Iterable[str]
) -> None:
    files: dict[str, str] = record["files"]  # type: ignore[assignment]
    errors: list[str] = []
    for relative in required:
        if relative not in files:
            errors.append(f"not registered: {relative}")
            continue
        path = repo / relative
        if not path.is_file():
            errors.append(f"missing: {relative}")
        elif canonical_sha256(path) != files[relative]:
            errors.append(f"changed since registration: {relative}")
    if errors:
        raise LockError("; ".join(errors))


def check_protocol_hash_file(repo: Path) -> None:
    recorded = (repo / PROTOCOL_HASH_FILE).read_text(encoding="utf-8").split()[0]
    actual = canonical_sha256(repo / PROTOCOL)
    if recorded != actual:
        raise LockError(
            f"protocol hash file {recorded} does not match protocol {actual}"
        )


def require_development_lock(repo: Path) -> dict[str, object]:
    check_protocol_hash_file(repo)
    record = _read_registration(repo, DEVELOPMENT_REGISTRATION)
    _check_hashes(repo, record, PRE_DEVELOPMENT_FILES)
    return record


def require_confirmatory_lock(repo: Path) -> dict[str, object]:
    require_development_lock(repo)
    if not (repo / CONFIRMATORY_LOCK).is_file():
        raise LockError(f"missing confirmatory lock: {CONFIRMATORY_LOCK.as_posix()}")
    record = _read_registration(repo, CONFIRMATORY_REGISTRATION)
    _check_hashes(repo, record, (CONFIRMATORY_LOCK.as_posix(),))
    return record


def require_split(repo: Path, split: str) -> None:
    """Raise ``LockError`` unless ``split`` may be instantiated now."""

    if split == SOFTWARE_TEST:
        return
    if split == DEVELOPMENT:
        require_development_lock(repo)
        return
    if split in CONFIRMATORY or split in UNLOCKED_ONLY_AFTER_DEVELOPMENT:
        require_confirmatory_lock(repo)
        if split in SINGLE_RUN and marker_path(repo, split).exists():
            raise LockError(f"{split} already has a successful run; refusing a rerun")
        return
    raise LockError(f"unknown or unsupported split: {split}")


def marker_path(repo: Path, split: str) -> Path:
    return repo / RUN_MARKER_DIR / f"{split}.success"


def record_successful_run(repo: Path, split: str, summary: str) -> Path:
    """Create the single-run marker; fails if it already exists."""

    if split not in SINGLE_RUN:
        raise ValueError(f"{split} is not a single-run split")
    path = marker_path(repo, split)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        handle.write(summary.rstrip("\n") + "\n")
    return path
