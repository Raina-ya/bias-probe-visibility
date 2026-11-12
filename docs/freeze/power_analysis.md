# Power analysis for the confirmatory holdout

Status: superseded for final freeze by the task 1d-2R repair. These v1--v3
design simulations used the old 30/20/6 matrix and independent-cell Wilson
endpoint. They remain immutable local design-history artifacts but are excluded
from Git because their three superseded raw files total about 153 MB. The
committed repaired matrix was revalidated by
`experiments/power/run_power_analysis_v4.py`.

Status: task 1d-1 complete for the committed 56-cell primary matrix. This is a
simulated design analysis, not a noisy-circuit result and not hardware evidence.

## 1. Preconditions and audit trail

The project owner committed the E3-closed prediction matrix in commit
`3b29c64`. The committed blob and working-tree file matched before the power
run. The matrix used here has SHA-256
`2148b95789b9a24f1c2bc158b372e0570f2fc8fab0fac9f07ffc105160c9c01b`.

No prediction was changed after either power run. P1b and GVS are exploratory
under the research plan and are excluded from the primary endpoint. All 56
primary cells have an evaluable label: 30 blind, 20 partial, and 6 visible.

Three generations are retained rather than overwritten:

- the unlabelled original run used the superseded 53-cell matrix and is kept
  only for audit;
- v2 used the committed 56-cell matrix and selected by the Monte Carlo power
  point estimate; its cheapest candidate was 100 graphs and 16 repeats, but the
  upper-boundary result was too close to the target for a stable decision;
- v3 used the same committed matrix and seeds but required the 95% Wilson lower
  bound of simulated power to meet the target. This is the final design rule.

The conservative rule was adopted before any development or holdout circuit
simulation and before the power-analysis files were committed. v2 remains
available as the audit record that motivated reporting Monte Carlo uncertainty.

## 2. Selected design

The final selected design is:

- 100 independent QAOA graph instances;
- two candidate target circuits per graph, hence 200 target circuits;
- 32 noisy repeats per graph and condition;
- widths 4, 5, 6, 7, and 8;
- QAOA depths 1, 2, 3, 4, and 5;
- four graph instances in every width-by-depth stratum, hence eight candidate
  target circuits per stratum;
- 34 Erdos-Renyi, 33 Watts-Strogatz, and 33 Barabasi-Albert graph instances;
- all random streams derived from `ROOT_SEED = 20261111` through
  `SeedSequence([ROOT_SEED, stage, scenario, graphs, repeats])`.

This exceeds the required minima of 100 target circuits, 50 QAOA graphs, three
graph families, and two circuits per width and depth. It entails 6,400 target
circuit-repeat units per evaluated cell before probe overhead and shots are
charged. Across 56 primary cells this is 358,400 such units. The number is
workload accounting, not a runtime estimate.

The full primary probe scope is retained. P1b and GVS remain exploratory. If a
later frozen resource calculation requires a scope cut, the plan's order is
GVS, then P1b, then P3; it must not change after holdout results are seen.

## 3. Statistical model and decision rule

The independent sampling unit is a graph instance; repeats from the same graph
are clustered. For each cell and graph, the alarm probability is beta
distributed. Conditional repeat outcomes are binomial. The intraclass
correlation is fixed at 0.10. This is a design assumption, not an empirical
estimate.

The observed label uses the frozen main thresholds:

- visible when estimated power is at least 0.80 and estimated false-alarm rate
  is at most 0.10;
- blind when estimated power is at most 0.10, equal to `alpha + 0.05` for
  `alpha = 0.05`;
- partial otherwise.

The primary endpoint succeeds when the Wilson lower bound of the agreement
rate is at least 0.80. With 56 primary cells, this requires at least 51
agreements. The selected design must have the 95% Wilson lower bound of its
simulated primary-endpoint power at least 0.90 in the baseline scenario and at
least 0.80 in both boundary-stress scenarios.

| Scenario | Visible mean; distance from 0.80 | Partial mean; distance from nearest boundary | Blind mean; distance from 0.10 | False-alarm mean; distance from 0.10 | Design-power target |
|---|---:|---:|---:|---:|---:|
| Baseline | 0.85; +0.05 | 0.45; +0.35 from 0.10 and -0.35 from 0.80 | 0.05; -0.05 | 0.05; -0.05 | 0.90 |
| Lower-boundary stress | 0.82; +0.02 | 0.12; +0.02 from 0.10 | 0.08; -0.02 | 0.08; -0.02 | 0.80 |
| Upper-boundary stress | 0.82; +0.02 | 0.78; -0.02 from 0.80 | 0.08; -0.02 | 0.08; -0.02 | 0.80 |

The screen uses 5,000 Monte Carlo runs per design and a normal approximation
with the beta-binomial mean and variance. Candidates are then checked with
5,000 direct beta-binomial Monte Carlo runs. The plan's sensitivity thresholds
remain required analyses but are not used to select the main-design sample
size.

## 4. Full v3 screening grid

