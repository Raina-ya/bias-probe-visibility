# Common Pain Points in the Literature

This document groups the open issues recorded in the 20-paper inventory (docs/inventory_20_step1.md) into common pain points, identifies which of them this project responds to, and checks three questions that bear directly on the novelty claim.

## Method

Counting rule. A series of papers by the same author counts as one source. Entry 8 (Scavino Alfaro 2026) and entry 9 (Scavino 2026) are merged into "the Scavino series", giving 19 independent sources.
Scope. Only the 20 inventory papers are counted. Other library entries (for example Tsubouchi 2023, or Koster and Mauerer, arXiv 2605.29872) are not counted and are mentioned separately where relevant.
Threshold. A pain point is common if at least three independent sources support it. Pain points with fewer sources are listed as minor, with their actual count.
Basis labels. [passages] means relevant passages or extracted full text were read; [abstract] means the judgement rests on the abstract only.
This document classifies pain points only; research facets are set out in docs/inventory_20_step3_facets.md.

## A. Common pain points (at least three independent sources)

### Pain point 1: a method's validity depends on a specific error structure, and its failure conditions are only partly stated

Why it matters. Each method works only under some error structures, but the failure conditions are scattered across papers; some are only "expected", others are not written down. At runtime a practitioner cannot tell whether the current situation falls in a failure region, and nothing warns when it does.
Basis: 7 independent sources.
  Giurgica-Tiron 2020 [passages]: the authors state that folding may fail to amplify coherent error and state-preparation-and-measurement error.
  Wallman and Emerson 2016 [passages]: Theorem 1 requires gate-independent noise on easy gates; the proof for general noise is left open.
  Koster and Mauerer 2026 [passages]: when the signal reaches the floor, ZNE reduces to a fixed rescaling.
  Scavino series [passages]: symmetry verification leaves a "residual undetectable-sector bias".
  Maciejewski 2021 [abstract]: readout correlations are assumed not to be too nonlocal, and only marginals are corrected.
  Czarnik 2021 [abstract]: the abstract does not say when Clifford training data fail to represent the target.
  Chen 2023 [abstract]: the result is limited to Pauli noise on Clifford gates.
Project response. The probe-by-structure matrix of Part 1b, covering P1 (folding), P2 (Clifford twin), P3 (randomized compiling), P4 (readout, E5) and P5 (symmetry).
Expected output: boundary conditions. Every cell gets an invariance proof or a sensitivity derivation, with its failure condition written in advance.

### Pain point 2: bias information depends on ideal values, reference values or a prior model, and is not directly available at runtime

Why it matters. Bias is exactly what flips a decision, yet most theories treat it as known or require ideal values and a correct noise model to compute it. None of these is available at runtime.
Basis: 3 independent sources, plus one weaker source.
  Scavino series [passages]: entry 9 takes â_m as an input to Algorithm 1 and, in what we read, does not state how it is obtained; in entry 8 the bias coefficients depend on the ideal state, the observable and the noise model.
  Armstrong and Kolesar 2020 [passages]: the worst-case bias comes from a function class F(M) fixed in advance, so M must be known.
  Koster and Mauerer 2026 [passages]: the recovery ratio rho needs the ideal value (the paper also proposes W_neg, which does not).
  Weaker: Cirstoiu 2023 [abstract] uses classical simulation as the evaluation reference. This is evaluation after the fact, not runtime, and is not counted toward the threshold.
Project response. Part 1a (definition of the identification region), Part 1c (bias-aware certificate, with B set by probe data), probes P1 to P5.
Expected output: a proposition (when bias can be identified from runtime data) and a method (the probes).

### Pain point 3: controlling sampling error or improving average metrics does not control the bias that flips a decision

Why it matters. A decision can be wrong while the confidence interval, the MSE and the average improvement all look good, and more shots make it wrong with more certainty. The previous project found the same, but it is not counted here.
Basis: 4 independent sources.
  Scavino series [passages]: entry 9 states "pointwise marginals, variances, confidence intervals, and MSE do not suffice"; the certification in entry 8 mainly addresses sampling error.
  Koster and Mauerer 2026 [passages]: "a bogus apparent improvement that is independent of noise amplification".
  Armstrong and Kolesar 2020 [passages]: conventional intervals that ignore estimator bias lose coverage, so the critical value is adjusted by the bias.
  Bultrini 2023 [abstract]: only estimation accuracy is compared.
Project response. Lemma 1 in Part 1a; the bias-aware certificate in Part 1c; P0 (the confidence-interval-only baseline).
Expected output: a proposition (Lemma 1: a certificate that looks only at the target is blind to any admissible bias) and a comparison (bias-aware certificate versus confidence-interval-only).

### Pain point 4: benchmarks stop at estimation accuracy and do not evaluate downstream decisions

Why it matters. Better accuracy does not guarantee a better decision, and most benchmarks do not check this.
Basis: 4 independent sources.
  Bultrini 2023 [abstract]: only estimation accuracy is compared.
  Cirstoiu 2023 [abstract]: how the guidance on when mitigation helps was validated was not seen.
  Takagi 2022 [abstract]: only estimation error and sampling cost are treated.
  Quek 2024 [abstract]: only estimation error and sampling cost are treated.
  Not counted: Sarovar 2020 [abstract] does not discuss decisions, but it is a characterization protocol, not a benchmark. The Scavino series is not counted, because entry 9 does evaluate decisions.
