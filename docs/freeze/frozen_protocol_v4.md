# Frozen protocol v4

Status: freeze candidate assembled on 2026-11-12. Not yet committed or
registered. It supersedes protocol v3 (OSF `j67wy`, commit `e8b5300`), which
stays registered and unchanged. The reasons are documented, before any data,
in `docs/freeze/pre_data_defect_audit_v3.md`. No development (split 10) or
holdout (split 20) row exists. No noisy development simulation is authorized
until the owner reviews this exact file, commits it together with the complete
execution code listed in Section 10.1, records an independent OSF or
AsPredicted timestamp, and writes `docs/freeze/registration_v4.json`.

Where this file says "as v3" or "those of v3", the cited text of
`docs/freeze/frozen_protocol_v3.md` (registered, immutable) is normative and
incorporated by reference.

Unlike v3, the complete execution code (probes, runner, analysis) is
registered together with the protocol. There is no "register first, write the
runner later" stage.

Evidence boundary: the v4 matrix labels are analytic. Population-level
semantic tests on the software-test namespace (split 99) were used before
registration to check the invariant-versus-sensitive direction of every cell;
four derivation errors were found and corrected, and both passes are retained
(Section 5.3). Power analysis v5 is a simulated design calculation from
split-99 population inputs and a frozen effect-size grid; it uses no matrix
label. None of these is evidence that a physical probe works.

## 1. Scope, roles, and estimands

### 1.1 Roles

- **Bias probes (primary matrix):** P1, P2, P3, P4a, P4b, P5.
- **CI-only comparator:** P0. It is not a bias probe, and its unresolved
  outcome is not a bias alarm. It enters only the decision endpoints.
- **Global null control:** E0, a clean device with common-mode offsets.
- **Structures:** E1, E2, E3, E4, E5, E5-prime, E6, each with a matched null
  (Section 3.2).
- **Exploratory, no prediction:** P1b, GVS, E7, probe combinations.

The primary visibility matrix has 6 probes by 7 structures, 42 cells.

### 1.2 Estimands

- **Primary (decision level), Section 11.1:** the pooled change in
  false-certification rate when the CI-only rule is replaced by the bias-aware
  rule at the same total budget.
- **Secondary:** coverage and abstention cost, interception of CI-only false
  certifications, detection on the decision-flip subset, false alarms on the
  non-flip subset, the readout certificate, probe fraction, and the
  Proposition-1 hit rate (Sections 11.2--11.5).
- **Secondary (visibility):** agreement of observed and predicted labels,
  reported separately for the invariant stratum (23 cells) and the sensitive
  stratum (19 cells), never pooled into one headline number (Section 11.3).

### 1.3 Fixed budget

Every row is evaluated against the same total budget `N=16,384` shots per
graph-cell-repeat. Probe, calibration, folding, twin, and target shots are
charged to that budget. Classical processing time, peak memory, and depth
multipliers are recorded separately.

## 2. Graphs, candidates, score, and compilation

### 2.1 Graph manifests

The confirmatory holdout contains 100 independently generated graph instances,
two target candidates per graph, and 32 repeats per graph, structure, probe, and
parameter condition. Widths are 4--8 and QAOA depths are 1--5. Every one of the
25 width-depth strata contains four graphs. Family totals are 34 Erdos-Renyi,
33 Watts-Strogatz, and 33 Barabasi-Albert graphs.

| Family | Frozen construction |
|---|---|
| Erdos-Renyi | Simple `G(w,0.5)`: each vertex pair is an edge independently with probability 0.5; reject disconnected draws and use the next derived seed. |
| Watts-Strogatz | Ring lattice with neighbourhood size 2 at width 4 and 4 at widths 5--8; each lattice edge is rewired with probability 0.30 to a uniformly chosen non-neighbour; reject disconnected draws. |
| Barabasi-Albert | Attachment parameter 2, grown from a star on three vertices by preferential attachment through a repeated-node list; always connected. |

