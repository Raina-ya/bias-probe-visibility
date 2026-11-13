# Verification of the v4 primary endpoint (Task 3-1)

Evidence type: recomputation of a noisy-simulation result from immutable raw
rows. Nothing here re-runs the holdout or changes the result.

## 1. Run integrity

- Single run at commit `6fc66370215e6497d4fea4a3082124ecef1385d6` on the
  reference workstation (Windows 11, Python 3.14.7, NumPy 2.3.4, SciPy 1.16.3,
  Qiskit 2.2.3), 2026-11-13 14:37--16:14 (UTC+08:00).
- `finalize`: 13,300 of 13,300 units, 0 missing, 0 extra, 0 duplicated,
  0 failed, 425,600 rows, all split `holdout`. Marker
  `results/run_markers_v4/holdout.success` written once.
- The SHA-256 of each of the 12 shards agrees across the run log, the marker,
  and a recomputation from the files.
- After the marker, the full test suite gives 161 passed, 6 xfailed. The
  change from 160/7 is the runner test of post-lock entry 5, which passes
  again once the holdout is closed.

## 2. Same code, second platform

`experiments/holdout/score_primary_v4.py` was rerun on Linux (Python 3.13,
NumPy 2.5.3) on the same raw rows and reference file. The JSON result is
identical to the Windows result (SHA-256
`2e9142d886c96ce870b231fdcb7c0583978f05cc3ca1c5bf80511f6303301c56`), and the
Markdown report is byte-identical. This includes the bootstrap interval, which
uses the frozen seed key.

## 3. Independent code path

`experiments/holdout/independent_primary_check_v4.py` shares no decision code
with the frozen scorer. It recomputes each target gap from the recorded
circuit counts and graph edges, recomputes `L_T` from the Hoeffding formula,
and applies the locked clean-E0 thresholds itself. It uses its own
graph-cluster bootstrap with an unrelated generator.

| Quantity | Frozen scorer | Independent check |
|---|---:|---:|
| max abs(recomputed gap - recorded gap) | | 1.1e-15 |
| rows where recomputed `L_T>0` disagrees with recorded `alarm_p0` | | 0 |
| dFC point | 0.008036 | 0.008036 |
| pooled FC(R0) | 0.010313 | 0.010313 |
| dFC 95% interval | [0.002857, 0.014152] | [0.002857, 0.014107] (own resampling) |
| FC(R0) 97.5th percentile | 0.017946 | 0.017903 (own resampling) |

All seven per-structure FC and coverage values agree to the printed precision.
The interval endpoints differ only through resampling noise, and both give
the outcome **improvement**.

## 4. Not yet independent

Both checks were run by the same project (owner and assistant). A blind
recomputation by a third person from the protocol and raw rows (specification
item 24) has not been done.
