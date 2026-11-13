"""Command-line runner for Part 2 raw rows (protocol v4; admitted by the v4 lock).

The runner refuses to start unless ``split_guard`` admits the split.  For any
split other than the software-test namespace (99) it also requires that HEAD
equals ``--commit`` and that tracked code and protocol files have no
uncommitted changes, so every raw row records the code that produced it.
Development (split 10) additionally requires ``--previous-project-closed``,
the owner's confirmation of the plan's Part 2 entry condition.  Output files
are created exclusively and never overwritten.  This task (2-1) ships the
runner but does not run it on split 10.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import execution  # noqa: E402
import manifest_v4 as manifest  # noqa: E402
import split_guard_v4 as split_guard  # noqa: E402
from hashing import canonical_sha256  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
TRACKED = ("src", "tests", "docs/freeze", "docs/theory")


class RunRefused(RuntimeError):
    pass


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", "--no-optional-locks", *args],
        cwd=REPO,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def preflight(
    split: str, commit: str, previous_project_closed: bool, repo: Path = REPO
) -> None:
    split_guard.require_split(repo, split)
    if split == split_guard.SOFTWARE_TEST:
        return
    if split == split_guard.DEVELOPMENT and not previous_project_closed:
        raise RunRefused(
            "development requires --previous-project-closed (plan, Section 14)"
        )
    head = _git("rev-parse", "HEAD")
    if not commit or head != commit:
        raise RunRefused(f"--commit {commit!r} does not equal HEAD {head}")
    dirty = _git("status", "--porcelain", "--", *TRACKED)
    if dirty:
        raise RunRefused(f"uncommitted changes in tracked files:\n{dirty}")


def row_json(row: execution.Row) -> str:
    payload = dataclasses.asdict(row)
    payload["total_shots"] = row.total_shots
    return json.dumps(payload, sort_keys=True)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", required=True)
    parser.add_argument("--probe", required=True, choices=sorted(execution.PROBE_CODES))
    parser.add_argument(
        "--structure", required=True, choices=sorted(execution.STRUCTURE_CODES)
    )
    parser.add_argument("--setting", required=True)
    parser.add_argument("--parameter-index", type=int, required=True)
    parser.add_argument("--repeats", type=int, default=32)
    parser.add_argument("--fraction", type=float, default=execution.MAIN_FRACTION)
    parser.add_argument("--graphs", type=int, default=None, help="first n graphs only")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--commit", default="")
    parser.add_argument("--previous-project-closed", action="store_true")
    args = parser.parse_args(argv)
    try:
        preflight(args.split, args.commit, args.previous_project_closed)
    except (split_guard.LockError, RunRefused) as error:
        print(f"refused: {error}")
        return 2
    records = manifest.build_manifest(args.split, REPO)[: args.graphs]
    protocol_hash = canonical_sha256(REPO / split_guard.PROTOCOL)
    cache = execution.SolveCache()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8", newline="\n") as handle:
        for record in records:
            for repeat in range(args.repeats):
                row = execution.run_row(
                    split=args.split,
                    record=record,
                    probe=args.probe,
                    structure=args.structure,
                    setting=args.setting,
                    parameter_index=args.parameter_index,
                    repeat=repeat,
                    fraction=args.fraction,
                    cache=cache,
                    commit=args.commit,
                    protocol_sha256=protocol_hash,
                )
                handle.write(row_json(row) + "\n")
    print(f"rows={len(records) * args.repeats} unique_solves={len(cache)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