All three generators are implemented in `src/manifest.py` on NumPy
`Generator` streams; no third-party graph library is used. After a
disconnected draw, attempt `r` uses `repeat_index=r` in the graph-draw seed key
(Section 9). Family labels are assigned before circuit evaluation by one seeded
permutation of the family-label multiset over the graph list ordered by width,
depth, and graph index. Every rejected graph and rejection count is logged. No
graph is rejected because of its ideal gap, noisy result, or probe behaviour.

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

After transpilation, the `RZ` between the two `CX` gates of every cost `RZZ`
is tagged as a cost rotation (`rzc`). The number of tagged rotations must equal
the number of edges times the depth; otherwise compilation stops. E2 acts on
every tagged cost rotation at execution time (Section 3).

## 3. Error structures, matched nulls, and grids

### 3.1 Structures

Channels use the fixed logical-to-physical layout and schedule. The grids are
those of v3.

| Code | Operational structure | Strength grid |
|---|---|---|
| E0 | Clean device; the same deterministic scalar offset is added to both sampled candidate values. | `c in {0,+/-0.01,+/-0.02,+/-0.04}` |
| E1 | Two-qubit depolarizing channel after every hard CX, in target and probe circuits. | `p in {0.0025,0.005,0.01,0.02,0.04}` |
| E2 | Every tagged cost rotation `RZ(theta)` executes as `RZ((1+epsilon)*theta)`, in target and probe circuits, including folded inverses and twin rotations. | `epsilon in {+/-0.005,+/-0.01,+/-0.02,+/-0.04}` |
| E3 | `RZZ(zeta)` on the pair of every hard CX, immediately after it, in target and probe circuits. | `zeta in {+/-0.005,+/-0.01,+/-0.02,+/-0.04}` |
| E4 | Independent assignment error `(Pr(1|0),Pr(0|1))` on every qubit. | `(0.01,0.02)`, `(0.02,0.04)`, `(0.04,0.08)`, `(0.08,0.12)`, and the four swapped pairs |
| E5 | On the lexicographically first edge: independent flips of marginal rate 0.10 plus `tau*(-1)^(f_i+f_j)`. Other qubits are error-free. | `tau in {+/-0.0025,+/-0.0050,+/-0.0075,+/-0.0100}` |
| E5-prime | On the lexicographically smallest connected vertex triple: independent flips of marginal rate 0.25 plus `tau*(-1)^(f_i+f_j+f_k)`. Synthetic; no hardware evidence. | `tau in {+/-0.00390625,...,+/-0.015625}` |
| E6 | Baseline assignment rates `e0=0.04+delta*t`, `e1=0.06-delta*t` on every qubit (Section 7). | `delta in {+/-0.005,+/-0.010,+/-0.020,+/-0.030}` |
| E7 | One recorded Qiskit fake-backend snapshot; exploratory and outside Part 2's main run. | Logged only |

### 3.2 Matched nulls

Each structure is compared with the same structure at zero strength of its
tested component.

| Structure | Matched null |
|---|---|
| E1, E2, E3, E4 | The clean device (`p=0`, `epsilon=0`, `zeta=0`, rates `(0,0)`) |
| E5 | `tau=0`, keeping the 0.10 marginal pair flips |
| E5-prime | `tau=0`, keeping the 0.25 marginal triple flips |
| E6 | `delta=0`, keeping the baseline rates 0.04/0.06 |

Visibility alarms (Section 6.3) are calibrated on the matched null. Decision
endpoints (Section 11.1) use alarms calibrated on clean E0, because a deployed
rule cannot know which structure is present.

## 4. Operating-point selection

The v3 rule is unchanged. Each structure is evaluated at its largest frozen
strength (main) and its smallest (sensitivity). Signs and E4 orientation are
chosen by the development median of
`beta/Delta=(g_noisy-g)*sign(g)/|g|`; medians within `1e-12` are tied, ties go
to the negative sign or to the first-listed E4 pair, and exact ideal ties are
omitted from the median. Development ideal values are used only for this map
(`docs/freeze/strength_map_v4.csv`, written by `src/strength_map.py`); they
never enter a probe, a threshold, or a holdout choice.

