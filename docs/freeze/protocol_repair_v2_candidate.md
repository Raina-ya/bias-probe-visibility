# Protocol repair v2 candidate

Status: owner-directed repair candidate for task 1d-2R, written on
2026-11-12. It is **not frozen, committed, or preregistered**. No noisy
development or holdout simulation is authorized until this file, a regenerated
power analysis, the analysis skeleton, and their hashes have been reviewed by
the owner, committed, and independently timestamped.

This document is a normative addendum to `frozen_protocol_v1.md`. Every v1 rule
not mentioned here remains unchanged. If the two documents conflict, this
document controls. A later registration artifact must combine them into one
self-contained protocol; this addendum is not itself the final registration
document.

## 1. Why v1 cannot be frozen

The repair closes these pre-simulation inconsistencies:

1. analytic sensitivity and finite-budget visibility were conflated;
2. the v1 P4b statistic could not detect independent assignment error E4;
3. the P5 projector derivation did not match its measured distribution score;
4. E6 did not specify a reproducible temporal design;
5. P0 had no operational alarm event;
6. the bias-aware bound `B(D_P)` was not executable;
7. target scoring, compilation, gap, and tie rules were incomplete;
8. post-generation ratio bins could yield zero or multiple rows per graph;
9. the endpoint ignored shared-graph dependence and used an unsupported
   uniform-visibility interpretation;
10. zero-cost probes were omitted from the `f*` endpoint;
11. resource caps were not fixed before the dry run; and
12. the hardware shot-allocation formula was missing.

The old v1 protocol and power-analysis files remain in the audit trail. They are
not overwritten or described as confirmatory evidence.

## 2. Decision object and compilation contract

For graph `G=(V,E)` and bit string `z`, the per-shot score is the normalized
MaxCut value

\[
s_G(z)=|\{(i,j)\in E:z_i\ne z_j\}|/|E|\in[0,1].
\]

Each candidate mean is the expectation of this score. Let `g=mu_A-mu_B`.
The ideal top candidate is `A` when `g>0`, `B` when `g<0`, and tied when
`g=0`. The ideal gap used for scoring is `Delta=abs(g)`. The observed winner is
defined by the sign of the noisy sample gap; an exact sample tie is unresolved.

An exact ideal tie, `Delta <= 1e-12`, is never regenerated. In the holdout it is
retained as an unsuccessful graph-level trial for every affected alternative.
The prespecified near-tie flag is

\[
\Delta/\max(|\mu_A|,|\mu_B|,10^{-12})\le0.02.
\]

It is reported as a subgroup and never removes a primary row.

Compilation uses the basis `rz,sx,x,cx`, identity initial layout, routing
method `none`, optimization level 0, and the derived `seed_transpiler`. The
candidate-1 `CX-CX` identity pair is inserted after transpilation inside
barriers after each cost layer. A structural assertion must verify that every
pair remains in the final circuit. Package versions and the transpiler output
hashes are part of the immutable manifest; failure of the assertion is a hard
stop, not permission to change optimization.

## 3. Prediction meaning and repaired matrix

The matrix labels are hypotheses about the frozen operational statistics at the
frozen budget. Analytic sensitivity is necessary motivation, not evidence of
finite-budget power. The primary estimand is **design-distribution visibility**:
power and false-alarm rates averaged over the prespecified graph mixture. No
claim of uniform visibility over all graphs or all parameters is made.

The repaired authoritative matrix is `docs/theory/06_matrix.csv`, SHA-256
`7a8e3a56e6f48d8a29c3643c1c2e24f46bce6a54c674d6b1937dbdcd041d8995`.
It contains 35 blind, 15 partial, and 6 visible primary cells. The count changed
because the operational P5 statistic is invariant under the concrete frozen
E1, E2, E3, E5, and E5-prime models. The v1 power analysis, which used the old
30/20/6 counts and independent-cell approximation, is superseded and must be
regenerated before freeze.

## 4. Operating-point selection without holdout tuning

The target design ratios are `q in {-1.5,-1.0,-0.5,+0.5}`. E0 remains the
zero-bias control. For each non-null structure and target `q`, development data
alone choose one physical strength from the already listed v1 grid. The chosen
strength minimizes

\[
|\operatorname{median}_{\rm development}(\beta/\Delta)-q|.
\]

