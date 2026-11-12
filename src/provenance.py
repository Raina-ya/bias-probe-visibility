"""Check or refresh the repository artifact registry."""

from __future__ import annotations

import argparse
import fnmatch
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from hashing import canonical_sha256  # noqa: E402


REGISTRY = "artifact_registry_v1.yaml"


def sha256_file(path: Path) -> str:
    """Return the line-ending-independent hash used by the registry."""

    return canonical_sha256(path)


def load_registry(repo: Path) -> dict[str, object]:
    return json.loads((repo / REGISTRY).read_text(encoding="utf-8"))


def validate_entry(repo: Path, entry: dict[str, str]) -> list[str]:
    errors: list[str] = []
    artifact = repo / entry["path"]
    generator = repo / entry["generator"]
    if not artifact.is_file():
        errors.append(f"missing artifact: {entry['path']}")
    elif sha256_file(artifact) != entry["sha256"]:
        errors.append(f"hash mismatch: {entry['path']}")
    if not generator.is_file():
        errors.append(f"missing generator: {entry['generator']}")
    if not fnmatch.fnmatch(artifact.name, entry["output_pattern"]):
        errors.append(
            f"generator pattern mismatch: {entry['path']} !~ {entry['output_pattern']}"
        )
    return errors


def check(repo: Path, registry: dict[str, object]) -> list[str]:
    errors: list[str] = []
    for raw_entry in registry["artifacts"]:
        errors.extend(validate_entry(repo, raw_entry))
    return errors


def write_hashes(repo: Path, registry: dict[str, object]) -> None:
    for entry in registry["artifacts"]:
        artifact = repo / entry["path"]
        if not artifact.is_file():
            raise FileNotFoundError(entry["path"])
        entry["sha256"] = sha256_file(artifact)
    rendered = json.dumps(registry, indent=2, ensure_ascii=True) + "\n"
    (repo / REGISTRY).write_text(rendered, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    registry = load_registry(repo)
    if args.write:
        write_hashes(repo, registry)
        registry = load_registry(repo)
    errors = check(repo, registry)
    if errors:
        for error in errors:
            print(error)
        return 1
    print(f"registered_artifacts={len(registry['artifacts'])}")
    print("provenance_check=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