Analytic constraints that remain in force (`docs/freeze/freeze_review_v2.md`,
Section 3):
- uniform readout gives `beta/Delta=-(1-lambda^2)`, so E4 and E6 never flip a
  decision;
- E6's ratio does not depend on `delta`;
- E5-prime's `tau` does not change the gap.

## 5. Definitions and prediction matrix

### 5.1 Labels

The visible, blind, and partial definitions and the identification region are
those of v3. A cell is evaluated on its component statistic (Section 6.2)
against its matched null (Section 3.2).

### 5.2 Matrix and strata

The authoritative file is `docs/theory/06_matrix_v4.csv`, LF-normalized
SHA-256 `53a2048062b25e8f09c772c332c56c463fa32a6b24e9cb56a3d8ff129fad661b`. The
42 cells comprise 4 visible, 13 partial, and 25 blind predictions.

Each cell also carries a stratum:
- **invariant** (23 cells): the cell's component statistic has exactly the
  same population value under the structure and under its matched null, by an
  analytic invariance;
- **sensitive** (19 cells): the population value changes. The label then
  depends on the budget.

A disagreement in the invariant stratum means an implementation or derivation
error. A disagreement in the sensitive stratum is a failed budget prediction.

### 5.3 Pre-registration semantic tests

`experiments/semantic/semantic_tests_v4.py` computes every cell's component at
the strongest settings and at the matched null from exact expected counts, on
10 split-99 graphs of widths 4--6. A cell is observed invariant if every
difference is below `1e-9`.

The first pass (`semantic_tests_v4_first_pass.csv`) disagreed with the analytic
stratum in four cells. Each was traced to a derivation error and corrected
before registration:

| Cell | First derivation | Corrected | Reason |
|---|---|---|---|
| P3/E2 | sensitive, visible | invariant, blind | Frames act only around each CX; non-Clifford cost rotations are not twirled. |
| P5/E3 | invariant, blind | sensitive, partial | A ZZ between the CX gates of a cost RZZ acts as a logical single-qubit Z rotation and breaks flip symmetry. |
| P1/E6 | invariant, blind | sensitive, blind | The candidates' shots fall in different blocks, so a block-dependent `delta(t)^2` term remains (about `2.5e-4`). |
| P3/E6 | invariant, blind | sensitive, blind | Same as P1/E6. |

The second pass (`semantic_tests_v4.csv`) has no disagreement. Because the
labels were corrected after the first pass, the second pass confirms the
corrected strata. It is not an independent test of them.

## 6. Probes, allocation, and alarms

### 6.1 Allocation

Unchanged from v3. At `f=0.10`, `n_P=1,638` and `n_T=14,746`; zero-extra
probes (P0, P5) give all `N` shots to the targets. Every ledger satisfies
`target_shots+probe_shots=N`.

### 6.2 Statistics and components

The probe statistics are those of v3, Section 6.2. The P4 probes record
component scores, and each cell uses exactly one component.

| Probe | Components recorded | Cell mapping |
|---|---|---|
| P4a | `assignment` (v3 P4a statistic); for E6 also `temporal_contrast` = max over qubits and both preparations of abs(one-rate in block 0 minus one-rate in block 7) | E1--E5-prime: `assignment`; E6: `temporal_contrast` |
| P4b | `t_marg`, `t_corr` (v3 definitions); for E6 also `temporal_contrast` = max over pairs, preparations, and the two prepared qubits of abs(block-0 one-rate minus block-7 one-rate) | E1--E4: `t_marg`; E5, E5-prime: `t_corr`; E6: `temporal_contrast` |
| P1, P2, P3, P5 | v3 statistic | statistic |

The mapping is frozen in `src/cells_v4.py`. No omnibus maximum is used for P4
cells.

### 6.3 Alarm calibration

For each probe, cell component, width-depth stratum, and calibration null,
sort the development null scores and set
`tau=T_(min(n,ceil((n+1)*(1-alpha))))` with exact rational arithmetic. The alarm
is strict, `T>tau`, with `alpha=0.05`. Visibility cells use their matched
null. Decision endpoints use clean E0. Thresholds are outputs of this rule and
enter the confirmatory lock (Section 10.2). They are never recalibrated on a
structure's non-null settings or on holdout data.

