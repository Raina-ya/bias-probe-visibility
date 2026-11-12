# Frozen protocol v1

Status: freeze candidate for task 1d-2, assembled on 2026-11-11. This file
becomes frozen only after the project owner commits it and records an independent
OSF or AsPredicted timestamp. No noisy development or holdout simulation is
authorized before those two events. The SHA-256 of the exact file bytes is kept
in `docs/freeze/frozen_protocol_v1.sha256`; a hash command is also given at the
end of this file.

Evidence boundary: the prediction matrix is analytic. The power analysis is a
simulated design calculation used only to choose the number of graphs and
repeats. It is not evidence that any probe works, and no simulation result is
used to create or revise a prediction.

## 1. Scope

### 1.1 Research facets

- **F1, primary:** the visibility boundary for decision-relevant differential
  bias under one fixed total shot budget.
- **F2, secondary:** the bias-aware certificate and the fixed-budget value of a
  probe.
- **F3, exploratory:** P1b (`W_neg`) and GVS as existing-diagnostic baselines.

The primary scope contains seven probes (P0, P1, P2, P3, P4a, P4b, and P5) by
eight structures (E0, E1, E2, E3, E4, E5, E5-prime, and E6), for 56 cells. P1b
and GVS do not enter the primary denominator. E7 and combinations of probes are
exploratory and carry no analytic prediction.

### 1.2 Circuit design

The confirmatory holdout contains 100 independently generated graph instances,
two candidate target circuits per graph, and 32 noisy repeats per graph,
structure, probe, and parameter condition. Widths are 4, 5, 6, 7, and 8; QAOA
depths are 1, 2, 3, 4, and 5. Every width-by-depth stratum contains four graphs
and therefore eight candidate target circuits. The family totals are 34
Erdos-Renyi, 33 Watts-Strogatz, and 33 Barabasi-Albert graphs.

Graph generation is fixed as follows.

| Family | Frozen construction |
|---|---|
| Erdos-Renyi | Simple `G(w, 0.5)`; reject disconnected draws and redraw from the next derived seed. |
| Watts-Strogatz | Rewiring probability 0.30; neighbourhood size 2 at width 4 and 4 at widths 5--8; reject disconnected draws. |
| Barabasi-Albert | Attachment parameter 2; the library generator's simple connected graph is used. |

The 100 family labels are assigned before circuit evaluation by a seeded
permutation constrained to the totals 34/33/33. Rejection counts and every
rejected graph are logged. No graph is rejected for its ideal gap, noisy result,
or probe behaviour.

For each graph and depth, the two QAOA parameter vectors are independent fixed
draws with each cost angle uniform on `[0, 2*pi)` and each mixer angle uniform on
`[0, pi)`. Candidate 1 additionally receives one logically identity-equivalent
`CX-CX` pair on the lexicographically first graph edge after every QAOA cost
layer. This leaves its ideal unitary unchanged while freezing a gate-count
contrast for E1. The noiseless reference selects the true top candidate only
when outcomes are scored; it is never supplied to a probe and is never used to
accept, reject, or regenerate a candidate pair.

The development set has the same width-depth grid but two graphs per stratum,
for 50 graphs and 100 candidate circuits. Its family totals are 17/17/16,
assigned by the same seeded constrained-permutation rule. Development and
holdout graphs, circuits, noise draws, and shot draws are disjoint.

### 1.3 Structures and parameter grid

All channels act after transpilation on the fixed logical-to-physical layout.
The layout, basis gates, optimization level, and schedule are identical across
development and holdout. The main total budget for one graph-cell-repeat is
`N = 16,384` shots. Exact population probabilities may be used only to assign
the realized bias-to-gap stratum and to score decisions. They may not tune a
channel, choose a graph, change a circuit, calibrate an alarm, or enter a probe.

