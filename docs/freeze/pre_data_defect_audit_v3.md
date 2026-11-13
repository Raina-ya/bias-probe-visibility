# Pre-data defect audit of protocol v3

Status: 2026-11-12, after OSF registration `j67wy` (commit `e8b5300`) and
Task 2-1 (commit `f86b0ee`), before any development (split 10) or holdout
(split 20) data. v3 and its registration are kept unchanged. This audit decides
whether the claim "at least 13 cells must disagree, so agreement is at most
43/56" made in `review_task0_2.tex` holds.

## Verdict

The claim is **partly proven and partly a high-risk projection**. The v3
primary endpoint no longer has a valid interpretation and has a high risk of
failure, but **43/56 is not an analytic proof**.

| Cells | Status | Evidence type |
|---|---|---|
| P4a/E5, P4a/E5', P4b/E5', P4a/E6, P4b/E6 (5) | **Proven**: the observed label is *visible*, so these 5 disagree with the prediction. | Analytic, exact bound |
| P0/E0--E6 (8) | **Not proven; high risk**: the implied label is *partial* on the split-99 graph mixture, against a *blind* prediction. | Population level with a Gaussian approximation, split 99 |

Proven consequence: agreement is at most 51/56 = 0.911 by construction. If the
eight P0 projections also hold on the holdout graphs, it is at most
43/56 = 0.768, below the 0.80 point threshold.

## 1. The five P4 cells (proven)

Under E0 there is no readout error. Every P4a and P4b preparation therefore
returns its prepared string with probability 1, and both statistics are
identically 0. The Section 6.1 order statistic then gives the threshold
`tau = 0`, the strict alarm is `T > 0`, and the matching E0 false-alarm rate is
exactly 0.

Under each listed structure the statistic is 0 only if no probe shot shows a
flip. `experiments/audit/p4_construction_audit.py` bounds that probability
exactly at the main fraction (`n_P = 1,638`); output:
`p4_construction_log.txt`.

| Cell | Predicted | log10 P(no alarm), upper bound (w=4 / w=8) | Observed |
|---|---|---|---|
| P4a/E5 | blind | -149.9 / -149.9 | visible |
| P4a/E5' | blind | -613.9 / -613.9 | visible |
| P4b/E5' | blind | -611.7 / -587.7 | visible |
| P4a/E6 | partial | -101.4 / -202.8 | visible |
| P4b/E6 | partial | -86.4 / -165.9 | visible |

Power is therefore 1 up to these bounds and the false-alarm rate is 0. The
Section 8 rule then gives *visible* in all five cells.

**Cause.** The matrix derives these cells from the parameterized component
(`tau` for E5 and E5', `delta` for E6). The protocol defines each structure as
the whole channel, which includes fixed marginal flips (0.10 for E5, 0.25 for
E5') or baseline rates (0.04/0.06 for E6), and calibrates against a perfect E0.
The matrix's own failure condition for P4a/E5, "the implemented structure leaks
into a marginal", is met by the protocol's definition.

## 2. The eight P0 cells (high risk, not proven)

The P0 alarm is the unresolved outcome `L_T <= 0`. Section 6.1 excludes P0 from
E0 calibration. Its alarm rate is therefore driven by how many graphs have small
gaps, not by bias detection, so it is not comparable to a calibrated
bias-alarm rate.

`experiments/audit/p0_unresolved_audit.py` computes, for each split-99 graph,
the exact noisy mean gap and the exact per-shot score variances at
`n_A = n_B = 8,192`. It then computes `P(|g_hat| <= h_A + h_B)` with a Gaussian
approximation and averages over the 50 graphs. Output:
`p0_unresolved_log.txt`. For signed grids, the smaller of the two sign values
is reported.

| Cell | Mean unresolved probability | Distance from blind bound 0.10 | Implied label |
|---|---:|---:|---|
| P0/E0 | 0.2429 | +0.1429 | partial |
| P0/E1 | 0.7231 | +0.6231 | partial |
| P0/E2 | 0.2586 | +0.1586 | partial |
| P0/E3 | 0.2820 | +0.1820 | partial |
| P0/E4 | 0.3321 | +0.2321 | partial |
| P0/E5 | 0.2627 | +0.1627 | partial |
| P0/E5' | 0.4028 | +0.3028 | partial |
| P0/E6 | 0.2864 | +0.1864 | partial |

**Why this is not a proof.**
- The holdout uses 100 different graphs. Per-graph probabilities range from 0
  to 1, so the graph-mixture mean has sampling uncertainty. The smallest
  margin (+0.143 for E0) is large relative to that uncertainty, but it is not
  zero-risk.
- The Gaussian approximation and the use of the more favourable sign are
  approximations of the frozen procedure.
- The development strength map may select a different sign than this audit.

**What is established** regardless of these points: the P0 alarm measures
unresolved certification, which near ties trigger with no bias at all. A
*blind* label for P0 therefore has no visibility meaning, and P0 should not
share the visible/partial/blind classification with calibrated bias probes.

## 3. Other defects found in the review (not cell disagreements)

1. **Construction-determined cells.** Many cells are fixed by construction.
   The P4a/P4b statistics are identically 0 under E0--E3. P1 and P3 are
   invariant in expectation under E4, E5, and E5', because folding and frames
   are logically equivalent and readout acts last. Their agreement does not
   test the probes.
2. **Endpoint misalignment.** The primary endpoint measures agreement with the
   matrix, not false certification, abstention cost, or detection of decision
   flips.
3. **Circular power analysis.** Power v4 set its class means from the predicted
   labels, so it shows only that the sample size suffices *if* those means hold.

## 4. Consequence

v3 stays registered and unchanged as the record of this defect. Protocol v4
(`docs/freeze/frozen_protocol_v4.md`) repairs the design before any data exist.
Every repair is justified by this audit, which uses analytic results and
population-level computations on split 99 only.