A degenerate null, one whose component is identically 0, gives `tau=0`. This
is reported for every affected cell.

## 7. E6 temporal design

E6 follows

\[
e_0(t)=0.04+\delta t,\qquad e_1(t)=0.06-\delta t,\qquad t\in[0,1].
\]

Each run has eight temporal blocks \(b=0,\ldots,7\). Every shot in block \(b\)
uses \(t_b=(2b+1)/16\). Wherever shots are divided, remainders go to earlier
blocks.

- **P4a/P4b:** each probe circuit's shots are split equally between blocks 0
  and 7. Each target candidate's shots are split evenly over blocks 1--6.
  Within a block the order is candidate A, candidate B, then probe circuits in
  canonical order.
- **P1/P2/P3:** let \(L\) be the canonical circuit list: target A, target B,
  then probe circuits in canonical order. A permutation \(\pi\) of \(L\) is
  drawn from the seed key with `artifact_code=4`, `structure_code=6`, the
  probe's code, and the graph, repeat, and parameter indices. Each circuit's
  allocation is split into two halves, the first receiving any odd shot. The
  first half of every circuit is executed in order \(\pi\) and the second half
  in reverse order. Each half's concatenated shot sequence is cut into four
  consecutive blocks of equal size: blocks 0--3 for the first half and 4--7
  for the second.
- **P0/P5:** each candidate's shots are split evenly over all eight blocks, A
  before B within a block. P5 half-scores use blocks 0--3 and 4--7.

The circuit/block/shot ledger is raw data. Inadequate temporal coverage makes a
run invalid and does not authorize a different ordering. E6 remains partial:
the schedule can reveal a measured change but cannot exclude a blind or post-
bracket component.

## 8. Thresholds and sensitivity values

| Quantity | Main value | Sensitivity values |
|---|---:|---:|
| Power required for visible | 0.80 | 0.50, 0.90 |
| Alarm level `alpha` | 0.05 | 0.01, 0.10 |
| Maximum matched-null false-alarm rate for visible | 0.10 | 0.05, 0.15 |
| Positive-cost probe fraction `f` | 0.10 | 0.05, 0.25 |
| Operating point | Largest frozen strength | Smallest frozen strength |
| Blind upper-power boundary | 0.10 | 0.06 at alpha 0.01; 0.15 at alpha 0.10 |
| Decision endpoint: no-problem bound on CI-only false certification | 0.01 | 0.005, 0.02 |
| Near-tie relative margin | 0.02 | 0.01, 0.05 |
| Reported interval confidence | 0.95 | none |

The labelling rule is that of v3, applied to the cell component and its
matched null. Every comparison reports `value-threshold`. Sensitivity analyses
change one value at a time and never replace the main result.

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
| `split_code` | 10 development, 20 holdout, 30 Proposition-1 pilot, 31 Proposition-1 scoring, 40 E7 exploratory, 99 software tests and design checks (never reported as results) |
| `artifact_code` | 1 family assignment, 2 graph draw, 3 candidate parameters, 4 compilation/frame, 5 channel draw, 6 shot draw, 7 bootstrap |
| `structure_code` | 0--7 for E0--E7, with E5-prime 55 and E6 6 |
| `probe_code` | 0 P0, 1 P1, 2 P2, 3 P3, 40 P4a, 41 P4b, 11 P1b, 50 P5, 90 GVS |

Strings are mapped only through this table, never Python's randomized `hash()`.
A matched null (Section 3.2) uses the structure's own `structure_code` and the
parameter index that follows the structure's last grid value.
Graph, family, and candidate keys use `structure_code=0` and `probe_code=0`
because those artifacts are shared by every structure and probe. Unused fields
are 0.
Every raw row stores its complete integer seed or spawn key.