| Code | Frozen operational structure | Physical-strength grid |
|---|---|---|
| E0 | Null/common-mode control. The same deterministic scalar offset is added to both candidate values after sampling, so the decision contrast is unchanged. | `c in {0, +/-0.01, +/-0.02, +/-0.04}`; zero differential bias for every value. |
| E1 | A two-qubit depolarizing channel after every hard two-qubit gate. Candidate 1 has the frozen extra identity pairs described above. | `p in {0.0025, 0.005, 0.01, 0.02, 0.04}`. |
| E2 | Angle-dependent coherent over-rotation: every target cost `RZZ(theta)` is implemented as `RZZ((1+epsilon) theta)`. | `epsilon in {+/-0.005, +/-0.01, +/-0.02, +/-0.04}`. |
| E3 | The static coherent ZZ insertion model in `docs/theory/06_matrix.md`, Eq. E3.1: an extra `RZZ(zeta)` follows every scheduled hard two-qubit cycle; the parameter is constant within a run and shared by both candidates and probes. | `zeta in {+/-0.005, +/-0.01, +/-0.02, +/-0.04}` radians. |
| E4 | Independent asymmetric assignment error on every qubit. The two entries are `Pr(1|0)` and `Pr(0|1)` and are shared across qubits. | `(0.01,0.02)`, `(0.02,0.04)`, `(0.04,0.08)`, `(0.08,0.12)`, and the four swapped pairs. |
| E5 | Pair-correlated readout on the lexicographically first graph edge. Start from independent bit flips with marginal rate `r=0.10`, then add `tau*(-1)^(f_i+f_j)` to the four flip-pattern probabilities. This preserves both one-qubit marginals. | `tau in {+/-0.0025, +/-0.0050, +/-0.0075, +/-0.0100}`. |
| E5-prime | Three-body-correlated readout on the lexicographically first connected triple. Start from independent bit flips with marginal rate `r=0.25`, then add `tau*(-1)^(f_i+f_j+f_k)` to the eight flip-pattern probabilities. This preserves every one- and two-qubit marginal. This is a synthetic pressure structure without claimed hardware evidence. | `tau in {+/-0.00390625, +/-0.00781250, +/-0.01171875, +/-0.01562500}`. |
| E6 | Calibration-to-execution readout drift. Calibration uses `(Pr(1|0),Pr(0|1))=(0.04,0.06)`; execution uses `(0.04+delta,0.06-delta)`. Probe circuits precede target circuits. | `delta in {+/-0.005, +/-0.010, +/-0.020, +/-0.030}`. |
| E7 | One recorded Qiskit fake-backend snapshot, used without advance prediction. | The backend name, package version, snapshot time, and extracted parameters are logged; no tuning to target outcomes is allowed. |

For every non-null run, the exact reference evaluator computes the realized
`r = beta/Delta` only after the graph, candidates, and channel strength have
been fixed. Rows are assigned without tuning to the following frozen bins:

| Label | Realized ratio |
|---|---:|
| positive | `r > 0.25` |
| 0 | `-0.25 <= r <= 0.25` |
| -0.5 | `-0.75 < r < -0.25` |
| -1.0 | `-1.25 < r <= -0.75` |
| -1.5 | `r <= -1.25` |

The main observed classification uses the `-1.5` bin. The `-1.0` and `-0.5`
bins are prespecified sensitivity analyses. Positive and zero bins are controls.
All fixed-strength rows remain in raw output even if their bin is empty or
unexpected. If a primary cell has no holdout row in its main bin, that cell is
marked **not evaluable and counted as a disagreement** in the fixed 56-cell
primary denominator; no channel strength may be added after seeing this.

## 2. Definitions

Let `P` be the joint population law of the frozen target and probe observations,
let `e` lie in the prespecified noise class `E`, and let the ideal top-1 gap be
`Delta = f(P,e)`. A strict decision succeeds only for `Delta > 0`; zero is on
the non-certifying side.

The identification region is

