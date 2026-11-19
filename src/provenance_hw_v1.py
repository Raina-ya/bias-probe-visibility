"""Check or refresh the hardware-amendment artifact registry (artifact_registry_hw_v1.yaml).

Same checks as provenance.py (file exists, canonical hash, generator exists,
output pattern), plus one: the artifact's file name must match a pattern in
the generator's own ``OUTPUTS`` tuple, read from its source without executing
it.  An entry renamed after generation names its original file in
``renamed_from``; an entry captured from the generator's standard output says
``"capture": "stdout"``.
"""

from __future__ import annotations

import argparse
import ast
import fnmatch
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import provenance  # noqa: E402

REGISTRY = "artifact_registry_hw_v1.yaml"


def declared_outputs(generator: Path) -> tuple[str, ...]:
    tree = ast.parse(generator.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "OUTPUTS" for t in node.targets
        ):
            return tuple(ast.literal_eval(node.value))
    return ()


def check(repo: Path, registry: dict) -> list[str]:
    errors: list[str] = []
    for entry in registry["artifacts"]:
        errors.extend(provenance.validate_entry(repo, entry))
        generator = repo / entry["generator"]
        if not generator.is_file():
            continue
        if entry.get("capture") == "stdout":
            continue
        name = entry.get("renamed_from") or Path(entry["path"]).name
        outputs = declared_outputs(generator)
        if not any(fnmatch.fnmatch(name, pattern) for pattern in outputs):
            errors.append(f"{entry['generator']} does not declare {name} in OUTPUTS {outputs}")
    return errors


def load(repo: Path) -> dict:
    return json.loads((repo / REGISTRY).read_text(encoding="utf-8"))


def write_hashes(repo: Path, registry: dict) -> None:
    for entry in registry["artifacts"]:
        entry["sha256"] = provenance.sha256_file(repo / entry["path"])
    (repo / REGISTRY).write_text(json.dumps(registry, indent=2, ensure_ascii=True) + "\n",
                                 encoding="utf-8", newline="\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    repo = Path(__file__).resolve().parents[1]
    registry = load(repo)
    if args.write:
        write_hashes(repo, registry)
        registry = load(repo)
    errors = check(repo, registry)
    if errors:
        print("\n".join(errors))
        return 1
    print(f"registered_artifacts_hw_v1={len(registry['artifacts'])}")
    print("provenance_hw_v1_check=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