Part 2 may instantiate only split 10. The Proposition-1 pilot (split 30)
reuses holdout graph identities and therefore requires the confirmatory lock. Split 20 and split 31 cannot be
instantiated, previewed, summarized, or debugged before their locks. Holdout and
Proposition-1 scoring runners refuse a second successful run and refuse to
overwrite. Failed and partial runs remain immutable and do not authorize a clean
rerun. Platform comparisons reuse manifests and logical seeds and record Python,
NumPy, BLAS, operating system, and simulator versions.

One aggregate raw row represents one graph/probe/structure/parameter/repeat and
contains complete circuit-level counts and costs. Raw and failed rows are never
deleted or overwritten. Every summary must be independently recomputable.

## 10. Freeze and confirmatory lock

### 10.1 Before development

The owner commits and independently timestamps:

- this protocol and its SHA-256, and the v4 matrix;
- **all execution and analysis code:** `src/hashing.py`,
  `src/protocol_contract.py`, `src/manifest.py`, `src/manifest_v4.py`,
  `src/split_guard_v4.py`, `src/circuits.py`, `src/simulate.py`,
  `src/channels.py`, `src/probes.py`, `src/execution.py`, `src/reference.py`,
  `src/cells_v4.py`, `src/strength_map.py`, `src/alarm_calibration.py`,
  `src/analysis.py`, `src/analysis_v4.py`, `src/runner.py`, `src/provenance.py`,
  `src/provenance_v4.py`, and every test file;
- the pre-data audit, the semantic-test outputs, and the power-v5 inputs,
  outputs, and code;
- `artifact_registry_v4.yaml` with `src/provenance_v4.py`.
  `artifact_registry_v1.yaml` belongs to the v3 lock and stays unchanged.

The owner then writes `docs/freeze/registration_v4.json`.
`src/split_guard_v4.py` admits split 10 only if every file in
`PRE_DEVELOPMENT_FILES_V4` is listed there and unchanged. The v3 lock files stay
unchanged and are not used for v4.

Part 2 additionally requires the owner's confirmation that the previous
project is closed (runner flag `--previous-project-closed`).

### 10.2 Before holdout

Development (split 10) produces only:
- `strength_map_v4.csv`;
- `thresholds_v4.md`, holding every matched-null and clean-E0 threshold;
- `dev_mismatch_v4.md`;
- the implementation-error log;
- the 1% timing pilot.

These are assembled with hashes into `docs/freeze/confirmatory_lock_v4.json`,
committed, and independently timestamped, together with proof that split 20
was never instantiated. Only then may split 20 be instantiated, once.

## 11. Endpoints

### 11.1 Primary: false-certification change at a fixed budget

For each non-null structure `s` at its main operating point:

- **CI-only rule R0 (P0 rows, all `N` on the targets):** certify when
  `L_T>0`, and declare the winner by the sign of `g_hat`.
- **Bias-aware rule R1 (rows of the designated probe `j(s)` at `f=0.10`):**
  certify when the row's own `L_T>0` (computed from its `n_T` target shots) and
  probe `j(s)` does not alarm against its clean-E0 threshold; the winner is as
  for R0.
- **Designated probes (frozen, `src/cells_v4.py`):** E1 P1; E2 P2; E3 P3; E4,
  E5, E5-prime, and E6 P4a.
- **False certification:** a certification whose winner differs from the ideal
  winner, scored after all decisions are written. An ideal tie counts as false
  whenever it is certified.

`FC_s(R)` is the mean over the 100 holdout graphs and 32 repeats.

**Estimand:**
`dFC = (1/7) * sum_s [FC_s(R0) - FC_s(R1)]`, with a 95% interval from 10,000
stratified graph-cluster bootstrap resamples using shared graph indices across
structures and rules (`method="inverted_cdf"`).

**Prespecified outcome:**
- **improvement:** the 2.5th percentile of `dFC` is greater than 0;
- **no decision problem at this budget:** not improvement, and the 97.5th
  percentile of the pooled `FC(R0)` is less than 0.01;
- **inconclusive:** otherwise.

Each outcome is a reportable result. Power v5 (Section 12) gives their design
probabilities.

### 11.2 Secondary decision endpoints

- **Coverage:** `C_s(R)=P(certify)` and the coverage loss `C_s(R0)-C_s(R1)`,
  per structure and pooled.
