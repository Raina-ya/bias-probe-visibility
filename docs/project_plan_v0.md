# Visibility Boundary of Bias Probes: Research Plan

This plan is not yet frozen. Every prediction in it is a hypothesis that Part 1 must derive; predictions become binding only when Part 1 freezes them. The plan contains no new numerical results. Figures quoted from the previous project come from paper/main_v2.tex and README.md of adaptive-qem-benchmark, and their evidence type is noisy simulation.

## 0. Research question

The previous project asked when quantum error mitigation (QEM) is unreliable. This project asks whether that unreliability can be detected at runtime: which probes, paid for out of the same budget, can see a differential bias that flips a decision, which cannot see it in principle, and where the boundary between the two lies.

Success criterion. The project succeeds if it draws the boundary between "the probe can see it" and "the probe cannot see it". If every probe fails, a proof of why it cannot see the bias also counts as success.

Scope of the novelty claim. Runtime diagnostics already exist for specific failure modes of specific methods; for example, the W_neg diagnostic of Koster and Mauerer (2026) needs no ideal values. In what we read, no existing diagnostic does all four of the following: (1) targets the differential bias between candidates and the top-1 decision; (2) charges the probe cost to a fixed total budget; (3) uses an alarm threshold frozen in advance and open to falsification; (4) determines under which error structures every probe is blind in principle. This project claims novelty only for the combination of these four points. The supporting analysis is in docs/inventory_20_step2_painpoints.md, section C.1.

## 1. Starting point: blind spots already observed in the previous project

All observations below are noisy-simulation evidence from the previous project.

| Observation | Source in the previous project | Role in this project |
|---|---|---|
| A confidence interval controls only the sigma term; when beta <= -Delta, more shots make the wrong answer more certain | main_v2.tex, Eq. (decision) | The starting problem |
| With gate-noise imbalance between candidates (high noise, margin 0.05), raw certifies the wrong winner in every repeat after about 2,000 shots | Certification section; README | An instance of confidence-interval-only blindness |
| The six bias alarms of two-layer certification fire in at most 2.4% of Layer-1 passes; all near ties fail; coherent over-rotation has the highest false-certification rate | Two-layer certification | An instance of weak existing probes |
| Inverse gates cancel over-rotation, so folding cannot amplify it | Signal strength section | An instance of blindness caused by symmetry (P1 under E2) |
| The condition number of the calibration matrix never gave a warning | Calibration mismatch section | A probe that reads only stale information |
| A 1,024-shot basis-state check cannot see a readout change that keeps the marginals but adds pairwise correlation | Calibration mismatch section | An instance of blindness caused by marginal invariance (P4a under E5) |

These are scattered counterexamples. This project explains them with one set of definitions and extends them to other error structures.

## 2. Core definitions

Decision. Choose the argmax among K candidates. The decisive gap is Delta_k = mu_(1) - mu_k > 0.

Decision-relevant bias. beta_k = E[gap estimate] - Delta_k. The decision flips if Delta_k + beta_k <= 0 for some k. Bias shared by both candidates (common-mode) does not affect the decision and is excluded.

Error structure. e in E, a parameterized family of noise models; each e determines a set of biases beta(e).

Probe. A probe is a set of circuits run at runtime, a statistic T, and an alarm rule.
  A probe may not read the ideal value of the target circuit. It may use quantities that do not depend on the target's ideal value and can be computed classically at runtime, such as ideal values of Clifford circuits; each probe must state which such quantities it uses.
  Its cost c(P) (number of circuits, number of shots, depth multiplier) is charged to the same total budget N. Classical post-processing time is reported separately.

