# Power analysis v5: decision endpoint (non-circular)

Status: design calculation for protocol v4, 2026-11-12. This is a simulated
design calculation from population-level split-99 inputs. It is not noisy
development, holdout, device-parameter, or hardware evidence.

## Why v4's power analysis is replaced

Power v4 set each cell's mean alarm rate from its predicted label, so it could
only show that the sample size suffices *if* the labels are right. Power v5
uses no prediction-matrix label.

## Inputs

`experiments/power/decision_design_inputs_v5.py` writes
`decision_design_inputs_v5.csv`. For each of the 50 split-99 graphs and each
non-null structure at its v4 main setting, it gives the population probability
that the CI-only rule R0 (16,384 target shots) certifies, and that it certifies
the wrong winner. It uses exact noisy means and variances with a Gaussian
approximation; no shot is drawn and no probe is evaluated.

| Structure | Mean R0 false certification | Mean R0 certification | Flipped graphs (of 50) |
|---|---:|---:|---:|
| E1 | 0.0000 | 0.277 | 4 |
| E2 | 0.0200 | 0.740 | 5 |
| E3 | 0.0000 | 0.713 | 3 |
| E4 | 0.0000 | 0.668 | 0 |
| E5 | 0.0000 | 0.736 | 0 |
| E5' | 0.0000 | 0.597 | 0 |
| E6 | 0.0000 | 0.714 | 0 |

CI-only false certification at this budget concentrates on a single split-99
graph (E2). Flipped graphs under E1 and E3 have noisy gaps inside the CI width,
so R0 leaves them unresolved instead of certifying them wrongly.

## Model and grid

`experiments/power/run_power_analysis_v5.py` simulates each dataset as follows:
1. Draw 100 graphs with replacement from the 50 split-99 graphs.
2. Draw 32 repeats per graph and structure as Bernoulli outcomes for R0 and R1.
3. Apply the unknown probe behaviour as a frozen grid: detection probability
   `d in {0, 0.5, 0.9}` on flipped graphs and alarm probability
   `a in {0.05, 0.20}` on non-flipped graphs.
4. Apply a stress factor `k in {1, 5}` to R0 false certification, capped at
   R0's certification probability.
5. Compute a 1,000-resample graph-cluster bootstrap and classify the outcome by
   protocol v4, Section 11.1.

There are 200 datasets per scenario.

## Results (`power_analysis_summary_v5.csv`)

| d | a | P(improvement) | P(no problem) | P(inconclusive) | Mean coverage loss |
|---:|---:|---:|---:|---:|---:|
| 0.0 | 0.05 | 0.000 | 0.730 | 0.270 | 0.031 |
| 0.0 | 0.20 | 0.000 | 0.775 | 0.225 | 0.127 |
| 0.5 | 0.05 | 0.125 | 0.695 | 0.180 | 0.033 |
| 0.5 | 0.20 | 0.130 | 0.725 | 0.145 | 0.127 |
| 0.9 | 0.05 | 0.150 | 0.705 | 0.145 | 0.034 |
| 0.9 | 0.20 | 0.135 | 0.685 | 0.180 | 0.129 |

These rows are for `k=1`. The `k=5` rows differ from them by at most 0.045 in every probability, because
false certification is carried by graphs whose probability is already near the
cap. Raising per-graph probabilities therefore adds almost no information; the
limit is the number of graphs on which false certification occurs at all.

## Interpretation fixed before data

- **Most likely outcome:** *no decision problem at this budget*, with design
  probability 0.69--0.78.
- **Improvement:** design probability at most 0.15 even with a highly sensitive
  probe, because the evidence lives on very few graphs.
- **Why not change the design:** reaching meaningful improvement power would
  need either many more holdout graphs or noise strengths beyond the frozen,
  physically motivated grids. The first exceeds the resource caps (Section 12);
  the second invites the charge of cherry-picking settings. Neither is adopted.
  The *no problem* outcome is a prespecified, publishable result.
- **What the analysis does not show:** it cannot show that any probe works, or
  that the holdout graph mixture matches split 99.