Project response. The decision-level setting of this project (top-1 selection); the Proposition 1 prediction test in Part 3.
Expected output: a comparison table and a proposition (the extension of Proposition 1).
Note. Scavino 2026 already addresses the point that accuracy is not the same as a good decision, so this pain point is background and positioning, not a source of novelty.

### Pain point 5: identifiability results are either local or limited to particular noise classes, and are not connected to decisions

Why it matters. Tools exist for deciding what cannot be seen in principle, but none answers this question: for a concrete top-1 decision, under what conditions does bias flip the decision globally such that no probe can rule it out?
Basis: 4 independent sources.
  Chen 2023 [abstract]: the cut space cannot be learned, but only for Pauli noise on Clifford gates.
  Nielsen 2021 [abstract]: gauge freedom exists, but its effect on decision quantities was not read and cannot be judged.
  Imbens and Manski 2004 [passages]: an identification region is given, but the admissible set is fixed in advance, and partial identification is not formally defined in the paper.
  Scavino series [passages]: Corollary C.1 is a local condition (Fisher-information null space).
Project response. Lemma 1 in Part 1a (a sign condition on the identification region) and the learnability criterion (research plan, section 3.2).
Expected output: a proposition and boundary conditions (see the local-versus-global analysis in C.2).

### Pain point 6: diagnostics and controls lack a formal, falsifiable decision threshold

Why it matters. Without a threshold frozen in advance, diagnostic results are easily interpreted after the fact and cannot be falsified.
Basis: 3 independent sources, exactly at the threshold.
  Koster and Mauerer 2026 [passages]: the authors state that W_neg has no formal threshold and was validated only on the circuits studied.
  Lipsitch 2010 [passages]: U-comparability is stated in degrees ("To the extent that … overlaps"); no quantitative test was seen.
  Scavino series [passages]: entry 9 states "The ratio GVS is only a diagnostic".
Project response. Thresholds and their sensitivity are frozen in Part 1d; alarms are calibrated on the E0 null distribution in Part 2; the holdout is read once in Part 3.
Expected output: a method (frozen alarm rules with threshold sensitivity) and a comparison (agreement rate on the holdout).

## B. Minor pain points (fewer than three independent sources)

### Minor pain point 1: limits theory of error mitigation stops at the estimator level, with no decision-level counterpart

Basis: 2 independent sources (Takagi 2022 [abstract]; Quek 2024 [abstract]). Support is insufficient, so this is a minor pain point.
Note. Within the 20 papers there are only these two. Tsubouchi 2023 is not among the 20 and is not counted. Takagi, Tajima and Gu 2023 is by the same group as Takagi 2022 and would be merged with it.
Consequence. The answer to the expected examiner question on limits still needs these two papers, but "limits theory lacks a decision level" cannot serve as a main pain point or a pillar of novelty.
Project response. When Proposition 1 is extended, it is explained that gamma is an instance, for a single estimator, of these lower bounds.

### Minor pain point 2: the cost of characterization and detection protocols is not charged to the decision budget

Basis: an inference from Sarovar 2020 [abstract] and Proctor 2022 [abstract]. Neither abstract discusses cost or budget; this is "not seen", not a statement in the papers.
Note. Two sources, and of the "not seen" kind, so it is minor.

## C. Three checks that bear on the novelty claim

### C.1 Runtime detection of differential bias: has it already been done?

Koster and Mauerer 2026, W_neg [passages]
  Runtime diagnostic without ideal values: yes; W_neg uses only the counts at each lambda.
  Target: artefactual improvement of Richardson ZNE when the signal reaches the floor (one method, one failure mode).
  Cost charged to a fixed budget: it uses counts already collected, at no extra cost; budget allocation is not discussed.
  Frozen, falsifiable threshold: no; the authors state there is no formal threshold.
  Targets differential bias between candidates and the decision: not seen; it targets a single estimate.

Scavino 2026, Decision Kernels [passages]
  Runtime diagnostic without ideal values: in what we read, there is no bias diagnostic. DRI and GRI need the margins mu_m (the true gaps); GVS needs no reference values but does not include the margins.
  Target: decision risk and covariance structure.
  Cost charged to a fixed budget: fixed total budget.
  Frozen, falsifiable threshold: not applicable.
  Targets the decision: yes, but bias is an input.

Scavino Alfaro 2026, Certified Operating Windows (arXiv 2606.15464) [passages]
  Runtime diagnostic without ideal values: partly. Clip events of the virtual-distillation denominator are monitored, and a crossing must pass a self-consistency test. The residual bias, including the "residual undetectable-sector bias", is computed from a model and the ideal state; the extracted text describes its diagnostics as offline checks against exact or simulated data.
  Target: stability of the virtual-distillation denominator; whether the local laws of the method comparison hold.
  Cost charged to a fixed budget: no; the budget B is a variable.
  Frozen, falsifiable threshold: there is a threshold (a sample-size threshold for the denominator), but it concerns sampling, not bias.
  Targets differential bias between candidates and the decision: no; estimator MSE is compared.

