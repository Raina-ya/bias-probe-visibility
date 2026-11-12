# Frozen protocol v2

Status: self-contained freeze candidate assembled on 2026-11-12. It is not yet
frozen, committed, or preregistered. No noisy development simulation is
authorized until the project owner reviews this exact file, commits it and its
analysis code, and records an independent OSF or AsPredicted timestamp. No
confirmatory holdout seed may be instantiated until the development-derived
confirmatory lock in Section 10 is also committed and independently timestamped.

This file is the only normative protocol for v2. `frozen_protocol_v1.md` and
`protocol_repair_v2_candidate.md` are retained only as audit history and do not
need to be consulted to execute v2.

Evidence boundary: the prediction matrix is analytic. Power analysis v4 is a
simulated design calculation used only to retain the number of graphs and
repeats. Neither is evidence that any physical probe works. No noisy quantum
simulation or hardware result was used to create or revise a prediction.

## 1. Scope and estimand

### 1.1 Research facets

- **F1, primary:** the visibility boundary for decision-relevant differential
  bias under one fixed total shot budget.
- **F2, secondary:** the bias-aware certificate and the fixed-budget value of a
  probe.
- **F3, exploratory:** P1b (`W_neg`) and GVS as existing-diagnostic baselines.

The primary scope is seven probes (P0, P1, P2, P3, P4a, P4b, P5) by eight
structures (E0, E1, E2, E3, E4, E5, E5-prime, E6), for 56 cells. P1b and GVS
do not enter the primary denominator. E7 and probe combinations are exploratory
and carry no analytic prediction.

The primary estimand is **design-distribution visibility**: power and false-
alarm rates averaged over the prespecified graph mixture. It is not a uniform
claim over every graph, width, depth, or error parameter. Minimum power by
width-depth stratum is reported as a limitation analysis.

### 1.2 Fixed-budget meaning

Every probe is evaluated separately against the same total budget
`N=16,384` shots per graph-cell-repeat. Probe, calibration, folding, twin, and
target shots are charged to that budget. Classical processing time, peak memory,
and circuit-depth multipliers are recorded separately. Costs from different
probes are never silently combined.

The primary matrix labels are finite-budget hypotheses about the operational
statistics in this protocol. Analytic sensitivity is necessary justification
for a visible prediction but is not evidence that the required power is reached.

## 2. Graphs, candidates, score, and compilation

### 2.1 Graph manifests

The confirmatory holdout contains 100 independently generated graph instances,
two target candidates per graph, and 32 repeats per graph, structure, probe, and
parameter condition. Widths are 4--8 and QAOA depths are 1--5. Every one of the
25 width-depth strata contains four graphs. Family totals are 34 Erdos-Renyi,
33 Watts-Strogatz, and 33 Barabasi-Albert graphs.

| Family | Frozen construction |
|---|---|
| Erdos-Renyi | Simple `G(w,0.5)`; reject disconnected draws and use the next derived seed. |
| Watts-Strogatz | Rewiring probability 0.30; neighbourhood size 2 at width 4 and 4 at widths 5--8; reject disconnected draws. |
| Barabasi-Albert | Attachment parameter 2; use the library generator's simple connected graph. |

Family labels are assigned before circuit evaluation by a seeded constrained
permutation. Every rejected graph and rejection count is logged. No graph is
rejected because of its ideal gap, noisy result, or probe behaviour.

The development manifest uses the same grid with two graphs per stratum, for 50
graphs and family totals 17/17/16. Development and holdout graph, circuit,
channel, and shot streams are disjoint.

### 2.2 Candidate construction

For each graph-depth record, the two QAOA parameter vectors are independent
fixed draws. Each cost angle is uniform on `[0,2*pi)` and each mixer angle is
uniform on `[0,pi)`. Candidate 1 also receives one logically identity-equivalent
`CX-CX` pair on the lexicographically first graph edge after every cost layer.
The identity pairs create the frozen E1 gate-count contrast without changing
the ideal unitary.

### 2.3 Decision score and ties

For graph `G=(V,E)` and measured bit string `z`, the per-shot score is

\[
s_G(z)=|\{(i,j)\in E:z_i\ne z_j\}|/|E|\in[0,1].
\]

Each candidate value is the expectation of this normalized score. Let
`g=mu_A-mu_B`. The ideal winner is A when `g>0`, B when `g<0`, and tied when
`g=0`; the ideal scoring gap is `Delta=abs(g)`. The observed winner is defined
by the sign of the noisy sample gap. An exact sample tie is unresolved.

