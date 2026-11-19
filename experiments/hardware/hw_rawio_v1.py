"""Immutable record storage for the hardware readout amendment v1.

Every record is a JSON file written once with exclusive create (``open(..., "x")``),
LF line endings and sorted keys, then listed in ``index.jsonl`` with its
canonical SHA-256.  Append-only logs (``submissions.jsonl``, ``index.jsonl``)
are opened in append mode and flushed to disk after each line.  Nothing here
overwrites or deletes a file; ``verify_index`` detects a changed, missing or
unindexed record.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

INDEX = "index.jsonl"


def canonical_sha256(path: Path) -> str:
    """SHA-256 of the file with CRLF/CR normalised to LF (as src/hashing.py)."""

    data = Path(path).read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _dump(payload: dict) -> str:
    return json.dumps(payload, indent=1, sort_keys=True, ensure_ascii=True) + "\n"


def append_line(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as h:
        h.write(json.dumps(payload, sort_keys=True, ensure_ascii=True) + "\n")
        h.flush()
        os.fsync(h.fileno())


def read_lines(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def write_record(root: Path, relpath: str, payload: dict, clock=utc_now) -> str:
    """Write ``root/relpath`` once and index it; return its canonical SHA-256."""

    root = Path(root)
    path = root / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as h:
        h.write(_dump(payload))
        h.flush()
        os.fsync(h.fileno())
    digest = canonical_sha256(path)
    append_line(root / INDEX, {"file": relpath, "sha256": digest, "written_utc": clock()})
    return digest


def read_record(root: Path, relpath: str) -> dict:
    return json.loads((Path(root) / relpath).read_text(encoding="utf-8"))


def verify_index(root: Path) -> list[str]:
    """Return problems: changed, missing, duplicated or unindexed records."""

    root = Path(root)
    problems: list[str] = []
    seen: set[str] = set()
    for entry in read_lines(root / INDEX):
        rel = entry["file"]
        if rel in seen:
            problems.append(f"indexed twice: {rel}")
        seen.add(rel)
        path = root / rel
        if not path.is_file():
            problems.append(f"missing: {rel}")
        elif canonical_sha256(path) != entry["sha256"]:
            problems.append(f"changed: {rel}")
    for path in root.rglob("*.json"):
        rel = path.relative_to(root).as_posix()
        if rel not in seen:
            problems.append(f"unindexed: {rel}")
    return problems
