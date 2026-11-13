"""Check or refresh the protocol-v4 artifact registry.

``artifact_registry_v1.yaml`` is part of the registered v3 lock and stays
unchanged; artifacts produced for v4 are registered in
``artifact_registry_v4.yaml`` with the same checks as ``provenance.py``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import provenance  # noqa: E402

REGISTRY = "artifact_registry_v4.yaml"


def load_registry(repo: Path) -> dict:
    return json.loads((repo / REGISTRY).read_text(encoding="utf-8"))


def write_hashes(repo: Path, registry: dict) -> None:
    for entry in registry["artifacts"]:
        entry["sha256"] = provenance.sha256_file(repo / entry["path"])
    (repo / REGISTRY).write_text(
        json.dumps(registry, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    registry = load_registry(repo)
    if args.write:
        write_hashes(repo, registry)
        registry = load_registry(repo)
    errors = provenance.check(repo, registry)
    if errors:
        print("\n".join(errors))
        return 1
    print(f"registered_artifacts_v4={len(registry['artifacts'])}")
    print("provenance_v4_check=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