Visible and blind. These are written in the form of Imbens and Manski (2004, Section 2); the check of that source is in section 2 of the reading notes.
  Following Imbens and Manski, the parameter is Delta = f(P, e), where P is the joint observable distribution of the target and probe outputs, and e is the noise, known only to lie in E.
  Identification region = {f(P, e') : e' in E}. Noise models incompatible with P are excluded by the form of P itself; E remains a fixed set. This step is our own derivation, not part of the source.
  Blind in principle: the identification region contains both positive and non-positive values.
  Blind within budget: the observable distributions differ, but they cannot be told apart with the required power within the probe budget fN.
  Visible: within the frozen probe budget, power reaches the target and false alarms are controlled.
  Assumptions that must be stated:
    (i) given P and e, the ideal gap is uniquely determined (the noise map is invertible on the relevant observables);
    (ii) when the circuits are known, the ideal gap is in principle a fixed number; we treat it as unknown because probes are not allowed to read ideal values and the target circuits cannot be simulated classically in practice.
  A formulation of the form "there exist e1, e2 with the same observable distribution but different sign(Delta + beta)" cannot hold, because the target's observable distribution already determines Delta + beta. It is therefore not used.

## 3. Theoretical work (Part 1; frozen before any noisy simulation)

### 3.1 Lemma 1: indistinguishable implies blind

What. If (Delta1, e1) and (Delta2, e2) have the same distribution over all runtime observables and Delta1 and Delta2 have opposite signs, then every decision or certification rule satisfies P_theta1(error) + P_theta2(error) >= 1.
Purpose. This is the formal version of the statement that statistical tools cannot control bias. Corollary: a confidence-interval certificate that looks only at the target estimate observes only Delta + beta, so whenever E allows a large enough beta, it cannot separate beta from Delta.
Basis. Le Cam's two-point method (lecam1973; page numbers not yet verified); identification-region language from Imbens and Manski (2004) and Tamer (2010).

### 3.2 Learnability criterion

What. Probe data can identify only the learnable components of the noise. If the sensitivity of the differential bias beta to the unlearnable components (the cut space) is large enough to offset Delta, then every combination of probes is blind in principle.
Purpose. This gives a first physical class of blindness in principle. Part 1 derives the projection of beta onto the cut space and determines which error structures fall into this class.
Basis. Chen et al. (2023), "The learnability of Pauli noise".
Status of the claim. This is a hypothesis; the derivation may refute it.

### 3.3 Local versus global identifiability

What. Prove that a local identifiability condition of the type in Scavino (2026), Corollary C.1 (a Fisher-information null-space condition), and this project's global sign criterion do not contain each other, with one counterexample in each direction: locally identifiable but globally blind; not locally identifiable but globally not blind. Both counterexamples are checked analytically or by noiseless computation.
Purpose. To state precisely how this project's notion of blindness differs from the closest existing identifiability result.
Basis. Scavino (2026), Corollary C.1. In what we read, Scavino defines theta as "an ideal-landscape instance" and does not state whether it includes noise parameters; Remark C.4 describes a converse over channel parameters as a different formulation. Corollary C.1 is therefore treated as a local condition over ideal-landscape instances under fixed primitive measurements, and the comparison covers both locality and the level of the unknown (reading notes, section 4.6).

### 3.4 Finite-shot version

What. Using total variation or Hellinger distance, write a lower bound on the number of shots needed to see a bias.
Purpose. The bound separates blindness in principle (distance zero) from blindness within budget (small distance).

### 3.5 Invariance criterion and validity condition

What. If a probe statistic is invariant under a family of perturbations G, the probe is blind to G. Every cell of the blind-spot matrix gets either an invariance proof or a derivation of the sensitivity kappa = dE[T]/dbeta != 0.
Validity condition. A cell is marked visible under a quantum condition defined by this project: the probe statistic and the target gap have nonzero sensitivity to the same noise parameters, and the probe's ideal value is known.
Basis. This condition is an analogy to the U-comparability of Lipsitch et al. (2010): the negative control and the target share the same set of unobserved common causes, and the negative control is not affected by the exposure. It may be described only as an analogy, not as the original condition; the original wording is in section 1 of the reading notes.
Reporting. For each decision, the minimum differential bias needed to flip it is also reported, in the format of Rosenbaum (1987) and VanderWeele and Ding (2017).

### 3.6 Proposition 2: is a probe worth its budget?

What. Using Proposition 1 as a template, spend fN shots on probes and (1 - f)N on the decision, and compare:
  detection power, approximately Phi(kappa |beta| sqrt(fN) / sigma_T - z_alpha);
  the cost of moving budget away from the decision: the decision error changes from Phi(-(Delta + beta) sqrt(N) / sigma) to Phi(-(Delta + beta) sqrt((1 - f)N) / sigma).
Purpose. To derive a condition for when spending on probes pays off. The result is left to the Part 1 derivation and is not assumed here.
Basis. Budget allocation uses the language of best-arm identification and OCBA (Kaufmann et al. 2016; Garivier and Kaufmann 2016; Chen et al. 2000).

### 3.7 Bias-aware certificate

What. Certify only if the lower confidence bound of the gap exceeds B, the largest bias compatible with the probe data. In a blind direction, B equals the prior bound, so the rule never certifies.
Basis. In form, this is an honest confidence interval (Armstrong and Kolesar 2020, which adjusts the critical value by a bias bound) and a confidence interval for an identification region (Imbens and Manski 2004). The worst-case bias in Armstrong and Kolesar comes from a function class fixed in advance, whereas B here comes from probe data, so coverage cannot be inherited directly. Part 1c adds a derivation of joint coverage for the probe interval and the target interval.
Purpose. Every outcome yields a positive result: either the bias is detected, or the degree to which certification is impossible is quantified.

### 3.8 Extension of Proposition 1

What. Extend Proposition 1 to K candidates, to gamma and a estimated from data, and to small samples.
Prediction test. A test of predictions made in advance is part of Part 3 and is a secondary endpoint only:
  it is run exactly once;
  Part 1 freezes the pilot procedure, the estimators of a and gamma, and the rule that predicts whether raw or ZNE is better;
  before Part 3 scoring begins, the pilot is run, the prediction for each new graph is written to a file, committed and registered (OSF or AsPredicted), and only then are the new scoring data run;
  the hit rate is reported once; the rule is not adjusted and the test is not rerun, whatever the result.

## 4. Error structure by probe matrix

The predictions below are hypotheses until Part 1 derives and freezes them.

### 4.1 Error structures

| Code | Structure | Note |
|---|---|---|
| E0 | Common-mode only (control) | Cannot flip a decision; used to measure false alarms |
| E1 | Stochastic Pauli or depolarizing noise, with different gate counts between candidates | Differential attenuation |
| E2 | Coherent over-rotation (angle dependent) | The previous project showed folding is blind to it |
| E3 | Static coherent ZZ crosstalk inserted after each hard two-qubit cycle on a fixed layout and schedule | The same parameter is shared across candidates; P1 and P2 need transfer conditions, while balanced full-Pauli P3 removes its first-order coherent mean |
| E4 | Independent, asymmetric readout error | |
| E5 | Pairwise-correlated readout with unchanged marginals | The previous project showed marginal checks are blind to it |
| E5' | Three-body correlated readout with unchanged pairwise marginals | Tests the blind spot of P4b |
| E6 | Drift between calibration and execution | |
| E7 | Combined model from a Qiskit fake backend | Labelled device-parameter simulation, not hardware evidence; measured only, no advance prediction |

Each structure is swept over bias size beta/Delta in {0, -0.5, -1.0, -1.5}, plus positive bias. The exact grid is frozen in Part 1.

### 4.2 Probes

| Code | Probe | Runtime cost |
|---|---|---|
| P0 | Confidence-interval certificate only (baseline) | No extra circuits |
| P1 | Gap folding slope: run both candidates at lambda = 1 and 3, check how the gap changes with lambda and whether the extrapolated gap changes sign | One extra circuit per candidate, depth x3 |
| P2 | Clifford twin: replace non-Clifford rotations with the nearest Clifford angle, compute the ideal value by stabilizer simulation, and measure the bias of the twin gap | One extra circuit per candidate, depth x1 |
| P3 | Twirl contrast: run each candidate plainly and in m randomized-compiling versions, and check whether the gap changes | m extra circuits per candidate |
| P4a | Readout marginal check: all-zeros and all-ones basis states | 2 circuits |
| P4b | Readout pairwise check: four basis states per qubit pair | 4 C(w,2) circuits, or fewer with a grouped design |
| P1b | W_neg: the weight of negative Richardson-extrapolated probabilities, computed from the per-scale-factor counts of folded circuits, needing no ideal values (Koster and Mauerer 2026) | Uses counts of folded circuits; no extra shots when P1's folded runs are reused (scale factors and reuse fixed in Part 1b) |
| GVS | Reference baseline: the share of covariance that survives projection onto the gap contrasts (Scavino 2026, Section 10); it contains no margins | Computed from the target counts and the contrast matrix; no extra circuits |
| P5 | Symmetry check: compute, from the target's own counts, a symmetry component whose ideal value is known (for example the global bit-flip symmetry of QAOA MaxCut); no extra circuits (Bonet-Monroig et al. 2018) | No extra circuits, no extra shots |

Positioning of P5. A symmetry check leaves a residual bias it cannot see. Scavino Alfaro (2026, arXiv 2606.15464) has already stated this as "residual undetectable-sector bias"; that residual bias is computed from a noise model and the ideal state, not detected at runtime. This project does not claim to have discovered the blind spot of P5. It claims only to place it on the same boundary map as the other probes, under a fixed budget, at the decision level, and with a global sign criterion.
Expected blind spot of P5: errors that preserve the symmetry. Hypothesis: partial for the symmetry-breaking part of E1, blind for symmetry-preserving rotations in E2, partial for readout under E4. These predictions are frozen only after the Part 1 derivation, as for every other probe.

P1b and GVS form facet F3, the comparison with existing diagnostics. Hypotheses: by its definition, W_neg targets the failure of Richardson ZNE when the signal reaches the floor, so it is expected to be blind away from the floor and under readout structures; GVS contains no margins, so by its definition it carries no bias information. Both are derived in Part 1b.

### 4.3 Predictions

Legend: V visible, B blind in principle, Pt partial or parameter dependent, ? to be derived.

| | E1 | E2 | E3 | E4 | E5 | E5' | E6 |
|---|---|---|---|---|---|---|---|
| P0 | B | B | B | B | B | B | B |
| P1 | V | B (U U-dagger cancels) | Pt (depends on the folded ZZ sensitivity) | B (folding does not amplify readout error) | B | B | Pt |
| P2 | V | Pt (bias depends on angle; the twin uses a different angle) | Pt (requires target-twin ZZ sensitivity transfer) | Pt | Pt | Pt | Pt |
| P3 | B (a Pauli channel is invariant under twirling) | V | V under the frozen balanced full-Pauli frame model | B | B | B | B |
| P4a | B | B | B | V | B (marginals unchanged) | B | Pt |
| P4b | B | B | B | V | V | B (pairwise marginals unchanged) | Pt |
| P1b | ? | ? | ? | B (folding does not amplify readout error) | B | B | ? |
| GVS | B (no margins) | B | B | B | B | B | B |

### 4.4 Failure conditions written in advance

P1: the error cancels under U U-dagger (E2, part of E3); the bias is not amplified by folding (readout); near a tie, the variance of the slope estimate is too large.
P2: the twin circuit's noise differs from the target's, for example when the error depends on the angle (E2); the twin's output distribution differs strongly from the target's, so readout bias is weighted differently.
P3: the error is already stochastic Pauli (E1); readout error (unless a separate readout twirl is used); the E3 frame set is incomplete or unbalanced, its coefficients depend on the frames, or layout/schedule changes; with small m, the contrast is swamped by sampling noise.
P4a and P4b: the order of the marginals checked is lower than the order of the actual correlation; drift happens after the probe.
P1b: the signal stays above the floor, so the arithmetic artefact W_neg detects does not occur; readout error; the source gives no formal threshold, so the threshold is set by the frozen E0 calibration.
GVS: it contains no margin information, so it cannot respond to bias by construction; it serves as a reference for what a covariance-only diagnostic sees.

## 5. Endpoints

Primary endpoint (the only one). On the holdout, the proportion of cells where the visibility prediction frozen in Part 1 (visible, partial, blind) agrees with the observed classification, with a Wilson interval.
  Observed classification: "visible" means power >= 0.8 at beta/Delta = -1.5 within the frozen probe budget, with false alarms <= 0.10 under the matching E0 control; "blind" means power <= alpha + 0.05; everything else is "partial".
  Success threshold: Wilson lower bound of the agreement rate >= 0.8.

Secondary endpoints.
  False-certification rate and unresolved rate of the bias-aware certificate versus the confidence-interval-only certificate, under the same total budget.
  For each probe, the minimum budget fraction f* needed to reach power 0.8 (the values on the boundary map).
  Hit rate of the Proposition 1 prediction test (new QAOA graphs; run once; predictions registered in advance).

Exploratory. Results under E7 (fake backend); combinations of probes; the cells of P1b and GVS (facet F3), which are evaluated under the same frozen thresholds and budget accounting but excluded from the primary endpoint.

## 6. Thresholds and sensitivity analysis (written into the frozen protocol)

| Threshold | Main value | Sensitivity values |
|---|---|---|
| Power for "visible" | 0.8 | 0.5, 0.9 |
| Alarm alpha | 0.05 | 0.01, 0.10 |
| Probe budget fraction f | 0.10 | 0.05, 0.25 |
| Bias size used for classification, beta/Delta | -1.5 | -1.0, -0.5 |
| Success threshold of the primary endpoint | 0.8 | 0.7, 0.9 |
| Near-tie margin | 0.02, as in the previous project | 0.01, 0.05 |

Every value-versus-threshold decision reports how far the value is from the threshold.

## 7. Four Parts

The order and content of the Parts are fixed before work starts and are not adjusted in light of results.

### Part 1: theory and freeze (analytic only, no noisy simulation)
Build the literature library to at least 60 verified papers.
Complete the derivations in section 3 and a proof or sensitivity derivation for every cell of the matrix in section 4.
Only after the predictions are frozen, run a power analysis by simulation to set: a holdout of at least 100 circuits; at least 50 QAOA graphs from at least 3 graph families; more than one circuit for each width and depth; the number of repeats.
Freeze: structures and parameter grid, probe implementation specifications, cost formulas, thresholds and sensitivity ranges, the split of development and holdout seeds, the primary endpoint, and an analysis code skeleton tested on synthetic data.
Register on OSF or AsPredicted; the project owner then commits and pushes.
Exit condition: the frozen protocol has a content hash and an OSF timestamp exists.
Results that hold whatever happens later: Lemma 1, the invariance criterion, Proposition 2.

### Part 2: probe implementation and development set (noisy simulation on the development set only)
Implement P0 to P5, P1b and GVS, each with a cost ledger; test that total shots equal the budget.
Positive control: cases with an analytically known beta must trigger the alarm. Negative control: under E0 the false-alarm rate must be about alpha.
Cross-check P1 with Mitiq's folding; cross-check Clifford ideal values with two stabilizer simulators.
Calibrate alarm thresholds from the E0 null distribution only, following the procedure frozen in Part 1; commit the results before Part 3.
The development-set boundary map is exploratory only. Cells that disagree with the Part 1 predictions are recorded as they are; the theory is not revised.
Build the fake-backend model.
Exit condition: thresholds committed; list of development-set mismatches written.

### Part 3: confirmatory holdout (read once)
Synthetic structures E0 to E6, plus E7 device-parameter simulation.
Compute the primary endpoint; compare the bias-aware certificate with the confidence-interval-only certificate.
Proposition 1 prediction test (secondary endpoint): pilot, then predictions written to file, committed and registered, then the scoring data, then the hit rate reported once.
Run on both Windows and Linux and compare; run logs record the numpy version and BLAS configuration.
Exit condition: results are entered in the claim ledger and can be recomputed independently from raw rows.

### Part 4: boundary synthesis, hardware decision, paper
Draw the boundary map (structure by beta/Delta by f*). Classify every failure by cause: method, resources, model, design.
Hardware go or no-go review. If the verdict is go and the specific run is explicitly authorized: run only the readout probes P4a and P4b within ten minutes, with predictions registered in advance, to test whether real readout has pairwise correlation that marginal checks cannot see. A no-go verdict is reported in the same way.
Write the paper (same format as the previous report; posted to arXiv first), and complete the claim ledger and cross-platform rebuild.

## 8. Project-wide rules

All rules of the previous project carry over: fixed total budget, freeze before running, holdout read once, failed data kept, evidence types labelled separately, no machine learning, reference values used only for scoring.
Three rules are added:
1. probes may not read ideal values and must state their cost;
2. analytic predictions are frozen before simulation, and simulation results never revise the theory;
3. every claim that a probe works also reports the structures where it fails.

## 9. Scientific concerns

1. Lemma 1 is close to mathematically obvious and may be challenged at the defence. The contribution must rest on the concrete invariances, the shot lower bound and Proposition 2, not on the lemma itself.
2. The synthetic error structures are chosen by this project and could be chosen to fit the predictions. Mitigation: the matrix is frozen first, E7 carries no prediction, and mismatched cells are reported as they are.
3. E3 (ZZ) is frozen as the static coherent insertion model in `docs/theory/06_matrix.md`. Its predictions do not generalize to time-varying, spectator-dependent, or frame-dependent crosstalk; those are model violations rather than evidence for revising the frozen matrix.
4. Scope: nine probes (P0 to P5, P1b and GVS) by eight structures by the bias grid may be too large. If the Part 1 power analysis shows it cannot be completed, the scope-cutting rule must be written at freeze time, not decided afterwards. Its priority order starts with the F3 diagnostics (GVS first, then P1b), because they do not enter the primary endpoint, and then P3.
5. P2 computes Clifford ideal values classically. It must be argued that this is not "reading ideal values": it does not depend on the target's ideal value and can be computed at runtime.
6. The Proposition 1 prediction test is placed in Part 3 as a secondary endpoint. It is related to the topic of this project but is not its main line.
7. The learnability criterion (section 3.2) depends on the theorem conditions of Chen et al. (2023). Only the abstract has been read so far, and the conditions may not apply to the non-Clifford target circuits of this project.
8. Narrow evidence and unclear generalization: in the 20-paper inventory, 8 independent sources share this problem, and this project, being mainly simulation, has it too. It is not addressed; it is acknowledged in the limitations section, conclusions are limited to existence claims, and E7 device-parameter simulation is used for sensitivity analysis.

## 10. Literature

The library is docs/literature/library.csv: 86 entries, each with a verification status and a three-line note. The 81 verified entries are in paper/references.bib; the 5 partial entries are excluded.
The literature review and research anchors are in docs/literature_review.md.
The 20-paper inventory and pain-point analysis are in docs/inventory_20_step1.md to docs/inventory_20_step4_schedule.md.
Limitation: no full text has been read word for word, so no numbers from new sources are cited yet. The reading list is in section 7 of docs/literature_review.md.
Limits literature: the paper cites Takagi 2022, Takagi 2023, Quek 2024 and Tsubouchi 2023 to answer the expected examiner question about limits of error mitigation (gamma is an instance, for a single estimator, of those lower bounds). The claim "limits theory has no decision-level counterpart" has only two sources in the 20-paper inventory and is not used as a main pain point or a pillar of novelty.

## 11. Settings adopted by this project

Task type: design the research plan in at most four Parts before running experiments.
Output format: a single paper in the same format as the previous report, posted to arXiv first; adapted to a specific journal only if one is targeted.
Repository: a separate public repository, bias-probe-visibility. The previous repository is used only as a source of citations and code and is not modified.
Proposition 1 prediction test: kept as a secondary endpoint only, run once, with predictions registered in advance (sections 3.8 and 7).
Zhou et al. 2020 (PRX) refers to the QAOA paper: PRX 10, 021067, DOI 10.1103/PhysRevX.10.021067.
Schedule rule: delays move later stages later; the content of the Parts does not change.
Part 2 starts only after the previous project is closed, so that results of both projects are not produced from a shared, still-changing code base.
The original wording of Lipsitch et al. (2010) is quoted, never paraphrased, in the paper, because a paraphrase introduced an inaccurate condition once.
Research facets: F1 visibility boundary (primary), F2 certificate with a data-driven bias bound (secondary), F3 comparison with existing diagnostics (exploratory).
W_neg as probe P1b, with GVS as a reference baseline: adopted, so that existing diagnostics are compared on the same visibility map and under the same budget accounting, which directly supports the four-condition novelty statement. The F3 comparison is done by simulation; P1b and GVS cells are exploratory and excluded from the primary endpoint.
Adopted adjustments: the local-versus-global proposition (section 3.3); the repositioning of P5 (section 4.2); the four-condition novelty statement (section 0); the narrow-evidence limitation (section 9, item 8); the treatment of the limits literature (section 10); the primary endpoint unchanged.
Decision rule: reversible, low-cost choices are made by whoever executes a task and are documented in its report; choices that touch frozen rules, widen the scope or affect the primary endpoint require approval by the project owner. Results are written directly into the repository by default.

## 12. Conditional settings

Hardware: any hardware run requires a separate, explicit authorization.

## 13. Time budget for the hardware experiment (frozen in Part 1)

Quota: according to IBM's published terms at the time of planning, the Open Plan provides up to the equivalent of 10 minutes of QPU time per rolling 28-day window, counted as QPU usage rather than wall-clock time. The terms are checked again before any run.
Only readout circuits (P4a and P4b) are run; no target circuits.
Time limit: total usage at most 6 minutes, keeping 4 minutes in reserve. Every job sets max_execution_time.
Order:
  1. run one very small job to measure the actual QPU time per shot;
  2. allocate shots from the measured value using a formula frozen in advance;
  3. if the limit would be exceeded, reduce in an order frozen in advance (first shots, then width), never decided on the spot.
Record the backend name, calibration timestamp, job IDs, and quantum_seconds for every job.

## 14. Stages

Delays move later stages later; the content of the Parts does not change. Each stage ends with a report in the eight-item format.

| Stage | Deliverables | Exit condition |
|---|---|---|
| Preparation | Literature library; close reading of the key sources (Chen 2023 and Imbens and Manski in full; Armstrong and Kolesar, Lipsitch and Scavino in their relevant passages) | Reading-depth fields in library.csv updated |
| Closing the previous project (in parallel with Part 1) | Second Linux rebuild; whether the selector_v3 numbers change; update of docs/release_rebuild_v1.md and section 8 of the previous paper; correction of the scavino2026 title | The previous project is closed before Part 2 starts |
| Part 1a: definitions and Lemma 1 | Lemma 1 in partial-identification form and the finite-shot bound; the local-versus-global proposition with two counterexamples; draft learnability criterion | Derivations written as docs/theory/*.md and self-reviewed |
| Part 1b: matrix derivation | Invariance proof or kappa derivation for every probe-by-structure cell, including P1b and GVS; validity condition; P5 predictions | Every cell has a derivation or an explicit "?" |
| Part 1c: Proposition 2 and certificate | Proposition 2; bias-aware certificate; extension of Proposition 1 (K candidates, estimated gamma) | Derivations complete; at least 90 papers in the library |
| Part 1d: freeze | Power analysis (only after predictions are frozen); frozen protocol; OSF or AsPredicted registration; commit and push by the project owner | Frozen protocol has a content hash and an OSF timestamp |
| Part 2: implementation and development set | Implementations of P0 to P5, P1b and GVS, with cost ledger; positive and negative controls; cross-checks with Mitiq and two stabilizer simulators; thresholds committed | Thresholds committed; development-set mismatch list |
| Part 3: confirmatory holdout | Holdout read once; Proposition 1 prediction test (run once); comparison of two platforms | Claim ledger recomputable from raw rows |
| Part 4: synthesis and paper | Boundary map; hardware go or no-go review (go requires separate authorization); paper; arXiv | Paper compiles, all citations verified, claim ledger has zero mismatches |

The task list, with a prompt for each task, is in docs/inventory_20_step4_schedule.md.
Part 2 starts only when Part 1d is frozen and the previous project is closed. Part 1 is analytic only and can run in parallel with closing the previous project.
If the Part 1d power analysis shows the scope cannot be completed, it is reduced using the scope-cutting rule written at freeze time (section 9, item 4), and Part 3 is not extended.
