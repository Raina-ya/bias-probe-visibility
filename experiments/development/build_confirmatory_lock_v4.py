"""Assemble docs/freeze/confirmatory_lock_v4.json (protocol v4 Section 10.2).

The lock records, with LF-normalized SHA-256 hashes:

* the development products named in Section 10.2: the strength map,
  thresholds (machine-readable and reviewed form), the development mismatch
  report and its investigation, the implementation-error log, and the timing
  pilot with its projections;
* every development raw shard (gitignored; the hash is the record), the
  reference rows, and the run log;
* the scripts that produced them;
* the frozen choices the holdout analysis must use: operating points,
  designated probes, matched nulls, and the thresholds file;
* the holdout execution and platform policy;
* checks that split 20 was never instantiated.

It refuses to run unless HEAD equals --commit and no tracked file has an
uncommitted modification (the products themselves are new, untracked files),
re-verifies the v4 development registration, and writes the lock once
(exclusive create).  It reads no holdout data and builds no holdout manifest.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

import cells_v4  # noqa: E402
import runner  # noqa: E402
import split_guard_v4  # noqa: E402
from hashing import canonical_sha256  # noqa: E402

DEV = Path("results/development_v4")
LOCK = split_guard_v4.CONFIRMATORY_LOCK

PRODUCTS = {
    "strength_map": DEV / "strength_map_v4.csv",
    "thresholds_csv": DEV / "thresholds_v4.csv",
    "thresholds_md": Path("docs/freeze/thresholds_v4.md"),
    "dev_mismatch": Path("docs/freeze/dev_mismatch_v4.md"),
    "dev_mismatch_investigation": Path("docs/freeze/dev_mismatch_investigation_v4.md"),
    "implementation_error_log": Path("docs/freeze/implementation_error_log_v4.md"),
    "timing_projection_first_pilot_invalid": DEV / "timing_projection_v4.json",
    "timing_projection_stratified": DEV / "timing_projection_stratified_v4.json",
}
SUPPORTING = {
    "reference_rows": DEV / "reference" / "dev_reference_v4.csv",
    "run_log": DEV / "run_log_v4.jsonl",
}
SCRIPTS = (
    "experiments/development/run_development_v4.py",
    "experiments/development/project_timing_v4.py",
    "experiments/development/compare_reference_v4.py",
    "experiments/development/calibrate_v4.py",
    "experiments/development/p5_e1_diagnostic_v4.py",
    "experiments/development/build_confirmatory_lock_v4.py",
)
RAW_PHASES = ("pilot", "pilot-stratified", "nulls", "main")
PLATFORM_POLICY = (
    "The holdout (split 20) is instantiated once, on the reference workstation "
    "and environment that produced development (recorded below), at a commit "
    "whose tracked files are clean and whose only change after this lock is "
    "registration_confirmatory_v4.json. The single-run marker refuses a second "
    "successful run; failed or partial runs stay immutable and do not authorize "
    "a clean rerun. Analysis is recomputed from the raw holdout rows; an "
    "independent CI recomputation of the analysis on Linux and Windows is "
    "verification, not a second holdout run, and every cross-platform "
    "difference is reported without tolerance changes."
)


def environment_from_log(path: Path) -> list[dict]:
    seen, out = set(), []
    for line in path.read_text(encoding="utf-8").splitlines():
        event = json.loads(line)
        if event.get("event") != "start":
            continue
        env = {
            k: event[k]
            for k in ("commit", "python", "numpy", "scipy", "qiskit", "platform")
            if k in event
        }
        key = json.dumps(env, sort_keys=True)
        if key not in seen:
            seen.add(key)
            out.append(env)
    return out


def raw_shards(repo: Path) -> dict[str, str]:
    out = {}
    for phase in RAW_PHASES:
        for path in sorted((repo / DEV / phase).glob("*.jsonl.gz")):
            out[path.relative_to(repo).as_posix()] = canonical_sha256(path)
    return out


def split_evidence(repo: Path) -> dict:
    rows, splits = 0, set()
    for phase in RAW_PHASES:
        for path in sorted((repo / DEV / phase).glob("*.jsonl.gz")):
            with gzip.open(path, "rt", encoding="utf-8") as handle:
                for line in handle:
                    for row in json.loads(line)["rows"]:
                        rows += 1
                        splits.add(row["split"])
    results = repo / "results"
    holdout_paths = sorted(
        p.relative_to(repo).as_posix()
        for p in results.rglob("*")
        if "holdout" in p.name.lower() or "split20" in p.name.lower()
    )
    markers = (
        sorted(
            p.relative_to(repo).as_posix()
            for p in (results / "run_markers_v4").glob("*")
        )
        if (results / "run_markers_v4").is_dir()
        else []
    )
    evidence = {
        "raw_rows_checked": rows,
        "raw_row_splits": sorted(splits),
        "paths_under_results_naming_holdout": holdout_paths,
        "v4_run_markers": markers,
        "confirmatory_registration_present": (
            repo / split_guard_v4.CONFIRMATORY_REGISTRATION
        ).exists(),
        "holdout_refused_by_split_guard_v4": _holdout_refused(repo),
    }
    evidence["split_20_never_instantiated"] = (
        evidence["raw_row_splits"] == ["development"]
        and not holdout_paths
        and not markers
        and not evidence["confirmatory_registration_present"]
        and evidence["holdout_refused_by_split_guard_v4"]
    )
    return evidence


def _holdout_refused(repo: Path) -> bool:
    try:
        split_guard_v4.require_split(repo, "holdout")
    except (split_guard_v4.LockError, FileNotFoundError):
        # A missing lock file also refuses the holdout.
        return True
    return False


def frozen_choices(repo: Path) -> dict:
    with (repo / PRODUCTS["strength_map"]).open(encoding="utf-8", newline="") as h:
        chosen = [
            {k: r[k] for k in ("structure", "point", "setting", "development_median")}
            for r in csv.DictReader(h)
            if r["chosen"] == "1"
        ]
    return {
        "operating_points": chosen,
        "designated_probes": dict(cells_v4.DESIGNATED),
        "matched_nulls": dict(cells_v4.MATCHED_NULL),
        "cell_components": {
            f"{p}/{s}": cells_v4.component(p, s) for p, s in cells_v4.cells()
        },
        "thresholds_file": PRODUCTS["thresholds_csv"].as_posix(),
        "alarm_rule": "strict T > tau; visibility uses matched-null tau, decision "
        "endpoints use clean-E0 tau, per probe, component, and width-depth stratum",
    }


def check_commit(repo: Path, commit: str) -> None:
    head = runner._git("rev-parse", "HEAD")
    if head != commit:
        raise SystemExit(f"--commit {commit} does not equal HEAD {head}")
    dirty = runner._git("status", "--porcelain", "--untracked-files=no")
    if dirty:
        raise SystemExit(f"uncommitted changes in tracked files:\n{dirty}")


def build(repo: Path, commit: str, ci_run_url: str | None = None) -> dict:
    record = split_guard_v4.require_development_lock(repo)
    missing = [
        p.as_posix()
        for p in {**PRODUCTS, **SUPPORTING}.values()
        if not (repo / p).is_file()
    ] + [s for s in SCRIPTS if not (repo / s).is_file()]
    if missing:
        raise SystemExit(f"missing inputs: {missing}")
    evidence = split_evidence(repo)
    if not evidence["split_20_never_instantiated"]:
        raise SystemExit(f"split-20 evidence check failed: {evidence}")
    return {
        "lock": "confirmatory_lock_v4",
        "protocol": "docs/freeze/frozen_protocol_v4.md",
        "protocol_sha256": canonical_sha256(repo / split_guard_v4.PROTOCOL),
        "development_registration": {
            k: record[k] for k in ("registry", "url", "timestamp_utc", "commit")
        },
        "built_at_commit": commit,
        "development_environment": environment_from_log(repo / SUPPORTING["run_log"]),
        "products": {
            k: {"path": p.as_posix(), "sha256": canonical_sha256(repo / p)}
            for k, p in PRODUCTS.items()
        },
        "supporting": {
            k: {"path": p.as_posix(), "sha256": canonical_sha256(repo / p)}
            for k, p in SUPPORTING.items()
        },
        "raw_shards_gitignored": raw_shards(repo),
        "scripts": {s: canonical_sha256(repo / s) for s in SCRIPTS},
        "frozen_choices": frozen_choices(repo),
        "platform_policy": PLATFORM_POLICY,
        "ci_reference_rebuild": {
            "workflow": ".github/workflows/rebuild-reference.yml",
            "run_url": ci_run_url,
            "reported_result": "passed on ubuntu-latest and windows-latest"
            if ci_run_url
            else None,
        },
        "split_20_evidence": evidence,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", required=True)
    parser.add_argument("--ci-run-url", default=None)
    args = parser.parse_args(argv)
    check_commit(REPO, args.commit)
    lock = build(REPO, args.commit, args.ci_run_url)
    with (REPO / LOCK).open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(lock, indent=1, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "wrote": LOCK.as_posix(),
                "sha256": canonical_sha256(REPO / LOCK),
                "split_20_never_instantiated": lock["split_20_evidence"][
                    "split_20_never_instantiated"
                ],
            }
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