An exact ideal tie, `Delta<=1e-12`, is never regenerated. In holdout scoring it
is retained as an unsuccessful graph-level trial for every affected alternative.
The near-tie flag is

\[
\Delta/\max(|\mu_A|,|\mu_B|,10^{-12})\le0.02.
\]

Near ties form a prespecified subgroup and never remove a primary row.

### 2.4 Compilation

Compilation uses basis gates `rz,sx,x,cx`, identity initial layout, routing
method `none`, optimization level 0, and the derived `seed_transpiler`.
Candidate-1 identity pairs are inserted after transpilation inside barriers
after each cost layer. A structural assertion verifies that every pair remains
in the final circuit. Package versions, circuit hashes, and transpiler output
hashes enter the immutable manifest. Assertion failure is a hard stop and does
not authorize a different optimization or routing rule.

## 3. Error structures and parameter grids

Channels use the fixed logical-to-physical layout and schedule. There are 60
physical parameter conditions across E0--E6.

| Code | Frozen operational structure | Physical-strength grid |
|---|---|---|
| E0 | Null/common-mode control: the same deterministic scalar offset is added to both sampled candidate values, leaving their contrast unchanged. | `c in {0,+/-0.01,+/-0.02,+/-0.04}`. |
| E1 | Two-qubit depolarizing channel after every hard two-qubit gate; candidate 1 has the frozen identity pairs. | `p in {0.0025,0.005,0.01,0.02,0.04}`. |
| E2 | Every target cost `RZZ(theta)` is implemented as `RZZ((1+epsilon)*theta)`. | `epsilon in {+/-0.005,+/-0.01,+/-0.02,+/-0.04}`. |
| E3 | Static coherent ZZ insertion from `docs/theory/06_matrix.md`, Eq. E3.1: extra `RZZ(zeta)` after every scheduled hard two-qubit cycle, constant within a run and shared by candidates and probes. | `zeta in {+/-0.005,+/-0.01,+/-0.02,+/-0.04}` radians. |
| E4 | Independent asymmetric assignment error on every qubit, shared across qubits. Entries are `Pr(1|0),Pr(0|1)`. | `(0.01,0.02)`, `(0.02,0.04)`, `(0.04,0.08)`, `(0.08,0.12)`, and the four swapped pairs. |
| E5 | Pair-correlated readout on the lexicographically first graph edge. Begin with independent flips of marginal rate 0.10 and add `tau*(-1)^(f_i+f_j)` to flip-pattern probabilities, preserving one-body marginals. | `tau in {+/-0.0025,+/-0.0050,+/-0.0075,+/-0.0100}`. |
| E5-prime | Synthetic three-body-correlated readout on the lexicographically first connected triple. Begin with independent flips of marginal rate 0.25 and add `tau*(-1)^(f_i+f_j+f_k)`, preserving one- and two-body marginals. No hardware evidence is claimed. | `tau in {+/-0.00390625,+/-0.00781250,+/-0.01171875,+/-0.01562500}`. |
| E6 | Linear asymmetric readout drift over normalized execution time; see Section 7. | `delta in {+/-0.005,+/-0.010,+/-0.020,+/-0.030}`. |
| E7 | One recorded Qiskit fake-backend snapshot, without advance prediction. Device-parameter simulation only. | Log backend name, package version, snapshot time, and extracted parameters; no target-outcome tuning. |

## 4. Operating-point selection

The design ratios are `q in {-1.5,-1.0,-0.5,+0.5}`. E0 remains the zero-bias
control. For each non-null structure and each `q`, development reference data
choose exactly one strength from Section 3 by minimizing

\[
|\operatorname{median}_{\rm development}(\beta/\Delta)-q|.
\]

Exact ideal ties are omitted only from this development median. Ties between
strengths go to the smaller absolute strength and then the smaller signed value.
The resulting strength, median, distance, and input hashes are written to
`docs/freeze/strength_map_v2.csv` by the frozen implementation.

If the closest development median is more than 0.25 from its target, that
structure/target operating point is declared unattainable before holdout. Its
primary cells remain in the 56-cell denominator as disagreements. Otherwise
every holdout graph is evaluated at that one fixed strength. There is no
post-holdout bin filtering, row selection, strength addition, or interpolation.
The realized holdout ratio distribution is diagnostic only.