- **Interception:** among (graph, repeat) units where R0 false-certifies, the
  fraction R1 does not certify. Reported with its count, and *insufficient*
  below 5 units.
- **Flip subset (v3 Section 11.4 definition):** the designated probe's alarm
  rate on flipped graphs, and its false-alarm rate on non-flipped graphs.
- **Structure-agnostic variant:** R1 with P2 as the designated probe for every
  structure.

### 11.3 Secondary visibility agreement

For each of the 42 cells, power is the mean alarm indicator at the main
operating point against the cell's matched-null threshold. The label follows
Section 8. Agreement is reported separately for the 23 invariant cells and the
19 sensitive cells, each with a stratified graph-cluster bootstrap interval.
There is no success threshold, and the strata are never pooled. P0 does not
enter.

### 11.4 Readout certificate

As v3 Section 11.2: valid only for P4a/E4, P4b/E4, and P4b/E5, and `+infinity`
elsewhere. It is compared with R0 at the same budget. Because E4 never flips a
decision, its value is reported as coverage gained or lost, not as error
prevented.

### 11.5 Other endpoints

The probe fraction `f*` and the Proposition-1 hit rate (Section 13) are as in
v3. P1b, GVS, E7, and probe combinations are exploratory.

## 12. Resources and power

The conservative dry-run upper bound uses 150 graphs and 63 parameter
conditions (the v3 grids plus matched nulls for E5, E5-prime, and E6):

| Quantity | Upper bound | Cap |
|---|---:|---:|
| Aggregate rows | 2,116,800 | 5,000,000 |
| Unique probability solves | 1,306,800 | 2,000,000 |
| Projected raw bytes | 17,424,875,520 | 20 GiB |

The 1% timing pilot decides the 14-day cap. The scope-cut order (GVS, P1b,
then P3) is unchanged. A cut that changes the 42-cell matrix requires a new
registered version.

**Power v5** (`docs/freeze/power_analysis_v5.md`) uses split-99 population
inputs and a grid of detection (0, 0.5, 0.9) and alarm (0.05, 0.20)
probabilities. Under every scenario, the most likely outcome is *no decision
problem at this budget* (0.67--0.78). *Improvement* has probability 0.10--0.15
even at detection 0.9, because CI-only false certification concentrates on
very few graphs (1 of 50 on split 99). This is stated in advance, and it is
why the no-problem outcome is a prespecified result rather than a failure.

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

As v3 Section 15. Because the execution code is registered, any change to a
registered file before holdout requires an implementation-error log entry with
its failing test and the before/after difference. The changed file's hash is
recorded in the confirmatory lock. Scientific mismatch is never an
implementation error.

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

Before development, verify that:
1. the protocol, matrix, code, and artifact hashes match `registration_v4.json`;
2. the full test suite and the provenance check pass;
3. no development or holdout seed has been instantiated for v4 outputs;
4. the owner has reviewed this file; and
5. the reviewed commit has an independent timestamp.

Hashes are SHA-256 of LF-normalized text (`src/hashing.py`).

## 18. Changes from v3

All changes were made before any development or holdout data. The reasons are
in `docs/freeze/pre_data_defect_audit_v3.md`.

1. **Roles:** P0 became a comparator, E0 a null control, and the primary matrix
   42 cells (P1--P5 by E1--E6 and E5-prime).
2. **Matched nulls:** each structure has a matched null (Section 3.2), used for
   visibility calibration.
3. **P4 components:** omnibus maxima were replaced by frozen component
   mappings, with E6 temporal contrasts.
4. **E2:** now acts at execution time on tagged cost rotations in all circuits,
   so folding and twins see the same miscalibration.
5. **Primary endpoint:** now decision-level (Section 11.1). Matrix agreement
   became secondary and is stratified.
6. **Matrix labels:** rederived (`06_matrix_v4.csv`); four derivation errors
   were found by semantic tests and corrected (Section 5.3).
7. **Power:** power v4, which was circular, was replaced by the non-circular
   power v5.
8. **Registration:** the complete execution code is registered with the
   protocol.