\[
\mathcal I_\Delta(P;\mathcal E)
=\{f(P,e'):e'\in\mathcal E,\ e'\text{ compatible with }P\}.
\]

- **Blind in principle:** the region contains at least one positive and at
  least one non-positive gap.
- **Blind within budget:** the relevant population laws differ, but no
  admissible rule under the frozen observations and budget meets the frozen
  power and false-alarm requirements uniformly over the alternative class.
- **Visible under budget:** an admissible runtime-only rule reaches the frozen
  power and false-alarm requirements uniformly over the declared class.
- **Partial:** only a stated component is visible, a transfer/context condition
  is needed, or the finite-budget operating point lies between visible and
  blind.

Given `P` and `e`, the ideal gap must be uniquely determined. A probe enlarges
the observable law but does not change the prespecified noise class. Probes may
not read the target's ideal value. The reference evaluator is isolated from all
probe APIs and is used only for post-generation stratum labels and scoring.

## 3. Prediction matrix

The authoritative analytic predictions are
`docs/theory/06_matrix.csv`, SHA-256
`2148b95789b9a24f1c2bc158b372e0570f2fc8fab0fac9f07ffc105160c9c01b`.
That hash matched commit `3b29c64` before the task 1d-1 power analysis.

The primary matrix has 56 cells: 30 blind, 20 partial, and 6 visible. P1b/E3
and P1b/E6 remain exploratory question-mark cells and never enter the primary
denominator. A matrix hash mismatch is a hard stop: no development or holdout
run may begin until the mismatch is explained and a new owner-approved freeze
and independent timestamp exist. Development or holdout outcomes never revise
the analytic labels; disagreements are reported as failed predictions.

## 4. Probe specifications and costs

### 4.1 Shared allocation rule

Each probe is evaluated separately against the same per-graph-cell-repeat
budget `N=16,384`; costs from different probes are not silently combined.
For a positive-cost probe, the main probe allocation is

\[
n_P=\lfloor 0.10N\rfloor=1,638,\qquad n_T=N-n_P=14,746.
\]

Shots are split as evenly as possible across the listed circuits. Remainders go
in canonical order: candidate id, then scale/frame/preparation id. The cost
ledger must satisfy `target_shots + probe_shots = N` exactly. Classical
post-processing time, peak memory, and circuit depth multipliers are recorded
separately. Zero-extra-shot statistics use target counts and therefore receive
all `N` target shots.

Every nonnegative alarm score below is calibrated from development E0 only.
For a width-depth stratum with `n` E0 scores sorted as
`T_(1) <= ... <= T_(n)`, the main threshold is
`tau = T_(min(n, ceil((n+1)*(1-alpha))))`. The alarm is strict, `T > tau`.
Ties therefore do not alarm. This rule is run separately for every probe and
width-depth stratum. It is not recalibrated from E1--E7 or from holdout data.

### 4.2 Probe table

| Code | Statistic and alarm score | Frozen circuits and shot cost |
|---|---|---|
| P0 | Confidence-interval-only baseline. It returns unresolved when the one-sided 95% lower confidence bound of the observed winner's gap is non-positive; it has no independent bias alarm. | Two target candidates; all `N` shots split between them; zero extra circuits. |
| P1 | Gap-folding score `T=abs((g_3-g_1)/2)`. Local unitary folding uses scale 3 and preserves layout. | Scale-1 target pair receives `n_T`; scale-3 pair receives `n_P`. Four circuits total, two extra relative to P0; folded depth approximately times 3. |
| P2 | Twin-bias score `T=abs(g_twin,observed-g_twin,ideal)`. The nearest-Clifford twin's ideal gap is computed classically; the target's ideal value is never computed or passed in. | Target pair receives `n_T`; twin pair receives `n_P`. Two extra circuits, depth multiplier 1. Nearest Clifford angles use deterministic nearest-distance rounding with exact half ties toward the smaller angle. |
| P3 | `T=abs(g_plain - mean_h g_frame,h)`. Use `m=16` logically equivalent randomized-compiling versions per candidate. The frame signs use 16 rows of a strength-2 binary orthogonal array obtained from distinct nonconstant columns of a Sylvester Hadamard matrix; this makes every sampled two-qubit ZZ sign exactly balanced for widths at most 8. | Plain target pair receives `n_T`; 32 framed circuits receive `n_P`. Cost is `2m=32` extra circuits. Layout and hard-cycle locations are unchanged. |
| P4a | Maximum absolute deviation of an observed single-qubit assignment probability from its prepared basis value, over qubits and the two preparations. | All-zero and all-one preparations; two probe circuits receive `n_P`; target pair receives `n_T`. |
| P4b | Maximum, over qubit pairs and four preparations, of total-variation distance between the observed pair distribution and the product of its observed one-qubit marginals. | Four preparations for every pair: `4*C(w,2)` probe circuits receive `n_P`; target pair receives `n_T`. No grouped-design reduction is used in the primary analysis. |
| P1b | `W_neg=sum_{s:p_hat(s)<0} abs(p_hat(s))`, where `p_hat` is the scale-1/scale-3 linear Richardson distribution with weights `(3/2,-1/2)`. | Reuses the exact P1 counts and ledger; no shots beyond P1. Exploratory only. |
| GVS | The covariance-survival ratio specified in `docs/theory/06_matrix.md`, with denominator stabilizer `epsilon_0=10^-12`. | Reuses target counts; all `N` shots remain target shots; no extra circuits. Exploratory only. |
| P5 | Global-bit-flip distribution-asymmetry score `T=(1/2)*sum_z abs(p_hat(z)-p_hat(bitwise_not(z)))`, whose ideal value is zero for the frozen QAOA MaxCut construction. | Reuses computational-basis target counts; all `N` shots remain target shots; no extra circuits or shots. |

P1b is evaluated only jointly with P1 because its claimed zero-extra-shot cost
depends on reusing P1 counts. For shared-count probes, dependence between target
and alarm events is retained in all joint analyses; it is never replaced by an
independence assumption.

## 5. Thresholds and sensitivity table

| Quantity | Main value | Prespecified sensitivity values |
|---|---:|---:|
| Power required for visible | 0.80 | 0.50, 0.90 |
| Alarm level `alpha` used in E0 calibration | 0.05 | 0.01, 0.10 |
| Maximum holdout false-alarm rate for visible | 0.10 | 0.05, 0.15 |
| Probe budget fraction `f` | 0.10 | 0.05, 0.25 |
| Bias-to-gap stratum used for classification | -1.5 bin | -1.0 bin, -0.5 bin |
| Blind upper-power boundary | `alpha+0.05=0.10` | recomputed as 0.06 and 0.15 when `alpha` is 0.01 and 0.10 |
| Primary Wilson-lower success threshold | 0.80 | 0.70, 0.90 |
| Near-tie relative margin | 0.02 | 0.01, 0.05 |
| Confidence level for reported Wilson intervals | 0.95 | none |

The observed cell label is visible only when holdout power is at least 0.80 and
the matching E0 false-alarm rate is at most 0.10; blind when power is at most
0.10; otherwise it is partial. Visible takes precedence only if both of its
conditions hold. A cell with high power and excessive false alarms is partial.

Every value-versus-threshold statement reports signed distance as
`value - threshold`; for an upper limit, the report also states that a negative
distance is favourable. Sensitivity analyses change one listed quantity at a
time and never replace the main result.

## 6. Data split and seeds

`ROOT_SEED = 20261111`. NumPy `SeedSequence` is the only seed derivation
mechanism. Stage 0 remains reserved for the completed power analysis. All later
random streams use

```text
SeedSequence([
  ROOT_SEED, split_code, artifact_code, structure_code, probe_code,
  width, depth, graph_index, candidate_index, repeat_index, parameter_index
])
```

The frozen codes are:

| Field | Codes |
|---|---|
| `split_code` | 10 development, 20 confirmatory holdout, 30 Proposition 1 pilot, 31 Proposition 1 scoring, 40 E7 exploratory |
| `artifact_code` | 1 family assignment, 2 graph draw, 3 candidate parameters, 4 compilation/frame, 5 channel draw, 6 shot draw, 7 bootstrap |
| `structure_code` | 0--7 for E0--E7, with E5-prime assigned 55 and E6 assigned 6 |
| `probe_code` | 0 P0, 1 P1, 2 P2, 3 P3, 40 P4a, 41 P4b, 11 P1b, 50 P5, 90 GVS |

String identifiers are mapped only through this table, never through Python's
process-randomized `hash()`. The complete derived integer seed or spawn key is
written in every raw row.

Part 2 may instantiate only split code 10. Split codes 20 and 31 must not be
instantiated, previewed, summarized, or used for debugging before Part 3. The
holdout runner refuses a second successful run and refuses to overwrite raw
rows. Failed and partial runs are retained and identified; they do not authorize
a clean rerun. Any platform comparison reuses the same immutable manifest and
logical seeds and records platform, Python, NumPy, and BLAS configuration.

## 7. Primary and secondary endpoints

### 7.1 Primary endpoint

For each of the 56 primary cells, estimate power and the matching E0 false-alarm
rate from the 100 independent graph clusters; 32 repeats within a graph are not
treated as 32 independent graphs. Apply the classification rule in Section 5.
The endpoint is the number of analytic labels in the hashed matrix that agree
with their observed labels, divided by 56, with a two-sided 95% Wilson interval.
Not-evaluable cells remain in the denominator as disagreements.

The primary endpoint succeeds only if the Wilson lower bound is at least 0.80.
With 56 fixed cells, at least 51 agreements are required. The signed distance
from 0.80 is reported. The holdout is read once and the endpoint is computed
once from immutable raw rows.

### 7.2 Secondary endpoints

1. False-certification rate and unresolved rate of the bias-aware rule
   `L_T > B(D_P)` versus the confidence-interval-only rule under the same total
   budget. The two rates are reported separately with 95% Wilson intervals.
2. For each primary probe, the minimum evaluated fraction `f*` among
   `{0.05,0.10,0.25}` that reaches power 0.80 while satisfying false alarms at
   most 0.10. If none qualifies, report `f* > 0.25`; do not interpolate.
3. The one-time hit rate of the frozen Proposition 1 Raw-versus-ZNE predictions,
   with a 95% Wilson interval.

P1b, GVS, E7, and probe combinations are exploratory. They use the same
threshold and budget accounting where applicable but cannot change the primary
or secondary endpoint definitions.

## 8. Scope-cutting rule

The full 56-cell primary scope is retained. Before Part 2, the implementation
must generate a deterministic dry-run cost ledger from this protocol. A scope
cut is allowed only before any development noise or shot outcome is generated,
and only if the ledger shows that the declared run cannot allocate at least one
shot to every frozen circuit or cannot complete within the storage and compute
limits recorded before the dry run.

The only permitted removal order is:

1. GVS;
2. P1b;
3. P3.

GVS and P1b are exploratory, so removing them does not change the 56-cell
primary denominator. Removing P3 changes the primary scope to 48 cells and is
therefore not automatic: work stops, the power analysis is rerun for the new
denominator without reading development or holdout data, the owner approves a
new protocol version, and a new independent timestamp is obtained. No fourth
cut is allowed under v1. Resource failure after development starts is reported
as a failure; it does not trigger a post-outcome scope cut or added runs.

## 9. Proposition 1 prediction procedure

This is a secondary predictive test, not a finite-sample certificate. Its
uncertainty rule is frozen to make the prediction falsifiable; it does not claim
the Berry--Esseen guarantee that `docs/theory/09_prop1_ext.md` explicitly leaves
unevaluated.

### 9.1 Candidate, budget, and pilot

- Use the same 100 holdout graph identities but a distinct seed namespace and
  four independently generated QAOA parameter vectors per graph (`K=4`).
- ZNE uses local folding scales `(1,3,5)` and an equal-weight ordinary least
  squares line in scale. The fitted intercept weights are
  `(13/12, 1/3, -5/12)`.
- There are `R_p=32` independent pilot blocks per graph. In every block Raw
  receives 4,096 shots and ZNE receives 4,096 shots. Raw shots are divided over
  four candidates; ZNE shots are divided over four candidates and three scales.
  Remainders follow the canonical ordering in Section 4.
- Scoring is separate and immutable: there are 32 independent scoring repeats;
  in each repeat Raw receives 16,384 shots and ZNE receives 16,384 shots. The
  complete charged cost is therefore
  `32*(4096+4096+16384+16384) = 1,310,720` shots per graph. Pilot and scoring
  costs are both reported; neither is hidden from the budget ledger.

For each pilot block and method, record all four candidate estimates and all
three gaps against the pilot anchor. Across blocks, compute the mean gap vector
and sample covariance exactly as Eqs. (24)--(25) of
`docs/theory/09_prop1_ext.md`. The marginal variance overhead is
`gamma_hat_i = Sigma_hat_ZNE,ii / Sigma_hat_Raw,ii`. A zero Raw variance makes
the ratio unstable and forces the Raw default.

The candidate with the largest mean fitted ZNE intercept is the proposed
anchor. Use 10,000 paired, block-level bootstrap resamples and a Bonferroni
simultaneous 95% percentile interval over the six pairwise intercept gaps. The
anchor is resolved only if every interval comparing it with another candidate
has lower endpoint strictly above zero. Otherwise the prediction defaults to
Raw. No noiseless or ideal target value is read.

For every non-anchor candidate `i`, let `Delta_hat_pilot,i` be its fitted
intercept gap and set

\[
\widehat a_i
=\widehat\mu_{Raw,i}/\widehat\Delta_{pilot,i}.
\]

If the simultaneous bootstrap interval for any intercept gap includes zero,
the attenuation ratio is unstable and the prediction defaults to Raw.

### 9.2 Binary decision rule

Within every bootstrap resample, compute the Raw and ZNE multivariate Gaussian
top-1 risks at the scoring budget from the resampled mean gap and covariance
vectors, without imposing a shared-correlation model. Because a pilot block has
4,096 shots and a scoring repeat has 16,384, use
`Sigma_scoring = Sigma_pilot/4`. Add the deterministic
ridge `10^-8 * trace(Sigma)/3` to each covariance diagonal; if the trace is zero,
use `10^-8`. Compute orthant probabilities with the implementation's fixed
absolute tolerance `10^-8`, relative tolerance `10^-8`, and maximum 100,000
integration points; convergence status is logged.

Let `U_ZNE` and `U_Raw` be the 97.5th percentiles of the corresponding 10,000
risk estimates, and let `L_ZNE` and `L_Raw` be their 2.5th percentiles.

- Predict **ZNE better** only when the anchor is resolved, every attenuation
  ratio is stable, every covariance calculation converges, and
  `U_ZNE < L_Raw`.
- Otherwise predict **Raw better**. Equality is a Raw tie.

Record `zne_separated` when the ZNE rule passes, `raw_separated` when it does not
pass and `U_Raw < L_ZNE`, and `uncertified_raw_default` when neither risk is
separated. The other permitted reasons are `unstable_attenuation`,
`unresolved_anchor`, and `numerical_failure`. Only the binary prediction enters
the hit-rate endpoint. This bootstrap separation is an operational prediction
rule, not Eq. (22)'s finite-sample certificate.

The prediction file is
`results/prop1/predictions.csv` with fields:

```text
graph_id,K,anchor_id,pilot_blocks,pilot_shots_raw,pilot_shots_zne,
scoring_repeats,scoring_shots_raw,scoring_shots_zne,mu_raw,gamma_hat,a_hat,
u_zne,l_zne,u_raw,l_raw,prediction,diagnostic_reason,root_seed,protocol_sha256
```

Arrays are JSON-encoded in candidate-id order. Task 3-3 stops after writing this
file. The project owner must commit and independently register the predictions
before split code 31 is instantiated. Scoring then records which method has the
lower top-1 error rate on each graph; an exact tie counts as a miss for either
directional prediction. The hit rate is reported once and the rule is never
retuned.

## 10. Items that may be adjusted but must be logged

Only the following may change without a new protocol version, and every change
must appear in both the run log and change record before holdout access:

- file layout, function boundaries, batching, caching, vectorization, and other
  performance changes that leave seeds, circuits, probabilities, allocations,
  and numeric outputs unchanged;
- a genuine implementation-error fix found on the development set, with the
  failing test, before/after diff, affected artifacts, and proof that no holdout
  seed was instantiated;
- plotting layout, typography, and colours when the underlying values are
  unchanged;
- package patch versions required for installation, provided a cross-check
  shows identical frozen manifests and probabilities within the already fixed
  numeric tolerances; otherwise work stops for owner review;
- E7 backend snapshot metadata, because E7 is exploratory and the snapshot is
  not under project control.

Graph rules, candidate rules, structures, parameter grids, bins, probe
statistics, circuit counts, allocations, thresholds, seeds, endpoints,
denominators, scope-cut order, pilot rule, and tie/default rules are not in this
adjustable list.

## 11. Change rules

1. Delays move later tasks later. They do not change the content or order of the
   four Parts.
2. No rule, threshold, matrix label, seed split, endpoint, or analysis choice
   changes after holdout results are seen.
3. Theory-simulation disagreement is a failed prediction, not a reason to
   revise the theory.
4. Raw repeat-level rows and failed runs are immutable and never deleted or
   overwritten. Summaries must be recomputable from raw rows.
5. Any change outside Section 10 requires an incremented protocol version,
   owner approval, a new content hash, and a new independent timestamp before
   further noisy simulation. The superseded version remains in the audit trail.
6. Hardware is outside Parts 2--3. A hardware run requires a separate explicit
   authorization, a renewed check of current provider terms, and registered
   predictions. If authorized, only P4a and P4b run, total QPU usage is capped
   at six minutes, and the reduction order is shots first and width second.
7. The word **preregistered** is not used until an independent OSF or
   AsPredicted timestamp exists. Before then, the correct description is
   **frozen and committed in this repository**.

Compute the exact content hash from the repository root with:

```powershell
Get-FileHash docs/freeze/frozen_protocol_v1.md -Algorithm SHA256
```