Each entry is the simulated probability that the primary endpoint succeeds.
The columns are baseline, lower-boundary stress, and upper-boundary stress.

| Graphs | Target circuits | Repeats | Baseline | Lower stress | Upper stress |
|---:|---:|---:|---:|---:|---:|
| 50 | 100 | 1 | 0.9494 | 0.0000 | 0.0000 |
| 50 | 100 | 2 | 0.9996 | 0.0014 | 0.0012 |
| 50 | 100 | 4 | 1.0000 | 0.0064 | 0.0070 |
| 50 | 100 | 8 | 1.0000 | 0.0766 | 0.0580 |
| 50 | 100 | 16 | 1.0000 | 0.2784 | 0.1858 |
| 50 | 100 | 32 | 1.0000 | 0.4796 | 0.3302 |
| 50 | 100 | 64 | 1.0000 | 0.6182 | 0.4438 |
| 75 | 150 | 1 | 0.9968 | 0.0000 | 0.0002 |
| 75 | 150 | 2 | 1.0000 | 0.0062 | 0.0042 |
| 75 | 150 | 4 | 1.0000 | 0.0780 | 0.0560 |
| 75 | 150 | 8 | 1.0000 | 0.3662 | 0.2526 |
| 75 | 150 | 16 | 1.0000 | 0.7272 | 0.5492 |
| 75 | 150 | 32 | 1.0000 | 0.8912 | 0.7490 |
| 75 | 150 | 64 | 1.0000 | 0.9496 | 0.8364 |
| 100 | 200 | 1 | 1.0000 | 0.0002 | 0.0004 |
| 100 | 200 | 2 | 1.0000 | 0.0222 | 0.0190 |
| 100 | 200 | 4 | 1.0000 | 0.2568 | 0.1640 |
| 100 | 200 | 8 | 1.0000 | 0.7128 | 0.5228 |
| 100 | 200 | 16 | 1.0000 | 0.9372 | 0.8202 |
| 100 | 200 | 32 | 1.0000 | 0.9910 | 0.9368 |
| 100 | 200 | 64 | 1.0000 | 0.9956 | 0.9712 |

Candidates are ordered by `2 * graphs * repeats`, then graph count and repeat
count. Direct checking rejected 100 graphs and 16 repeats before accepting 100
graphs and 32 repeats.

## 5. Direct beta-binomial confirmation

| Repeats | Scenario | Estimated power | 95% Wilson interval | Target | Point margin | Lower-bound margin | Decision |
|---:|---|---:|---:|---:|---:|---:|---|
| 16 | Baseline | 1.0000 | [0.9992, 1.0000] | 0.90 | +0.1000 | +0.0992 | pass |
| 16 | Lower-boundary stress | 0.9306 | [0.9232, 0.9373] | 0.80 | +0.1306 | +0.1232 | pass |
| 16 | Upper-boundary stress | 0.8046 | [0.7934, 0.8154] | 0.80 | +0.0046 | -0.0066 | fail |
| 32 | Baseline | 1.0000 | [0.9992, 1.0000] | 0.90 | +0.1000 | +0.0992 | pass |
| 32 | Lower-boundary stress | 0.9822 | [0.9781, 0.9855] | 0.80 | +0.1822 | +0.1781 | pass |
| 32 | Upper-boundary stress | 0.9236 | [0.9159, 0.9306] | 0.80 | +0.1236 | +0.1159 | pass |

These results support the chosen design only under the declared beta-binomial
model and scenario margins. They do not establish the physical power of a
probe, correctness of a matrix prediction, or feasibility of the shot budget.

## 6. Reproducibility

Run from the repository root with the recorded Python environment:

```powershell
& 'C:\Users\wits\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  experiments/power/run_power_analysis.py `
  --matrix-committed-confirmed --run-label v3 --selection-basis lower
```

The script refuses to run without the confirmation flag and refuses to
overwrite raw, summary, or log files for the same run label. The v3 run log
records Python, NumPy 2.3.5, the platform, and complete `np.show_config()`
output. The v3 raw file has 345,000 Monte Carlo rows: 315,000 screening rows
and 30,000 direct-confirmation rows for the failed and selected candidates.

Local audit files (retained on the originating workstation, not tracked):

- `experiments/power/run_power_analysis.py`
- `experiments/power/power_analysis_raw_v3.csv`
- `experiments/power/power_analysis_summary_v3.csv`
- `experiments/power/run_log_v3.txt`

The original and v2 files are likewise retained locally as audit sensitivity
runs and are not the final design source.

## 7. Remaining limitations before protocol freeze

1. The intraclass correlation of 0.10 and scenario means are design
   assumptions. They are not observed probe performance.
2. Probe overhead, shots, and wall-clock cost are not represented by
   graph-repeat units. The frozen protocol must include the separate cost
   formulas before claiming the full scope fits the total budget.
3. P1b/E3 and P1b/E6 remain exploratory `?` cells. They do not enter the
   primary denominator and must not be promoted to confirmatory claims.