Development ideal values may be used only to construct this map. They never
enter a probe, set an alarm threshold, select a graph, change a circuit, or
change a holdout strength. Holdout ideal values are used only for immutable
scoring and diagnostics after all observed decisions are written.

The main operating point is `q=-1.5`; `-1.0` and `-0.5` are sensitivity
analyses and `+0.5` is a positive control. E0 false-alarm estimation weights its
seven frozen common-mode values equally.

## 5. Definitions and prediction matrix

Let `P` be the joint population law of frozen target and probe observations,
let `e` lie in the prespecified class `E`, and let the ideal signed top-1 gap be
`Delta=f(P,e)`. The identification region is

\[
\mathcal I_\Delta(P;\mathcal E)
=\{f(P,e'):e'\in\mathcal E,\ e'\text{ compatible with }P\}.
\]

- **Blind in principle:** the region contains a positive and a non-positive gap.
- **Blind within budget:** the relevant population laws differ but no admissible
  frozen rule meets both power and false-alarm requirements over the declared
  class or design distribution.
- **Visible under budget:** an admissible runtime-only rule meets both operating
  requirements. In this protocol, *design-distribution visible* means the
  requirements hold after averaging over the frozen graph mixture; it is not a
  uniform guarantee.
- **Partial:** only a component is visible, an additional transfer/context
  condition is required, or the operating point lies between visible and blind.

Given `P` and `e`, the ideal gap must be uniquely determined. A probe enlarges
the observable law without changing `E`. Probe APIs never accept a target ideal
value.

The authoritative prediction file is `docs/theory/06_matrix.csv`, SHA-256
`7a8e3a56e6f48d8a29c3643c1c2e24f46bce6a54c674d6b1937dbdcd041d8995`,
committed as `c839b95`. The 56 primary cells comprise 35 blind, 15 partial, and
6 visible predictions. P1b/E3 and P1b/E6 remain exploratory question marks.

A matrix mismatch is a hard stop. Development or holdout outcomes never revise
analytic labels; disagreements are failed predictions.

Power analysis v4 retained 100 holdout graphs and 32 repeats after using the
repaired matrix and shared-graph cluster bootstrap. Its design-power estimate
was 1.0000 in each of three prespecified scenarios, with Wilson lower bound
0.9849 over 250 simulated datasets. This validates only design stability under
the assumed scenario means, not physical probe effectiveness. Full details and
hashes are in `docs/freeze/power_analysis_v4.md`.

## 6. Probes, allocation, and alarms

### 6.1 Allocation

For a positive-cost probe at the main fraction `f=0.10`,

\[
n_P=\lfloor0.10N\rfloor=1,638,\qquad n_T=N-n_P=14,746.
\]

Shots are split as evenly as possible across listed circuits. Remainders follow
candidate id and then scale/frame/pair/preparation id. Every cost ledger must
satisfy `target_shots+probe_shots=N`. Zero-extra-shot probes use target counts
and retain all `N` target shots.

Except for P0, every nonnegative composite alarm score is calibrated from
development E0 only. Within each width-depth stratum, sort `n` E0 scores as
`T_(1)<=...<=T_(n)` and set

`tau=T_(min(n,ceil((n+1)*(1-alpha))))`.

The alarm is strict, `T>tau`; ties do not alarm. The entire composite maximum is
calibrated once, so no uncorrected componentwise threshold is added. Numeric
thresholds are deterministic outputs of this frozen rule and enter the
confirmatory lock in Section 10. They are never recalibrated on E1--E7 or
holdout data.

### 6.2 Probe table

| Code | Frozen statistic | Circuits and cost |
|---|---|---|
| P0 | Let `g_hat` be the target sample gap, `h_i=sqrt(log(4/alpha_T)/(2*n_i))`, and `L_T=abs(g_hat)-h_A-h_B`, with `alpha_T=0.025`. Alarm/unresolved is `1{L_T<=0}`. A confidently wrong winner remains blind. | Two targets; all `N` shots split between them; zero extra circuits. |
| P1 | Gap-folding score `abs((g_3-g_1)/2)`. Local unitary folding uses scale 3 and preserves layout. | Scale-1 targets receive `n_T`; scale-3 targets receive `n_P`. Four circuits, two extra; folded depth approximately times 3. |
| P2 | Twin-bias score `abs(g_twin,observed-g_twin,ideal)`. Nearest Clifford angles use deterministic nearest-distance rounding, exact half ties toward the smaller angle. The target ideal value is never computed or passed in. | Target pair receives `n_T`; twin pair receives `n_P`. Two extra circuits, depth multiplier 1. |
| P3 | `abs(g_plain-mean_h(g_frame,h))`, with 16 logically equivalent versions per candidate. Frame signs use 16 rows of a strength-2 binary orthogonal array from distinct nonconstant Sylvester-Hadamard columns, balancing every sampled two-qubit ZZ sign for widths at most 8. | Plain targets receive `n_T`; 32 framed circuits receive `n_P`. Layout and hard-cycle positions are unchanged. |
| P4a | Maximum absolute deviation of an observed single-qubit assignment probability from its prepared basis value, across qubits and the two preparations. | All-zero and all-one preparations receive `n_P`; target pair receives `n_T`. Two probe circuits. |
| P4b | `max(T_marg,T_corr)`. `T_marg` is the maximum assignment deviation across pairs and four preparations. `T_corr` is the maximum TV distance between a pair output and the product of its observed marginals. | Four preparations for every pair: `4*C(w,2)` probes receive `n_P`; target pair receives `n_T`. No grouped reduction. |
| P5 | For each candidate, `T_sym=0.5*sum_z abs(p_hat(z)-p_hat(bitwise_not(z)))`; use the maximum across candidates. E6 adds the two half-scores and their absolute difference to the composite maximum. | Reuses target computational-basis counts; `f=0`, no extra circuit or shot. |
| P1b | `W_neg=sum_{s:p_hat(s)<0} abs(p_hat(s))` for the P1 scale-1/3 Richardson distribution with weights `(3/2,-1/2)`. | Reuses P1 counts; exploratory only. |
| GVS | Covariance-survival ratio in `docs/theory/06_matrix.md`, denominator stabilizer `1e-12`. | Reuses target counts; exploratory only. |

P1b is evaluated only with P1. Dependence from reused counts is retained in all
joint analyses and is never replaced by an independence assumption.

## 7. E6 temporal design

E6 follows

\[
e_0(t)=0.04+\delta t,\qquad e_1(t)=0.06-\delta t,qquad t\in[0,1].
\]

Each run has eight equal temporal blocks; remainder shots go to earlier blocks.

- P4a/P4b split probes equally between blocks 0 and 7; targets occupy blocks
  1--6 in canonical candidate order.
- P1/P2/P3 cycle target and probe identities through all eight blocks using a
  seed-derived permutation followed by its reverse. Each circuit receives shots
  in both halves whenever its allocation is at least 2.
- P0/P5 split each candidate across all eight blocks. P5 halves are blocks 0--3
  and 4--7.

The circuit/block/shot ledger is raw data. Inadequate temporal coverage makes a
run invalid and does not authorize a different ordering. E6 remains partial:
the schedule can reveal a measured change but cannot exclude a blind or post-
bracket component.

## 8. Thresholds and sensitivity values

| Quantity | Main value | Prespecified sensitivity values |
|---|---:|---:|
| Power required for visible | 0.80 | 0.50, 0.90 |
| E0 alarm level `alpha` | 0.05 | 0.01, 0.10 |
| Maximum false-alarm rate for visible | 0.10 | 0.05, 0.15 |
| Positive-cost probe fraction `f` | 0.10 | 0.05, 0.25 |
| Main design ratio | -1.5 | -1.0, -0.5; +0.5 control |
| Blind upper-power boundary | 0.10 | 0.06 at alpha 0.01; 0.15 at alpha 0.10 |
| Primary bootstrap-lower success threshold | 0.80 | 0.70, 0.90 |
| Near-tie relative margin | 0.02 | 0.01, 0.05 |
| Reported interval confidence | 0.95 | none |

An observed cell is visible only if power is at least 0.80 and matching E0 false
alarms are at most 0.10; it is blind if power is at most 0.10; otherwise it is
partial. Visible takes precedence only when both conditions hold. High power
with excessive false alarms is partial.

Every threshold comparison reports `value-threshold`. For an upper limit, a
negative distance is explicitly described as favourable. Sensitivity analyses
change one listed value at a time and never replace the main result.

## 9. Seeds, splits, and immutable raw data

`ROOT_SEED=20261111`. NumPy `SeedSequence` is the only stochastic derivation:

```text
SeedSequence([
  ROOT_SEED, split_code, artifact_code, structure_code, probe_code,
  width, depth, graph_index, candidate_index, repeat_index, parameter_index
])
```

| Field | Codes |
|---|---|
| `split_code` | 10 development, 20 holdout, 30 Proposition-1 pilot, 31 Proposition-1 scoring, 40 E7 exploratory |
| `artifact_code` | 1 family assignment, 2 graph draw, 3 candidate parameters, 4 compilation/frame, 5 channel draw, 6 shot draw, 7 bootstrap |
| `structure_code` | 0--7 for E0--E7, with E5-prime 55 and E6 6 |
| `probe_code` | 0 P0, 1 P1, 2 P2, 3 P3, 40 P4a, 41 P4b, 11 P1b, 50 P5, 90 GVS |

Strings are mapped only through this table, never Python's randomized `hash()`.
Every raw row stores its complete integer seed or spawn key.

Part 2 may instantiate only split 10. Split 20 and split 31 cannot be
instantiated, previewed, summarized, or debugged before their locks. Holdout and
Proposition-1 scoring runners refuse a second successful run and refuse to
overwrite. Failed and partial runs remain immutable and do not authorize a clean
rerun. Platform comparisons reuse manifests and logical seeds and record Python,
NumPy, BLAS, operating system, and simulator versions.

One aggregate raw row represents one graph/probe/structure/parameter/repeat and
contains complete circuit-level counts and costs. Raw and failed rows are never
deleted or overwritten. Every summary must be independently recomputable.

## 10. Two-stage freeze and confirmatory lock

### 10.1 Before development

The owner must commit and independently timestamp:

- this exact protocol and its SHA-256;
- prediction matrix and hash;
- development/holdout manifest-generation code and split guards;
- strength-map algorithm, alarm-calibration algorithm, analysis skeleton, and
  tests; and
- artifact registry and power-v4 artifacts.

Only after this lock may split 10 be instantiated. Numeric thresholds and the
strength map are outputs of frozen algorithms, not manually selected thresholds.

### 10.2 Before holdout

Development may produce only the prespecified strength map, numeric E0 alarm
thresholds, development mismatch report, implementation-error log, and the 1%
timing pilot. These are assembled into `docs/freeze/confirmatory_lock_v2.json`
with input/output hashes. The owner reviews, commits, and independently
timestamps that file. No algorithm, grid, matrix label, endpoint, denominator,
or seed rule can change at this stage.

If an implementation error is fixed, the failing test, before/after difference,
affected artifacts, and proof that split 20 was never instantiated enter the
lock. Scientific mismatch is not an implementation error and never changes the
protocol.

Only after this second lock may split 20 be instantiated. The holdout is read
once.

## 11. Endpoints

### 11.1 Primary endpoint

For each primary cell, power is the mean alarm indicator over 100 graph clusters
and their 32 repeats at the fixed main strength. Matching E0 false alarms use the
same graph manifest. Repeats do not create independent graph clusters.

The point endpoint is the analytic/observed label agreement fraction over all 56
cells. Unattainable, invalid, and not-evaluable cells count as disagreements.

For its 95% interval, perform 10,000 stratified graph-cluster bootstrap
resamples. Resample graph identities within each width-depth stratum, use the
same resampled indices across every probe and structure, recompute all cell
labels, then recompute agreement. Percentiles use NumPy
`method="inverted_cdf"`. The primary endpoint succeeds only if its bootstrap
lower endpoint is at least 0.80. Report the signed distance from 0.80.

### 11.2 Bias-aware certificate

The total false-certification level is 0.05, with
`alpha_T=alpha_P=0.025`. The target bound is P0's simultaneous Hoeffding `L_T`.

The initially validated transfer envelope applies only to P4a/E4 and
P4b/E4,E5, including E6 paths composed from those readout models. Every other
cell returns `B(D_P)=+infinity` and unresolved; this is a substantive negative
result, not missing data.

For an applicable cell:

1. build simultaneous Clopper-Pearson intervals for retained probe event
   probabilities, with Bonferroni allocation of `alpha_P`;
2. retain the frozen finite-grid channels whose predicted event probabilities
   all lie inside those intervals, forming `C_P(D_P)`;
3. for graph score vector `c` and assignment channel `M_e`, compute
   `v_e=c^T(M_e-I)` and `b_G(e)=max_j(v_e,j)-min_j(v_e,j)`; and
4. set `B(D_P)=sup_{e in C_P(D_P)} b_G(e)` by exhaustive finite-grid and
   `2^w`-column enumeration.

Empty sets, failed enumeration, unvalidated models, or unbounded directions set
`B=+infinity`. Certify only if `L_T>B(D_P)`. This certificate covers declared
readout-induced differential bias, not gate, state-preparation, or unmodelled
bias.

Compare false-certification and unresolved rates of this rule with P0 under the
same budget. Point estimates and 95% intervals use graph-cluster resampling;
shared graph indices are retained across rules. Rates and intervals are
reported separately.

### 11.3 Probe fraction and other endpoints

For P0 and P5, test `f=0`; if the operating requirements hold, report `f*=0`.
For positive-cost probes, `f*` is the minimum qualifying value among
`{0.05,0.10,0.25}`. If none qualifies, report `f*>0.25`. Never interpolate.

The Proposition-1 hit rate in Section 13 is secondary and receives a 95% Wilson
interval across its 100 independent graphs. P1b, GVS, E7, and probe combinations
are exploratory and cannot alter primary or secondary definitions.

## 12. Resource contract and scope cuts

The deterministic conservative upper-bound dry run treats all 150 graphs as if
they used all 60 physical grid points, although the holdout uses only the
development-selected `q` strengths. It produced:

- 150 development-plus-holdout graphs;
- 60 parameter conditions;
- 2,016,000 aggregate rows;
- 33,030,144,000 nominal charged shots;
- 1,231,200 unique cached circuit/channel probability solves; and
- 16,389,242,880 projected uncompressed raw bytes.

Fixed caps are 2,000,000 unique probability solves, 5,000,000 aggregate rows,
20 GiB raw output, and 14 elapsed days on the declared reference workstation.
Shot repeats reuse immutable probabilities and draw new multinomial counts; an
identical statevector/density-matrix solve is never rerun for a repeat.

The structural dry run passes. After the initial lock, a 1% development-only
timing pilot projects full elapsed time. If it exceeds 14 days, stop for owner
review before remaining development. No holdout seed may be used for timing.

The only permitted removal order is GVS, P1b, then P3. Removing GVS/P1b does not
change the primary denominator. Removing P3 changes it to 48 cells, so work
stops, power analysis is rerun without development/holdout outcomes, and a new
owner-approved, independently timestamped protocol version is required. No
fourth cut is allowed. No outcome-driven cut occurs after development starts.

## 13. Proposition-1 prediction procedure

This is a secondary predictive test, not a finite-sample certificate.

### 13.1 Pilot and scoring budgets

- Reuse the 100 holdout graph identities under distinct split namespaces and
  draw four independent QAOA candidates per graph (`K=4`).
- ZNE uses local folding scales `(1,3,5)` and equal-weight OLS in scale; fitted
  intercept weights are `(13/12,1/3,-5/12)`.
- Use 32 pilot blocks per graph. Per block, Raw receives 4,096 shots and ZNE
  receives 4,096 shots. Divide Raw over four candidates and ZNE over four
  candidates and three scales.
- Use 32 independent scoring repeats. Per repeat, Raw and ZNE each receive
  16,384 shots. Total charged cost per graph is
  `32*(4096+4096+16384+16384)=1,310,720` shots.

Pilot and scoring costs are both reported. For each block, record four candidate
estimates and three gaps against the pilot anchor. Compute the mean gap vector
and sample covariance as Eqs. (24)--(25) of `docs/theory/09_prop1_ext.md`.
`gamma_hat_i=Sigma_hat_ZNE,ii/Sigma_hat_Raw,ii`; zero Raw variance forces the Raw
default.

The largest mean fitted ZNE intercept proposes the anchor. Use 10,000 paired
block-bootstrap resamples and Bonferroni simultaneous 95% percentile intervals
over all six pairwise intercept gaps. The anchor is resolved only if all its
lower comparison endpoints are positive; otherwise default Raw. No ideal target
value is read. Define `a_hat_i=mu_hat_Raw,i/Delta_hat_pilot,i`; any intercept
interval containing zero makes attenuation unstable and defaults Raw.

### 13.2 Binary rule

Within each bootstrap resample, compute Raw and ZNE multivariate Gaussian top-1
risks at the scoring budget without a shared-correlation model. Use
`Sigma_scoring=Sigma_pilot/4`. Add ridge
`1e-8*trace(Sigma)/3` to covariance diagonals, or `1e-8` when trace is zero.
Orthant probabilities use absolute and relative tolerances `1e-8` and at most
100,000 integration points; convergence is logged.

Let `U_ZNE,U_Raw` be 97.5th percentiles and `L_ZNE,L_Raw` 2.5th percentiles.
Predict ZNE only if the anchor is resolved, attenuation ratios are stable, all
calculations converge, and `U_ZNE<L_Raw`; otherwise predict Raw. Equality is a
Raw tie. Diagnostic reasons are `zne_separated`, `raw_separated`,
`uncertified_raw_default`, `unstable_attenuation`, `unresolved_anchor`, and
`numerical_failure`.

Write `results/prop1/predictions.csv` with:

```text
graph_id,K,anchor_id,pilot_blocks,pilot_shots_raw,pilot_shots_zne,
scoring_repeats,scoring_shots_raw,scoring_shots_zne,mu_raw,gamma_hat,a_hat,
u_zne,l_zne,u_raw,l_raw,prediction,diagnostic_reason,root_seed,protocol_sha256
```

Arrays are JSON-encoded in candidate order. Stop after predictions are written.
The owner must commit and independently timestamp them before split 31 is
instantiated. An exact scoring tie is a miss for either directional prediction.

## 14. Hardware boundary

Hardware is unauthorized by this protocol. A future run requires separate
explicit authorization, a renewed provider-terms check, a go review, and
registered predictions. Only P4a/P4b may run, with total reported QPU usage at
most 360 seconds.

First run the fixed pilot and record `S_pilot` shots and `q_pilot` QPU seconds.
With a 30-second reserve, set `r=1.25*q_pilot/S_pilot` and

\[
S_{remaining}=\left\lfloor\max(0,360-q_{pilot}-30)/r\right\rfloor.
\]

Split remaining shots equally over selected P4a/P4b circuits; remainders follow
probe, pair, preparation order. Fewer than 100 shots per circuit is no-go. If
needed, reduce shots first and width second. Never use an assumed time per shot
or exceed 360 reported QPU seconds. Record backend, calibration timestamp, job
ids, and reported quantum seconds.

## 15. Permitted implementation adjustments

Without a protocol-version change, and only before holdout, the following may
change with a logged reason:

- file layout, function boundaries, batching, caching, and vectorization that
  leave seeds, circuits, probabilities, allocations, and numerical outputs
  unchanged;
- a genuine implementation-error fix satisfying Section 10.2;
- plotting typography, layout, and colours without value changes;
- package patch versions required for installation, only after fixed-manifest
  probabilities agree within already frozen numeric tolerances; and
- E7 snapshot metadata, because E7 is exploratory and externally controlled.

Graph/candidate rules, structures, grids, strength-map and alarm algorithms,
probe statistics, circuit counts, allocations, thresholds, seed splits,
endpoints, denominators, scope-cut order, certificate envelope, pilot rule, and
tie/default rules are not adjustable.

## 16. Change and reporting rules

1. Delays move later tasks later and do not change Part content or order.
2. No rule, matrix label, seed split, endpoint, or analysis choice changes after
   holdout access.
3. Theory-simulation disagreement is a failed prediction, not permission to
   revise theory.
4. Raw and failed runs remain immutable; summaries remain recomputable.
5. A change outside Section 15 requires a new version, owner approval, new
   content hash, and independent timestamp before further noisy simulation.
6. The word **preregistered** is used only after an independent OSF or
   AsPredicted timestamp. Before then, use **freeze candidate** or, after commit
   but before independent timestamp, **frozen and committed in this repository**.
7. Every result is labelled analytic, noiseless simulated, noisy simulated,
   device-parameter simulated, or hardware-derived. Failed, null, and negative
   results are retained without inflation.

## 17. Freeze checklist and hash

Before development, verify all of the following:

1. matrix, protocol, code, and artifact hashes match;
2. protocol-contract and split-lock tests pass;
3. power v4, dry-run ledger, and provenance are independently recomputable;
4. no development or holdout seed has been instantiated;
5. the owner has reviewed this self-contained file; and
6. the reviewed commit has an independent timestamp.

Compute the exact protocol hash from the repository root with:

```powershell
Get-FileHash docs/freeze/frozen_protocol_v2.md -Algorithm SHA256
```