Exact ideal ties are omitted only from this development median. Ties between
strengths go to the smaller absolute strength and then the smaller signed
value. The selected map, realized development medians, distances, and input
hashes are written to `docs/freeze/strength_map_v2.csv` and frozen before any
holdout seed is instantiated.

If the closest development median is more than 0.25 from its target, that
structure/target operating point is declared unattainable before holdout. Its
primary cells are not rescued by adding strengths; they remain in the 56-cell
denominator as disagreements. Otherwise every holdout graph is evaluated at
the one fixed mapped strength. There is no post-holdout bin filtering or
nearest-row selection. The complete realized holdout ratio distribution is
reported only as a diagnostic.

This is the sole exception to v1's statement that exact references are used
only for scoring: development ideal values may construct the strength map.
They still never enter a probe, set an alarm threshold, select a graph, or
change a holdout strength.

## 5. Repaired operational probes

### 5.1 P0

With target shot counts `n_A,n_B`, let `g_hat` be the difference of the two
normalized sample means and define

\[
h_i=\sqrt{\log(4/\alpha_T)/(2n_i)},\qquad
L_T=|\widehat g|-h_A-h_B.
\]

The main target confidence allocation is `alpha_T=0.025`. P0's operational
alarm is `A_0=1{L_T<=0}`: it says that the CI-only rule is unresolved. It is not
called a bias detector, and a confidently wrong noisy winner remains its frozen
blind spot. An exact sample tie also alarms/unresolves.

### 5.2 P4b

For each pair and each of its four prepared basis states, retain the full pair
counts. Define

- `T_marg`: the maximum absolute difference between an observed one-qubit
  assignment probability and its prepared bit value; and
- `T_corr`: the maximum total-variation distance between an observed pair
  distribution and the product of its observed one-qubit marginals.

The P4b score is `T_4b=max(T_marg,T_corr)`. Its single E0-calibrated threshold
therefore controls multiplicity of the composite maximum without a second
post-hoc threshold. Circuit and shot costs are unchanged from v1 except for the
E6 bracketing rule below.

### 5.3 P5

For each candidate distribution `p_hat`, compute
`T_sym=0.5*sum_z abs(p_hat(z)-p_hat(bitwise_not(z)))`. P5 uses the maximum over
the two candidates and, for E6, the same maximum in each prespecified temporal
half plus the absolute difference between the two half-scores. It reuses target
counts and has `f=0`. The derivation and repaired predictions are in
`docs/theory/06_matrix.md`.

All other probe statistics remain as in v1. Every score is a single
prespecified composite maximum calibrated as a whole on development E0.

## 6. E6 temporal design

E6 is a linear readout-drift path over normalized execution time `t in [0,1]`:

\[
e_0(t)=0.04+\delta t,\qquad e_1(t)=0.06-\delta t,
\]

with the unchanged grid
`delta in {+/-0.005,+/-0.010,+/-0.020,+/-0.030}`. All probabilities remain in
`[0,1]` on this interval.

Each run has eight equal temporal blocks. Remainder shots go to earlier blocks.

- P4a and P4b split probe shots equally between blocks 0 and 7; target shots
  occupy blocks 1--6 in canonical candidate order.
- P1, P2, and P3 cycle their target and probe circuit identities through all
  eight blocks using a seed-derived permutation followed by its reverse. Each
  circuit receives shots in both halves whenever its allocation is at least 2.
- P0 and P5 split each target candidate across all eight blocks. P5's temporal
  halves are blocks 0--3 and 4--7.

The exact circuit/block/shot ledger is raw data. A circuit that cannot receive
the required temporal coverage makes the run invalid; it does not authorize a
different order. E6 remains partial because the schedule can reveal a measured
change but cannot rule out a blind or post-bracket component.

## 7. Executable bias-aware certificate

The total false-certification level is 0.05, split as
`alpha_T=alpha_P=0.025`. `L_T` is the simultaneous Hoeffding lower bound in
Section 5.1 for the sample-selected winner.

The initial validated transfer envelope is deliberately narrow. It applies
only to P4a/E4 and P4b/E4,E5, including the E6 paths composed from those
readout models. For every other probe/structure cell, set `B(D_P)=+infinity`
and return unresolved. This is a negative result, not a missing-data value.

For an applicable cell:

1. construct simultaneous Clopper--Pearson intervals for every retained probe
   event probability, using Bonferroni allocation of `alpha_P` over all events;
