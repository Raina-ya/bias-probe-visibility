# Verification of the v4 secondary endpoints (Task 3-2)

Evidence type: recomputation of a noisy-simulation result from immutable raw
rows. Nothing here re-runs the holdout or changes a result.

## 1. Order of operations

- `experiments/holdout/score_secondary_v4.py` and its tests were committed at
  `00e90f2` (2026-11-17 10:07:57 +08:00) before the scorer first read a
  holdout row. The first run wrote `secondary_endpoints_v4.json` at 10:10:12
  +08:00.
- Before that commit, the scorer was dry-run only on development rows
  (split 10). `tests/test_secondary_v4.py` reproduces the development agreement
  of `docs/freeze/dev_mismatch_v4.md` (invariant 22/23, sensitive 11/19), which
  was computed by separate code in Task 2-3.

## 2. Same code, second platform

On Linux (NumPy 2.5.3), the 12 holdout shards matched the SHA-256 values in
`results/run_markers_v4/holdout.success`. The scorer was rerun on them. The
JSON result is identical to the Windows result (SHA-256
`f081ec3728ad8fed43758974c82693bcb7287408c6c0a0b0e33edbcd082eb3a0`), including
every bootstrap interval, and the Markdown report is byte-identical.

## 3. Points recorded for Task 4-1 (not re-analysed here)

- **Invariant-stratum disagreements: 2 of 23 cells.**
  - P5/E1 (power 0.187) is the cell investigated before the lock
    (`docs/freeze/dev_mismatch_investigation_v4.md`).
  - P2/E5' is new on the holdout: power 0.132 and matched-null false alarm
    0.133. The two rates are equal, so the statistic shows no response to the
    structure. The partial label comes from a holdout null alarm rate above
    alpha against development thresholds that were calibrated on two graphs per
    stratum.
- Both are reported as registered disagreements. Neither label is revised.

## 4. Not yet independent

Both runs used the same scorer. A blind recomputation by a third person
(specification item 24) has not been done.
