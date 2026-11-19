"""Write or check docs/hardware/package_manifest_v1.json (the file the OSF registration hashes).

The manifest lists every file of the hardware readout package with its
canonical SHA-256: the amendment, input templates, code, tests, registry,
provenance checker, planning outputs, dry-run and smoke-test outputs.  The
OSF registration records the manifest's own SHA-256 and the commit, and the
runner's real mode refuses if any listed file has changed.  No timestamps, so
the manifest is reproducible from the files.

Order of work: generate outputs -> provenance_hw_v1 --write -> this --write
-> tests -> commit -> OSF registration of that commit and the manifest hash.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import hw_rawio_v1 as rio  # noqa: E402

OUTPUTS = ("package_manifest_v1.json",)
REPO = Path(__file__).resolve().parents[2]
MANIFEST = Path("docs/hardware/package_manifest_v1.json")
INCLUDE = (
    "docs/hardware/amendment_readout_v1.md",
    "docs/hardware/review_v1.md",
    "docs/hardware/*.template.json",
    "experiments/hardware/*.py",
    "experiments/hardware/*.csv",
    "experiments/hardware/*.json",
    "experiments/hardware/*.txt",
    "experiments/hardware/dry_run/**/*",
    "experiments/hardware/adapter_smoke/**/*",
    "tests/test_hw_readout_v1.py",
    "tests/test_readout_power_v1.py",
    "artifact_registry_hw_v1.yaml",
    "src/provenance_hw_v1.py",
    "src/provenance.py",
    "src/hashing.py",
)


def package_files(repo: Path) -> list[str]:
    found: set[str] = set()
    for pattern in INCLUDE:
        for path in repo.glob(pattern):
            if path.is_file() and "__pycache__" not in path.parts:
                found.add(path.relative_to(repo).as_posix())
    found.discard(MANIFEST.as_posix())
    return sorted(found)


def build(repo: Path) -> dict:
    return {"version": "hw_v1",
            "files": {rel: rio.canonical_sha256(repo / rel) for rel in package_files(repo)}}


def check(repo: Path) -> list[str]:
    path = repo / MANIFEST
    if not path.is_file():
        return ["manifest missing"]
    recorded = json.loads(path.read_text(encoding="utf-8"))
    current = build(repo)
    problems = []
    for rel in sorted(set(recorded["files"]) | set(current["files"])):
        a, b = recorded["files"].get(rel), current["files"].get(rel)
        if a != b:
            problems.append(f"{rel}: manifest {a} != current {b}")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    if args.write:
        (REPO / MANIFEST).write_text(json.dumps(build(REPO), indent=1, sort_keys=True) + "\n",
                                     encoding="utf-8", newline="\n")
    problems = check(REPO)
    if problems:
        print("\n".join(problems))
        return 1
    files = json.loads((REPO / MANIFEST).read_text(encoding="utf-8"))["files"]
    print(f"package_files={len(files)}")
    print(f"package_manifest_sha256={rio.canonical_sha256(REPO / MANIFEST)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