2. let `C_P(D_P)` be the frozen finite readout-parameter grid whose predicted
   event probabilities all lie in those intervals;
3. for graph score vector `c` and full assignment channel `M_e`, set

   \[
   v_e=c^T(M_e-I),\qquad b_G(e)=\max_j(v_{e,j})-\min_j(v_{e,j});
   \]

4. set `B(D_P)=sup_{e in C_P(D_P)} b_G(e)`.

The supremum is exhaustive over the finite frozen grid and all `2^w` basis
columns; no local optimizer is permitted. Empty confidence sets, failed
enumeration, unvalidated models, or unbounded directions all return
`B=+infinity`. The bias-aware rule certifies only when `L_T>B(D_P)`. This bound
covers readout-induced differential bias within the declared model; it does not
certify the absence of gate or state-preparation bias.

## 8. Estimation and dependent primary endpoint

For each cell, power is the mean alarm indicator over all 100 graph clusters
and their 32 repeats at the fixed main strength. Matching E0 false-alarm rate is
computed from the same graph manifest. Repeats do not create new graph
clusters. The observed labels retain v1's point rules: visible requires power
at least 0.80 and false alarms at most 0.10; blind requires power at most 0.10;
otherwise partial.

The primary point estimate remains the agreement fraction over 56 cells.
Unattainable or invalid cells count as disagreements. Its 95% interval is no
longer a Wilson interval over correlated cells. Use 10,000 stratified graph-
cluster bootstrap resamples, resampling graph identities within each of the 25
width-depth strata and recomputing every cell label and the final agreement
fraction. The same resampled graph indices are shared across probes and
structures. Percentile endpoints use NumPy's `method="inverted_cdf"`. The root
seed namespace is fixed in the analysis contract. Success still requires the
bootstrap lower endpoint to be at least 0.80.

This endpoint is mixture-average, not uniform. Minimum power by width-depth
stratum is reported as a secondary limitation and cannot replace the primary
result.

For `f*`, P0 and P5 are evaluated at `f=0`; if either meets the operating rule,
report `f*=0`. Positive-cost probes use `{0.05,0.10,0.25}` as in v1. No
interpolation is allowed.

## 9. Resource contract and scope cut

Before noisy development, the deterministic dry run must meet all of these
fixed caps:

- at most 2,000,000 unique circuit/channel probability solves after immutable
  probability caching;
- at most 5,000,000 aggregate repeat rows;
- at most 20 GiB projected uncompressed raw output; and
- at most 14 elapsed days for the complete development plus holdout simulation
  on the declared reference workstation.

Shot repeats must reuse cached probabilities and draw new multinomial counts;
they must not rerun an identical statevector/density-matrix solve. One aggregate
raw row represents one graph/probe/structure/parameter/repeat and contains the
complete circuit-level count and cost ledger. The dry-run estimator is
`src/protocol_contract.py`; its tested output is required before owner review.

If the structural caps fail, use v1's removal order. If the structural caps pass
but a 1% development-only timing pilot projects more than 14 days, stop for
owner review before the remaining development run. No holdout seed may be used
for timing. No scope cut occurs after development outcomes are observed.

## 10. Hardware allocation formula

Hardware remains unauthorized. If a later, separately authorized go review
passes, first run the fixed pilot and record `S_pilot` shots and its reported
`q_pilot` QPU seconds. With a six-minute cap and a 30-second reserve, use the
conservative rate `r=1.25*q_pilot/S_pilot` and set

\[
S_{remaining}=\left\lfloor
\max(0,360-q_{pilot}-30)/r
\right\rfloor.
\]

Split remaining shots equally over the already selected P4a/P4b circuits;
remainders follow canonical probe, pair, preparation order. If this gives fewer
than 100 shots per circuit, the verdict is no-go. The formula may reduce shots
and then width as already prescribed, but it may not exceed 360 reported QPU
seconds or substitute an unmeasured time-per-shot assumption.

## 11. Exit criteria for task 1d-2R

The repair is complete only when all of the following hold:

1. matrix prose, CSV, and protocol hashes agree;
2. the new power analysis uses the 35/15/6 matrix and shared-cluster endpoint;
3. dry-run cost and seed tests pass without generating noisy outcomes;
4. the artifact registry verifies every registered hash and generator;
5. no holdout seed or noisy development outcome has been instantiated; and
6. the owner has reviewed the combined self-contained v2 protocol.

