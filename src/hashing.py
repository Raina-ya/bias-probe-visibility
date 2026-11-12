"""Line-ending-independent content hashes.

Text artifacts are hashed after converting CRLF and lone CR to LF, so the same
logical file has one hash on Windows and Linux.  Binary artifacts are hashed
byte for byte.  This normalization never changes file contents on disk.
"""

from __future__ import annotations

import hashlib
from pathlib import Path


TEXT_SUFFIXES = frozenset(
    {
        ".csv",
        ".json",
        ".md",
        ".py",
        ".sha256",
        ".tex",
        ".bib",
        ".txt",
        ".yaml",
        ".yml",
    }
)


def is_text_artifact(path: Path) -> bool:
    return path.suffix.lower() in TEXT_SUFFIXES


def canonical_bytes(path: Path) -> bytes:
    data = path.read_bytes()
    if is_text_artifact(path):
        data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return data


def canonical_sha256(path: Path) -> str:
    return hashlib.sha256(canonical_bytes(path)).hexdigest()
