# Holdout execution plan, protocol v4 (Task 3-1)

Status: written and committed **before** split 20 is instantiated, after the
confirmatory lock (`docs/freeze/confirmatory_lock_v4.json`, OSF `j597k`). This
plan implements protocol v4 Sections 9, 11, and 12. It changes no protocol
rule, threshold, operating point, or endpoint.

## 1. What runs

Driver: `experiments/holdout/run_holdout_v4.py`. 100 holdout graphs (four per
width-depth stratum), 32 repeats per unit, `f = 0.10` for positive-cost probes
and `f = 0` for P0 and P5. Operating points come from the locked strength map;
the driver refuses if its hash differs from the lock.

| Phase | Probes | Conditions | Units |
|---|---|---|---:|
| `main` | P0, P1, P2, P3, P4a, P4b, P5 | 7 structures at the main operating point | 4,900 |
| `nulls` | P1--P5 (6 bias probes) | 7 matched nulls | 4,200 |
| `sensitivity` | P1--P5 (6 bias probes) | 7 structures at the smallest frozen strength | 4,200 |
| **Total** | | | **13,300** (425,600 rows) |

- **Primary endpoint (Section 11.1)** uses `main` rows: P0 (R0) and the
  designated probe (R1), scored against the clean-E0 thresholds in the lock.
- **Secondary endpoints (Sections 11.2--11.4)** use `main` (coverage,
  interception, flip subset, P2 variant, readout certificate), `nulls`
  (matched-null false alarms), and `sensitivity` (operating-point sensitivity
  labels). They are computed in Task 3-2 from the same raw rows.
- **Not run:** E0 rows on the holdout (no v4 endpoint uses them), E7, and any
  fraction other than 0.10.

## 2. A secondary endpoint that is not evaluable

`f*` (v3 Section 11.3) requires labels at `f = 0.05` and `f = 0.25`. The
locked thresholds were calibrated in development at `f = 0.10` only, so no
frozen threshold exists at the other fractions. Calibrating them now would
change the confirmatory lock. `f*` is therefore reported as **not evaluable
under v4** for every positive-cost probe; for P0 and P5, `f* = 0` follows from
their zero probe cost. This is a design gap of the development stage, recorded
before the holdout.

## 3. Order and single-run rules

1. `plan`, then `main`, `nulls`, and `sensitivity`, each in four parallel shards.
2. `finalize` checks that each of the 13,300 units appears exactly once, that
   every row is a holdout row, and writes the single-run marker
   `results/run_markers_v4/holdout.success` (exclusive create). After it, the
   split guard refuses every run phase.
3. `reference` (after the marker): ideal and noisy population gaps for scoring.
4. `experiments/holdout/score_primary_v4.py`: the primary endpoint, written once.

Every run phase requires the confirmatory lock and its registration, HEAD equal
to `--commit`, clean tracked files, clean `experiments/holdout` and
`experiments/development`, and an absent marker.

**Failures.** A unit that raises is kept with its traceback, is never rerun, and
counts as present in `finalize`. If any unit needed by the primary endpoint
failed or is missing, the primary outcome is `not_evaluable` and a
complete-case analysis is reported only as a labelled sensitivity result.
A process that stops before writing its shard leaves no rows; rerunning that
shard at the same commit is permitted, reproduces the same rows from the frozen
seed keys, and the run log keeps the aborted start. No shard file is ever
overwritten.

## 4. Platform

Reference workstation and environment of development (Windows 11, Python
3.14.7, NumPy 2.3.4, SciPy 1.16.3, Qiskit 2.2.3; the run log records each
start). Recomputing the analysis from the raw rows on other platforms is
verification, not a second run; every cross-platform difference is reported
without tolerance changes.

## 5. Resources (estimate from development, split 10)

Development unit times (Windows) scaled to the holdout unit list give about
18,300 CPU seconds (about 5.1 hours in one process, about 1.3 hours with four
processes per phase). The conservative bound from the stratified pilot,
0.97 days for 7,000 units, scales to about 1.8 days for 13,300 units, inside the
14-day cap. Raw output is expected near 0.5 GB (gitignored; hashes in the run
log and the marker).

## 6. Evidence labels

All holdout results are noisy simulation. They are confirmatory only for the
endpoints fixed in protocol v4 and read once; everything else is labelled
secondary or exploratory.