Conclusions
  The gap can no longer be stated as "no runtime diagnostic exists". The W_neg diagnostic of Koster and Mauerer is a runtime diagnostic that needs no ideal values; it targets a single failure mode of ZNE.
  Restated gap, qualified by "in what we read": existing diagnostics each target a specific failure mode of a specific method, and either lack a formal threshold or depend on a model and ideal values. In what we read, none satisfies all four of the following:
    1. targets the differential bias between candidates and the top-1 decision;
    2. charges the probe cost to a fixed total budget;
    3. uses an alarm threshold frozen in advance and open to falsification;
    4. determines under which error structures every probe is blind in principle.
  W_neg is included as probe P1b in the P1 family, and GVS as a reference baseline, both evaluated in the same matrix (research facets, F3).

Positioning of arXiv 2606.15464
  It does not detect residual bias at runtime; the residual bias is computed from a model and the ideal state. It is therefore not a precedent for runtime detection by P5.
  It does state that symmetry verification leaves a "residual undetectable-sector bias", so the fact that a symmetry check cannot see part of the bias has already been pointed out. The novelty of P5 is therefore positioned as follows:
    it cannot be claimed that this project discovered the P5 blind spot;
    the claim is that the P5 blind spot is placed on the same visibility boundary map as the other probes, under a fixed budget, at the decision level, and with a global sign criterion.
  Accordingly, entry 8 in the inventory is classified as contrast (existing evidence for the predicted P5 blind spot; not runtime detection).

### C.2 Local versus global identifiability: how does Corollary C.1 relate to this project's "blind"?

Scavino's Corollary C.1 [passages]. Assuming the primitive laws are smooth, if "Gh = 0 for every h ∈ ker Ī(w, θ)", then "the target gaps are identifiable under the chosen primitive measurements". It applies "in the locally efficient, identifiable, small-margin, and realizable case" and is used to derive an error exponent.
This project's definition. The case is blind in principle when the identification region {f(P, e') : e' in E} contains both positive and non-positive values.
Assessment (an inference, to be written as a formal proposition with counterexamples in Part 1a): the two are different conditions, and neither contains the other.
  1. Locally identifiable but globally blind: near the true parameter the gap is identifiable, but a distant, observationally equivalent parameter may give a gap of opposite sign. A local condition cannot see this.
  2. Not locally identifiable but globally not blind: the gap is not uniquely determined locally, but if the margin is large enough, every observationally equivalent parameter gives a gap of the same sign, so the direction of the decision is still determined.
  3. Only in the small-margin limit do the two come close, and the scope of Corollary C.1 is exactly the small-margin case.
Open point, now settled as far as the text allows. Whether Scavino's theta includes noise parameters is not stated in what we read: theta is described as an "ideal-landscape instance", and Remark C.4 treats a converse at the level of channel parameters as a different formulation (reading notes, section 4.6). Corollary C.1 is therefore not presented as a local version of our "visible" condition; the comparison covers both locality and the level of the unknown.

### C.3 Estimator-level limits versus decision-level consequences: are two sources enough for a main pain point?

No. Within the 20 papers, only Takagi 2022 and Quek 2024 support it; it is listed as minor pain point 1 with insufficient support.
Pain point 4 (benchmarks stop at estimation accuracy) also includes these two papers, but it has two further independent sources (Bultrini and Cirstoiu), so pain point 4 stands on its own.
Pain point 4 and minor pain point 1 are stated separately; the minor pain point is not merged into pain point 4 to raise its count.

## D. Outside the scope of this phase

Narrow evidence base and unclear generalization. Supported by 8 independent sources: Koster and Mauerer [passages], the Scavino series [passages], Quek [passages], Maciejewski [abstract], Czarnik [abstract], Hashim [abstract], Bonet-Monroig [abstract], Bultrini [abstract]. Reason: this project is mainly simulation, with hardware limited to a separately authorized readout experiment, so it shares the same limitation and cannot resolve it. It is acknowledged in the limitations section, conclusions are limited to existence claims, and E7 device-parameter simulation is used for sensitivity analysis.

Complete correction of correlated readout (Maciejewski corrects only marginals). Reason: this project detects bias; it does not mitigate it.

A full proof of randomized compiling under general noise (an open problem stated by Wallman and Emerson). Reason: it belongs to the theory of randomized compiling; this project only uses its invariance in deriving probe properties.

Worst-case versus typical-case limits (stated by Quek et al.). Reason: it belongs to estimator-level limits research, not to the decision level.

Scalability and cost of GST and other characterization protocols (Nielsen, Proctor, Sarovar). Reason: dedicated work already exists; this project borrows only their identifiability and detection concepts.

Statistical rigour of error-mitigation benchmarking (the topic of Koster and Mauerer, arXiv 2605.29872, not among the 20). Reason: it is already addressed elsewhere; this project adopts the recommended practices (freezing, sensitivity analysis, drift records).
