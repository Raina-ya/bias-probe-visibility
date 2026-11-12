# Task List

This document turns the research facets (docs/inventory_20_step3_facets.md) into an ordered list of tasks. Each task states what is to be done, why, on what basis, what it produces and when it counts as done, and gives a prompt that can be pasted directly into an AI assistant.

The order of tasks matters; there is no calendar. If a task takes longer, later tasks move later, and their content does not change.

## Basis of this task list

Plan settings: the local-versus-global proposition, the repositioning of P5, the four-condition novelty statement, the narrow-evidence limitation, the treatment of the limits literature, and W_neg as probe P1b with GVS as a reference baseline are adopted; the primary endpoint is unchanged.
Research facets: F1 visibility boundary (primary endpoint), F2 certificate with a data-driven bias bound (secondary), F3 comparison with existing diagnostics (exploratory).
Pain points are numbered as in docs/inventory_20_step2_painpoints.md: pain points 1 to 6, minor pain points 1 and 2.
Part 2 can start only after Part 1d is frozen and the previous project (adaptive-qem-benchmark) is closed.

## Rules that apply to every task

Each prompt below repeats these rules, so that it can be used on its own. They are listed here once for review.

  R1. Never commit, push or reset. Give the git commands to the user instead. Never run git on the user's computer.
  R2. No machine learning. No hardware runs unless the user explicitly authorizes that specific run.
  R3. Never invent citations, numbers or results. Check every new citation online (authors, venue, volume, DOI). If it cannot be checked, mark it "unverified" and keep it out of references.bib.
  R4. A probe must never read the ideal value of the target circuit. Every probe states its cost in circuits and shots.
  R5. Analytic predictions are frozen before any noisy simulation. Simulation results never change the theory; a mismatch is reported as a failed prediction.
  R6. Every claim that a probe works must also list the error structures where it fails.
  R7. Label evidence by type: analytic, noiseless simulation, noisy simulation, device-parameter simulation (fake backend), hardware. A fake backend is not hardware evidence.
  R8. Write results directly into the repository unless there is a specific reason not to; in that case, say why.
  R9. When finished, report in eight items: files created or changed, experiment grid actually run, verification results, supported findings, negative or inconclusive findings, remaining scientific concerns, whether the next task can start, commit hash if the user has committed.

## Preparation (before Part 1a)

### Task W0-1: Apply the adopted settings to the research plan

What to do. Apply the adopted plan settings to the research plan: the local-versus-global proposition, the repositioning of P5, the four-condition novelty statement, the narrow-evidence limitation and the treatment of the limits literature.
Purpose. Keep the research plan consistent with the settings derived from the pain-point analysis before Part 1a begins.
Basis. docs/inventory_20_step3_facets.md, section 2; docs/inventory_20_step2_painpoints.md, section C.
Status. Complete; its result is the current research plan.
Expected output. Docs/project_plan_v0.md and section 6 of docs/literature_review.md.
Acceptance criteria. The only changes are the text of the adopted settings, the recorded settings in sections 11 and 12, and the schedule note. Endpoints, thresholds, probes and the number and order of Parts are unchanged.
Pain points and facets served. The adopted plan settings; pain points 1 and 5; minor pain point 1.
Prompt. None; the task is complete.

### Task W0-2: Read Scavino, Appendix C: what does theta contain?

What to do. Determine from the original text whether theta in Scavino's primitive laws includes noise parameters.
Purpose. The exact relation between Corollary C.1 and this project's definition of blindness depends on it, and the local-versus-global proposition (task 1a-4) cannot be finalized without it.
Basis. Scavino (2026), arXiv 2607.02888, Appendix C and Section 9; Corollary C.1.
Status. Complete. Result: not stated in what we read; see section 4.6 of docs/reading_notes_key_sources.md.
Expected output. An addendum to section 4 of docs/reading_notes_key_sources.md, or a separate notes file.
Acceptance criteria. The question "does theta include noise parameters?" is answered with verbatim quotes. If the paper does not say, the answer is "not stated in what we read", with the range of text read.
Pain points and facets served. F1, pain point 5, local-versus-global proposition.
Prompt:

    Task: Read Appendix C and Section 9 of arXiv 2607.02888 (Scavino, "Decision Kernels for Quantum Error Mitigation") and answer one question: what does theta in the primitive laws p_{s,theta} contain, and in particular, does it include noise parameters?
    Inputs: https://arxiv.org/pdf/2607.02888 ; section 4 of docs/reading_notes_key_sources.md in the bias-probe-visibility repository.
    Output:
      (a) verbatim quotes, each with its section or equation number;
      (b) a one-line conclusion that is exactly one of: "theta includes noise parameters", "theta does not include noise parameters", "not stated in what we read";
      (c) what this means for the relation between Corollary C.1 and this project's definition of "blind" (if theta includes noise parameters, Corollary C.1 is a local, point-value version of our "visible" condition).
    Do not: use speculative wording; present a paraphrase as a quote; write "the paper does not do X" (write "not stated in what we read"); commit or push.
    Write the result into the repository. Report in the eight-item format.

### Task W0-3: Decide on W_neg as probe P1b (decision by the project owner)

What to do. Obtain a decision on the extension that adds W_neg to the probe set as P1b, with GVS as a reference baseline.
Purpose. Part content cannot change after Part 1a begins, so the option must be settled before then; it determines whether F3 is compared by simulation or as text.
Basis. Koster and Mauerer (2026), arXiv 2607.09360; Scavino (2026), Section 10; docs/inventory_20_step3_facets.md, section 2.
Expected output. One line recording the decision in section 11 of the plan.
Acceptance criteria. The project owner answers "adopt" or "reject". No answer before Part 1a starts counts as reject.
Status. Complete. Result: adopted; recorded in section 11 of docs/project_plan_v0.md.
Pain points and facets served. F3, pain point 6.
Prompt:

    Task: Before Part 1a starts, remind the user to decide the optional extension: whether to add the W_neg diagnostic of Koster and Mauerer (arXiv 2607.09360) to the probe set as P1b, with Scavino's GVS as a reference baseline.
    Input: the subsection on W_neg as probe P1b in section 2 of docs/inventory_20_step3_facets.md.
    Output: one short message stating the cost (more derivation work in Part 1b; the probe set grows from 7 to 9; the scope-cutting rule must be rewritten) and the benefit (it directly supports the four-condition novelty statement). Ask for a plain answer, adopt or reject.
    Do not: decide for the user; change the plan before the user answers.
    Report: the user's answer verbatim and the line to add to section 11 of the plan.

## Part 1a: definitions and Lemma 1 (analytic only)

### Task 1a-1: Definitions

What to do. Write the core definitions: identification region, blind in principle, blind within budget, visible, with the assumptions that must be stated.
Purpose. Every later result depends on these definitions, and identifiability results in the literature are local or not connected to decisions (pain point 5).
Basis. Imbens and Manski (2004), Section 2; the reading notes, section 2; research plan, section 2.
Expected output. Docs/theory/01_definitions.md
Acceptance criteria.   the identification region, blind in principle, blind within budget, and visible are all defined;
  each definition is marked either with its source (Imbens and Manski 2004, Section 2) or as "this project's definition";
  two assumptions are stated: (i) given the observable distribution P and the noise e, the ideal gap is uniquely determined; (ii) the ideal gap is a fixed number in principle, and treating it as unknown is a modelling choice;
  the user's review of Imbens and Manski has been included.
Pain points and facets served. F1, pain point 5.
Prompt:

    Task: Write the core definitions for this project. Analytic work only.
    Inputs: section 2 of docs/project_plan_v0.md; section 2 of docs/reading_notes_key_sources.md (the check of Imbens and Manski); the user's own review notes on Imbens and Manski and on Chen et al. 2023. Ask the user for these notes; do not guess their content.
    What to do: following the form used by Imbens and Manski, write the gap as Delta = f(P, e) and define the identification region as {f(P, e') : e' in E}. Then define "blind in principle", "blind within budget" and "visible". P is the joint observable distribution of the target and probe outputs.
    Output format: Markdown with LaTeX. After each definition write either "Source: ..." or "This project's definition". End with a section "Assumptions that must be stated" listing (i) and (ii), and stating that the probes change P while the noise set E stays fixed; say clearly that this last step is our own derivation.
    Do not: present our derivation as the source's; cite unverified work (for example, Rothenberg 1971 must not be cited until verified); run any simulation; commit or push.
    Write the result into the repository. Report in the eight-item format, and also list every "this project's definition" so the user can approve each one.

### Task 1a-2: Lemma 1 and its proof

What to do. State and prove Lemma 1 and its corollary for confidence-interval-only certificates.
Purpose. To give the formal version of the statement that controlling sampling error does not control decision-flipping bias (pain point 3), on the basis of the identification region (pain point 5).
Basis. The standard two-point argument (source to be verified before citation); docs/theory/01_definitions.md; research plan, section 3.1.
Expected output. Docs/theory/02_lemma1.md
Acceptance criteria.   the statement and proof are complete: if the identification region contains points of opposite sign, then for any rule P1(error) + P2(error) >= 1;
  the corollary is stated: a certificate that looks only at the target is blind to any bias large enough within the allowed noise set;
  any source for the two-point argument is verified before it is cited.
Pain points and facets served. F1, pain points 3 and 5.
Prompt:

    Task: Write the statement and full proof of Lemma 1.
    Inputs: docs/theory/01_definitions.md; section 3.1 of docs/project_plan_v0.md.
    What to do: prove that when the identification region contains both a point with Delta > 0 and a point with Delta <= 0, every decision or certification rule satisfies P_theta1(error) + P_theta2(error) >= 1. Then derive the corollary that a confidence-interval-only certificate is blind.
    Output format: Markdown with LaTeX, in this order: statement, proof, corollary, conditions under which it holds, cases where it does not apply.
    Do not: cite page numbers of Le Cam 1973 or any unverified source (if you cite the two-point method, verify the source online first; if you cannot, mark it "unverified" and call it "the standard two-point argument"); use simulation to support the proof; commit or push.
    Write the result into the repository. Report in the eight-item format, and also list every assumption used in the proof.

### Task 1a-3: Finite-shot lower bound

What to do. Extend Lemma 1 to a finite number of shots and derive a lower bound on the shots needed to distinguish two parameter values.
Purpose. To separate blindness in principle (distance zero) from blindness within budget (small distance), which F1 needs for its classification.
Basis. Total variation and Hellinger distance between product distributions (textbook inequalities, to be verified before citation); research plan, section 3.4.
Expected output. Docs/theory/03_finite_shot_bound.md
Acceptance criteria. A lower bound on the number of shots needed to tell two parameter values apart is written using total variation or Hellinger distance, and the text clearly separates distance zero (blind in principle) from small distance (blind within budget).
Pain points and facets served. F1.
Prompt:

    Task: Extend Lemma 1 to a finite number of shots and give a lower bound on the shots needed to distinguish two parameter values.
    Inputs: docs/theory/01_definitions.md and docs/theory/02_lemma1.md.
    What to do: using total variation or Hellinger distance between product distributions of N independent shots, derive a lower bound on the error probability and turn it into a condition for "blind within budget".
    Output format: Markdown with LaTeX, plus one small analytic example (for instance two single-qubit Pauli channels), labelled as analytic evidence.
    Do not: run noisy simulations; cite an unverified source for any inequality (textbook inequalities must be verified before they are cited); commit or push.
    Write the result into the repository. Report in the eight-item format.

### Task 1a-4: Local versus global identifiability, with two counterexamples

What to do. Prove that local identifiability and the global sign criterion do not contain each other, with one counterexample in each direction.
Purpose. To state precisely how this project's notion of blindness differs from the closest identifiability result in the literature (pain point 5).
Basis. Scavino (2026), Corollary C.1; the result of task W0-2; research plan, section 3.3.
Expected output. Docs/theory/04_local_vs_global.md
Acceptance criteria.   a proposition states that the two conditions do not contain each other;
  counterexample one shows a case that is locally identifiable but globally blind;
  counterexample two shows a case that is not locally identifiable but globally not blind;
  both counterexamples can be checked analytically or by noiseless computation, with the evidence type labelled;
  the relation to Scavino's Corollary C.1 is written according to the result of task W0-2.
Pain points and facets served. F1, pain point 5, local-versus-global proposition.
Prompt:

    Task: Prove that local identifiability (a Fisher-information null-space condition of the kind in Scavino's Corollary C.1) and this project's global sign criterion (whether the identification region contains points of opposite sign) do not contain each other, and give one counterexample in each direction.
    Inputs: docs/theory/01_definitions.md; section 4 of docs/reading_notes_key_sources.md and the addendum from task W0-2; the verbatim text of Corollary C.1.
    Output format: Markdown with LaTeX: proposition; proof; counterexample one (locally identifiable but globally blind); counterexample two (not locally identifiable but globally not blind); how the two conditions relate in the small-margin limit. Each counterexample comes with closed-form expressions that can be recomputed. Any numerical check must use noiseless computation only and be labelled "noiseless simulation".
    Do not: claim that theta includes noise parameters before task W0-2 settles it; restate Scavino's condition in a form the paper does not use; run noisy simulations; commit or push.
    Write the result into the repository. Report in the eight-item format, and also write a short comparison paragraph for the related-work table in which every sentence cites its source.

### Task 1a-5: Learnability criterion, draft

What to do. Connect the unlearnable noise components of Chen et al. (2023) to the identification region, or show that the connection does not hold.
Purpose. To obtain a first physical class of blindness in principle (pain point 5).
Basis. Chen et al. (2023), The learnability of Pauli noise; the project owner's reading notes on it; research plan, section 3.2.
Expected output. Docs/theory/05_learnability.md
Acceptance criteria. Based on the user's reading of Chen et al. 2023, either a criterion is written ("the projection of the differential bias onto the cut space"), or the text states that the theorem conditions of Chen et al. 2023 do not apply to this project's target circuits. Either outcome counts as done.
Pain points and facets served. F1, pain point 5.
Prompt:

    Task: Connect the unlearnable noise components in Chen et al. 2023 ("The learnability of Pauli noise") to this project's definition of the identification region.
    Inputs: the user's reading notes on Chen et al. 2023 (ask the user for them); docs/theory/01_definitions.md; section 3.2 of docs/project_plan_v0.md.
    Output format: Markdown with LaTeX: (a) the exact meaning of "unlearnable" in Chen et al. 2023, quoted from the paper; (b) whether it can be written as a special case of the identification region; (c) if yes, the criterion; if no, the reason.
    Do not: assume the theorem conditions without the user's reading notes; present content known only from the abstract as a theorem; commit or push.
    Write the result into the repository. Report in the eight-item format, and state plainly whether the conclusion is "can be connected" or "cannot be connected".

## Part 1b: the probe by error-structure matrix (analytic only)

### Task 1b-1: Probe by error-structure matrix, P0 to P5, P1b and GVS against E0 to E6

What to do. Derive the visibility prediction for probes P0 to P5, P1b (W_neg) and the GVS baseline under error structures E0 to E6.
Purpose. Failure conditions of existing methods are only partly stated (pain point 1); the matrix states them for every probe and structure in advance.
Basis. Research plan, section 4; Lipsitch et al. (2010), original wording, as the source of the analogy; limitations stated by Giurgica-Tiron et al. (2020) and Wallman and Emerson (2016).
Expected output. Docs/theory/06_matrix.md and docs/theory/06_matrix.csv (columns: probe, structure, prediction, derivation_summary, failure_condition, confidence).
Acceptance criteria.   every cell has an invariance proof, a sensitivity (kappa) derivation, or an explicit "?" with the reason;
  every visible cell is paired with the cells where the same probe is blind (rule R6);
  the validity condition is this project's own quantum condition, stated as an analogy to U-comparability, and labelled as an analogy.
Pain points and facets served. F1, pain point 1.
Prompt:

    Task: Derive the visibility prediction for probes P0 to P5, P1b (W_neg) and the GVS reference baseline under error structures E0 to E6. Analytic work only. P1b and GVS cells belong to facet F3 and are exploratory.
    Inputs: section 4 of docs/project_plan_v0.md; docs/theory/01 to 05; section 1 of docs/reading_notes_key_sources.md (the original wording of Lipsitch et al. 2010); the limitations admitted by the authors of Giurgica-Tiron et al. 2020 and Wallman and Emerson 2016 (see docs/inventory_20_step1.md); for P1b and GVS, Koster and Mauerer 2026 (arXiv 2607.09360) and Section 10 of Scavino 2026 (arXiv 2607.02888).
    Output format:
      (1) 06_matrix.md, one subsection per cell, with the prediction (visible, blind, partial, or ?), the derivation, and the failure condition;
      (2) 06_matrix.csv with columns probe, structure, prediction, derivation_summary, failure_condition, confidence.
    State the validity condition as "this project's quantum condition, by analogy with the U-comparability of Lipsitch et al. 2010".
    Do not: use simulation results to decide a prediction; describe Lipsitch's condition as "a shared bias mechanism"; mark any cell visible without listing the matching blind cells; commit or push.
    Write the result into the repository. Report in the eight-item format, and also list every "?" cell with its reason.

### Task 1b-2: P5 symmetry probe: positioning and blind-spot derivation

What to do. Write the visibility derivation for P5 (symmetry check) and state its positioning relative to earlier work.
Purpose. The P5 blind spot has already been pointed out in the literature, so the novelty claim for P5 must be limited accordingly.
Basis. Scavino Alfaro (2026), arXiv 2606.15464; Bonet-Monroig et al. (2018); docs/inventory_20_step2_painpoints.md, C.1.
Expected output. The P5 subsection of docs/theory/06_matrix.md.
Acceptance criteria. The text cites the "residual undetectable-sector bias" of arXiv 2606.15464, explains that this project differs by working under a fixed budget, at the decision level, with a global sign criterion, and derives why P5 is blind to errors that preserve the symmetry.
Pain points and facets served. F1, repositioning of P5.
Prompt:

    Task: Write the visibility derivation for P5 (symmetry check) and position its novelty as set in section 4.2 of docs/project_plan_v0.md.
    Inputs: entries 8 and 17 of docs/inventory_20_step1.md; section C.1 of docs/inventory_20_step2_painpoints.md; the relevant passages of arXiv 2606.15464 (re-read them and quote verbatim if you need quotes).
    Output format: one Markdown subsection with: positioning (one paragraph that first says what earlier work already showed), derivation, prediction, failure condition.
    Do not: claim this project was first to find the P5 blind spot; describe 2606.15464 as runtime detection (its residual bias is computed from a noise model and the ideal state); commit or push.
    Write the result into the repository. Report in the eight-item format.

### Task 1b-3: Text-level comparison of existing diagnostics (only if the W_neg extension is not adopted)

Status. Not applicable: the W_neg extension was adopted, so existing diagnostics are compared by simulation in tasks 1b-1 and 4-1. The task is kept for reference.
What to do. Build a text-level comparison of existing runtime diagnostics. This task applies only if the W_neg extension is not adopted.
Purpose. Diagnostics in the literature lack formal, falsifiable thresholds (pain point 6); a comparison with traceable cells supports the restated novelty (F3).
Basis. Koster and Mauerer (2026), arXiv 2607.09360; Scavino (2026), arXiv 2607.02888; Scavino Alfaro (2026), arXiv 2606.15464.
Expected output. Docs/related_work_table.md
Acceptance criteria. W_neg, GVS, DRI and GRI, and the symmetry-verification clip monitoring are compared column by column (needs ideal values or not, what failure it targets, whether its cost is charged to a budget, threshold, whether it targets differential bias between candidates). Every cell can be traced to the original paper. Nothing is marked "no" without a source.
Pain points and facets served. F3, pain point 6.
Prompt:

    Task: Build a comparison table of existing runtime diagnostics. Text only, no simulation.
    Inputs: section C.1 of docs/inventory_20_step2_painpoints.md; the original papers: Koster and Mauerer 2026 (arXiv 2607.09360), Scavino 2026 (arXiv 2607.02888), Scavino Alfaro 2026 (arXiv 2606.15464).
    Output format: a Markdown table with columns: diagnostic, source, needs ideal values, failure mode targeted, cost charged to a fixed budget, threshold frozen in advance, targets differential bias between candidates, quote.
    Do not: write "no" without a source (write "not seen in what we read"); commit or push.
    Write the result into the repository. Report in the eight-item format.

## Part 1c: certificate and Proposition 2 (analytic only)

### Task 1c-1: Bias-aware certificate and joint coverage

What to do. Derive a bias-aware certificate whose bias bound B is set by probe data, and prove joint coverage.
Purpose. Existing theory treats bias as known or computable from ideal values (pain point 2), and controlling sampling error does not control bias (pain point 3).
Basis. Armstrong and Kolesar (2020); Imbens and Manski (2004); research plan, section 3.7.
Expected output. Docs/theory/07_certificate.md
Acceptance criteria.   the rule is written: certify only if the lower confidence bound of the gap exceeds B, where B is set by the probe data;
  joint coverage is derived (for example, a union bound that controls the probe interval and the target interval together);
  the difference from Armstrong and Kolesar (whose bias bound is fixed in advance) is stated;
  it is proved that the rule never certifies in a blind direction.
Pain points and facets served. F2, pain points 2 and 3.
Prompt:

    Task: Derive a bias-aware certificate whose bias bound B is set by the probe data, and prove its joint coverage.
    Inputs: docs/theory/01 to 03; section 3 of docs/reading_notes_key_sources.md (Armstrong and Kolesar, original wording) and section 2 (Imbens and Manski).
    Output format: Markdown with LaTeX: the rule; a coverage theorem with proof; the differences from Armstrong and Kolesar, point by point with quotes; a proof that the rule never certifies in a blind direction; one analytic example.
    Do not: claim that coverage is inherited directly from Armstrong and Kolesar; replace a proof with simulation; commit or push.
    Write the result into the repository. Report in the eight-item format, and also list every condition the coverage proof needs.

### Task 1c-2: Proposition 2: when is spending budget on probes worth it?

What to do. Derive Proposition 2: when spending part of the budget on probes lowers the overall decision error.
Purpose. Detection cost is not usually charged to the decision budget (minor pain point 2); F2 needs a condition on the probe fraction.
Basis. Proposition 1 of the previous project; Kaufmann et al. (2016); Garivier and Kaufmann (2016); Chen et al. (2000); research plan, section 3.6.
Expected output. Docs/theory/08_prop2.md
Acceptance criteria. Using Proposition 1 as a template, a condition on the probe fraction f is derived. Budget-allocation language cites only verified entries (Kaufmann et al. 2016, Garivier and Kaufmann 2016, Chen et al. 2000).
Pain points and facets served. F2, minor pain point 2.
Prompt:

    Task: Derive Proposition 2. Out of a total budget N, a fraction fN goes to probes and (1 - f)N to the decision. Find the conditions under which the overall decision error goes down.
    Inputs: Proposition 1 of the previous project (Section 2 of paper/main_v2.tex in adaptive-qem-benchmark; read only, do not edit); section 3.6 of docs/project_plan_v0.md; docs/theory/07_certificate.md.
    Output format: Markdown with LaTeX: proposition, proof, comparison with Proposition 1, conditions under which it holds. Budget-allocation citations may only use verified entries in docs/literature/library.csv.
    Do not: edit the previous repository; cite unverified work; commit or push.
    Write the result into the repository. Report in the eight-item format.

### Task 1c-3: Extending Proposition 1: K candidates, estimated gamma, link to the limits literature

What to do. Extend Proposition 1 to K candidates, to gamma and a estimated from data, and to small samples, and relate it to the limits literature.
Purpose. This supports the secondary endpoint (the Proposition 1 prediction test) and the answer to the expected examiner question on limits (minor pain point 1).
Basis. Proposition 1 of the previous project; Takagi et al. (2022); Quek et al. (2024); Scavino (2026), effective margin.
Expected output. Docs/theory/09_prop1_ext.md
Acceptance criteria.   a version for K candidates is given;
  the correction for gamma and a being estimated from data is given;
  a bound or correction for small samples or non-normal data is given;
  the text explains that gamma is an instance, for a single estimator, of the lower bounds in Takagi et al. and Quek et al.;
  Scavino's effective margin is cited and compared.
Pain points and facets served. Secondary endpoint (the Proposition 1 prediction test), minor pain point 1.
Prompt:

    Task: Extend Proposition 1 of the previous project (Delta_m > sqrt(gamma) Delta_r) to K candidates, to gamma and a estimated from data, and to small samples, and explain its relation to the literature on limits of error mitigation.
    Inputs: Proposition 1 in paper/main_v2.tex of the previous repository (read only); the abstracts and, if read, relevant passages of Takagi et al. 2022 and Quek et al. 2024; Scavino 2026's definition of the effective margin mu_m = Delta + L a_m, with quotes.
    Output format: Markdown with LaTeX: the extended proposition; proof; comparison with Scavino's effective margin; a paragraph linking to Takagi and Quek in which every sentence states its source and how deeply that source was read. Also attach a draft of the pilot estimators and decision rule for the Part 3 prediction test, labelled "to be frozen in Part 1d".
    Do not: state theorem details of Takagi or Quek that are known only from their abstracts; change the primary or secondary endpoints; commit or push.
    Write the result into the repository. Report in the eight-item format.

### Task 1c-4: Grow the literature library to at least 90 verified papers

What to do. Bring the verified entries of the literature library to at least 90.
Purpose. The literature requirements of the project call for a library of 60 to 100 verified papers with notes, and the original sources of all statistical methods.
Basis. docs/literature/library.csv; docs/literature_review.md, section 8.
Expected output. Docs/literature/library.csv and paper/references.bib
Acceptance criteria. At least 90 papers are verified; each has a three-line note; the five partial entries are either completed or stay excluded; the original sources for cluster bootstrap and mixed-effects models are verified.
Pain points and facets served. Literature requirements of the project specification.
Prompt:

    Task: Bring the verified entries in docs/literature/library.csv to at least 90.
    Inputs: docs/literature/library.csv; the open topics in section 8 of docs/literature_review.md (biased or misspecified bandits; model uncertainty in error mitigation; original sources for cluster bootstrap and mixed-effects models).
    What to do: check each paper online (authors, venue, volume, DOI) and record how it was checked in the source_checked column. If a paper cannot be fully checked, mark it partial and keep it out of references.bib.
    Output format: the updated library.csv and references.bib, plus a list of additions (for each paper: how it was checked, how deeply it was read, the three-line note).
    Do not: fill in bibliographic details from memory; put partial entries into references.bib; work around a site that refuses access; commit or push.
    Write the result into the repository. Report in the eight-item format, and attach a consistency check between references.bib and library.csv.

## Part 1d: freeze

### Task 1d-1: Power analysis by simulation (only after the predictions are frozen)

What to do. Run a power analysis by simulation to set the holdout size and the number of repeats.
Purpose. The design must have enough power for the primary endpoint (F1), and the power analysis must not influence the predictions.
Basis. docs/theory/06_matrix.csv; research plan, sections 5 and 6.
Expected output. Experiments/power/ (code, raw rows, run log) and docs/freeze/power_analysis_v4.md
Acceptance criteria.   it runs only after 06_matrix has been committed;
  it sets a holdout of at least 100 circuits, at least 50 QAOA graphs from at least 3 graph families, and at least 2 circuits for each width and depth;
  the run log records the numpy version and BLAS configuration;
  the scope is set using the frozen scope-cutting rule.
Pain points and facets served. F1, the power-analysis requirement of the specification.
Prompt:

    Task: Run a power analysis by simulation to set the holdout size and number of repeats.
    Precondition: confirm that docs/theory/06_matrix.csv has been committed by the user. If not, stop and report.
    Inputs: docs/theory/06_matrix.csv; sections 5 and 6 of docs/project_plan_v0.md (endpoints and thresholds).
    Output format: code under experiments/power/ (all seeds derived from ROOT_SEED), raw rows as CSV, a run log (including the numpy version and the output of np.show_config()); docs/freeze/power_analysis_v4.md stating each design parameter chosen and its power, and for every value-versus-threshold decision, how far the value is from the threshold.
    Do not: change any prediction in 06_matrix after seeing the power results; use machine learning; run hardware; overwrite raw rows; commit or push.
    Write the result into the repository. Report in the eight-item format, with the full experiment grid.

### Task 1d-2: Frozen protocol

What to do. Assemble the frozen protocol.
Purpose. Without a threshold frozen in advance, results can be interpreted after the fact (pain point 6); every facet depends on the frozen protocol.
Basis. docs/theory/01 to 09; docs/freeze/power_analysis_v4.md; research plan.
Expected output. Docs/freeze/frozen_protocol_v2.md (with its content hash)
Acceptance criteria. The structures and parameter grid, probe specifications and cost formulas, thresholds and sensitivity table, development and holdout seed split, primary endpoint, scope-cutting rule, and the pilot procedure and decision rule for the Proposition 1 test are all fixed in writing; items that may be adjusted but must be logged are listed separately.
Pain points and facets served. Pain point 6 and all facets.
Prompt:

    Task: Assemble the frozen protocol.
    Inputs: docs/theory/01 to 09, 06_matrix.csv, docs/freeze/power_analysis_v4.md, docs/project_plan_v0.md.
    Output format: docs/freeze/frozen_protocol_v2.md with these sections in order: scope; definitions; prediction matrix (cite the hash of 06_matrix.csv); probe specifications and costs; thresholds and sensitivity table; data split and seeds; primary and secondary endpoints; scope-cutting rule; Proposition 1 prediction procedure; items that may be adjusted but must be logged; change rules (delays only move later). End with the command that computes the file's content hash.
    Do not: add probes or endpoints the user has not approved; include any simulation result as the basis for a prediction; commit or push.
    Write the result into the repository. Report in the eight-item format.

### Task 1d-3: Registration draft for OSF or AsPredicted

What to do. Write the draft registration form for OSF or AsPredicted.
Purpose. An independent timestamp is required before the word preregistration can be used.
Basis. docs/freeze/frozen_protocol_v2.md.
Expected output. Docs/freeze/registration_draft.md
Acceptance criteria. The draft matches the frozen protocol; the user submits it personally and records the timestamp in the repository.
Pain points and facets served. The registration requirement of the specification.
Prompt:

    Task: Write a draft of the OSF (or AsPredicted) registration form based on docs/freeze/frozen_protocol_v2.md.
    Output format: fill in the platform's fields in their order; for each field, note the matching section of the frozen protocol.
    Do not: submit on the user's behalf; use the word "preregistration" before an independent timestamp exists (write "frozen and committed in this repository" instead).
    Report in the eight-item format, and remind the user to record the timestamp in the repository after submitting.

## Part 2: implementation and development set
Starts only after Part 1d is frozen and the previous project is closed.

### Task 2-1: Probe implementation and cost ledger

What to do. Implement the probes and the cost ledger exactly as specified in the frozen protocol.
Purpose. F1 and F2 require every probe's cost to be charged to the same total budget, and no probe may read ideal values.
Basis. docs/freeze/frozen_protocol_v2.md, probe specifications and cost formulas.
Expected output. Src/probes/, the manifest and analysis-contract implementation required by section 10.1 of the frozen protocol, and their tests.
Acceptance criteria. P0 to P5, P1b and GVS are implemented; tests confirm that total shots in every run equal the budget; a test enforces that probes never receive ideal values; manifest generation, strength-map selection, E0 alarm calibration, analysis skeleton and split guards are complete and tested before split 10 can be instantiated.
Pain points and facets served. F1, F2.
Prompt:

    Task: Implement the probes and the cost ledger exactly as specified in the frozen protocol.
    Input: the probe specifications and cost formulas in docs/freeze/frozen_protocol_v2.md.
    Output format: a src/probes/ module (one function per probe, returning its statistic and the number of circuits and shots it actually used); manifest generation, strength-map selection, E0 alarm calibration, analysis skeleton and split guards required by section 10.1; tests covering exact budgets, no ideal-value probe argument, deterministic seeds, immutable manifests and refusal to instantiate split 10 before the before-development lock.
    Do not: change any specification in the frozen protocol; use machine learning; run ruff format on the whole repository (format new files only); commit or push; run git on the user's computer.
    Write the result into the repository. Report in the eight-item format, and give the pytest command (on Windows add --basetemp="$env:TEMP\qem-pytest").

### Task 2-2: Positive and negative controls, and cross-checks with independent code

What to do. Run positive and negative controls and cross-checks with independent code on the development set.
Purpose. Alarms must be shown to fire on known bias and stay quiet under E0 before thresholds are set (pain point 6); key numbers must be cross-checked with different code.
Basis. docs/freeze/frozen_protocol_v2.md; Mitiq; two stabilizer simulators.
Expected output. Experiments/dev_controls/ and docs/dev/controls_report.md
Acceptance criteria. Before split 10 is instantiated, the protocol and section-10.1 implementation are committed and independently timestamped; cases with an analytically known bias trigger the alarm; the false-alarm rate under E0 is close to alpha; P1 is cross-checked with Mitiq's folding; the Clifford ideal values used by P2 are cross-checked with two different stabilizer simulators.
Pain points and facets served. Pain point 6, the cross-validation requirement of the specification.
Prompt:

    Task: Run positive and negative controls and cross-checks on the development set.
    Precondition: confirm that the protocol and the complete section-10.1 implementation have been committed and independently timestamped, and that split 10 has never been instantiated. If not, stop and report.
    Inputs: docs/freeze/frozen_protocol_v2.md; src/probes/.
    Output format: code, raw rows and run log under experiments/dev_controls/; docs/dev/controls_report.md listing each check as passed or failed, with its value and its distance from the threshold.
    Do not: read any data from holdout seeds; change probe specifications or loosen tolerances when a check fails; delete failed runs; commit or push.
    Write the result into the repository. Report in the eight-item format, grouping failures by cause (method, resources, model, design).

### Task 2-3: Calibrate alarm thresholds from E0 only, then commit

What to do. Calibrate the alarm thresholds from the E0 null distribution only, and list the cells where development data disagree with the predictions.
Purpose. Thresholds must be fixed by a procedure set in advance, not chosen after seeing results (pain point 6, F1).
Basis. docs/freeze/frozen_protocol_v2.md; raw rows in experiments/dev_controls/.
Expected output. Docs/freeze/strength_map_v2.csv, docs/dev/thresholds_v2.md, docs/dev/dev_mismatch_v2.md, and docs/freeze/confirmatory_lock_v2.json.
Acceptance criteria. The strength map and thresholds are produced only by the frozen algorithms; thresholds are calibrated from the E0 null distribution; every cell where development data disagree with the prediction is listed; the 1% timing pilot and all input/output hashes are recorded; the theory is not changed; the owner commits and independently timestamps the confirmatory lock before any holdout seed is instantiated.
Pain points and facets served. Pain point 6, F1.
Prompt:

    Task: Following the frozen procedure, calibrate the alarm thresholds using only the E0 (common-mode) null distribution, and list the cells where the development data disagree with the predictions.
    Inputs: docs/freeze/frozen_protocol_v2.md; raw rows in experiments/dev_controls/.
    Output format: docs/freeze/strength_map_v2.csv; docs/dev/thresholds_v2.md (threshold, calibration sample size and sensitivity for each probe); docs/dev/dev_mismatch_v2.md (for each mismatched cell: prediction, observation, possible cause); docs/freeze/confirmatory_lock_v2.json containing their hashes, the implementation-error log, the 1% timing-pilot result, and proof that split 20 was never instantiated.
    Do not: change predictions in 06_matrix or any theory document because of mismatches; read the holdout; commit or push.
    Write the result into the repository. Report in the eight-item format, and remind the user to commit and independently timestamp the confirmatory lock before Part 3.

## Part 3: confirmatory holdout

### Task 3-1: One-time holdout scoring (primary endpoint)

What to do. Compute the primary endpoint on the holdout, exactly once.
Purpose. This is the confirmatory test of F1.
Basis. docs/freeze/frozen_protocol_v2.md; docs/freeze/confirmatory_lock_v2.json.
Expected output. Results/holdout/ (raw rows, summary, run log) and docs/results/primary_endpoint.md
Acceptance criteria. It runs exactly once; the agreement rate between predicted and observed visibility is reported with the prespecified shared-graph cluster-bootstrap interval; it can be recomputed independently from the raw rows; it is run on both Windows and Linux and the two are compared.
Pain points and facets served. F1 (primary).
Prompt:

    Task: Compute the primary endpoint on the holdout. Run it exactly once.
    Precondition: confirm that the frozen protocol and confirmatory_lock_v2.json have been committed and independently timestamped, and that split 20 has never been instantiated. If not, stop and report.
    Inputs: docs/freeze/frozen_protocol_v2.md; docs/freeze/confirmatory_lock_v2.json; src/probes/.
    Output format: raw rows in results/holdout/ (never overwritten); a summary script that recomputes everything from the raw rows; a run log (numpy version and BLAS configuration); docs/results/primary_endpoint.md (agreement rate, shared-graph cluster-bootstrap interval, result for every cell, distance from each threshold).
    Do not: change any rule or threshold after seeing results; rerun the holdout; delete rows that fail checks; commit or push.
    Write the result into the repository. Report in the eight-item format, and report unfavourable results plainly.

### Task 3-2: Bias-aware certificate versus confidence-interval-only (secondary, F2)

What to do. Compare the bias-aware certificate with the confidence-interval-only certificate on the holdout data.
Purpose. This is the secondary test of F2.
Basis. docs/theory/07_certificate.md (frozen rule).
Expected output. Docs/results/secondary_certificate.md
Acceptance criteria. False-certification rate and unresolved rate are reported for both rules under the same total budget, with intervals.
Pain points and facets served. F2.
Prompt:

    Task: On the holdout data, compare the bias-aware certificate with the confidence-interval-only certificate. This is a secondary endpoint.
    Inputs: raw rows in results/holdout/; the frozen rule in docs/theory/07_certificate.md.
    Output format: docs/results/secondary_certificate.md with the false-certification rate, unresolved rate and shared-graph cluster-bootstrap intervals for both rules, clearly labelled as a secondary endpoint.
    Do not: change the certificate rule; present secondary results as the main conclusion; commit or push.
    Write the result into the repository. Report in the eight-item format.

### Task 3-3: Proposition 1 prediction test (secondary, run once)

What to do. Run the Proposition 1 prediction test, exactly once.
Purpose. This is a falsifiable test of the extended Proposition 1 (secondary endpoint).
Basis. docs/theory/09_prop1_ext.md; the frozen pilot procedure and decision rule.
Expected output. Docs/results/prop1_prediction_test.md and a predictions file that is committed and registered before the scoring data are run.
Acceptance criteria. The steps happened in this order: pilot; predictions written to a file; the user commits and registers them; scoring data; hit rate reported once.
Pain points and facets served. Secondary endpoint.
Prompt:

    Task: Run the Proposition 1 prediction test, exactly once.
    Step one (then stop): run the pilot, compute a and gamma for each new graph using the frozen estimators, write the prediction (raw better or ZNE better) for each graph using the frozen decision rule, and save it as results/prop1/predictions.csv. Then stop and ask the user to commit and register it.
    Step two: only after the user reports the commit hash and the registration timestamp, run the scoring data and compute the hit rate.
    Output format: predictions.csv; docs/results/prop1_prediction_test.md (hit rate, interval, result for each graph).
    Do not: run the scoring data before the user reports back after step one; change any prediction; rerun; commit or push.
    Write the result into the repository. Report in the eight-item format.

## Part 4: synthesis and paper

### Task 4-1: Boundary map and failure causes

What to do. Produce the visibility boundary map and classify every failure by cause.
Purpose. This is the central result of F1, with the F3 comparison included.
Basis. results/holdout/; docs/results/*.md; docs/theory/06_matrix.csv.
Expected output. Figures/boundary_map.* and docs/results/boundary_synthesis.md
Acceptance criteria. The boundary map (structure by bias-to-gap ratio by required probe fraction) is drawn; every failure is grouped by cause (method, resources, model, design); the F3 comparison (P1b and GVS) is done by simulation and labelled exploratory.
Pain points and facets served. F1, F3.
Prompt:

    Task: Produce the visibility boundary map and the classification of failure causes.
    Inputs: results/holdout/, docs/results/*.md, docs/theory/06_matrix.csv.
    Output format: figures/boundary_map.png whose caption starts with the conclusion; docs/results/boundary_synthesis.md (for each cell: prediction, observation, cause category, evidence type). Compare figures at the pixel level, and run provenance --write only after all generation steps.
    Do not: present exploratory results as confirmatory; hide mismatched cells; commit or push.
    Write the result into the repository. Report in the eight-item format.

### Task 4-2: Hardware go or no-go review

What to do. Review whether the readout hardware experiment should go ahead, without running any hardware.
Purpose. Resources are spent on hardware only after a review, and a no-go verdict is given when evidence is insufficient.
Basis. Research plan, section 13; IBM Quantum's current official plan terms.
Expected output. Docs/hardware/review_v1.md
Acceptance criteria. The review follows the time budget and reduction rules in section 13 of the plan; IBM's current plan terms have been checked; the verdict is no-go if evidence is insufficient; a go verdict still needs the user's explicit authorization before anything runs.
Pain points and facets served. The hardware review requirement of the specification.
Prompt:

    Task: Review whether the readout hardware experiment (P4a and P4b) should go ahead. Do not run any hardware.
    Inputs: section 13 of docs/project_plan_v0.md; IBM Quantum's current official plan terms, looked up online (record the date and URL).
    Output format: docs/hardware/review_v1.md: each go condition checked one by one, the no-go triggers, a time-budget estimate (never using an unmeasured time per shot), and the verdict.
    Do not: submit any job; ask for, print or store an API key; treat the experiment as approved without the user's explicit authorization; commit or push.
    Write the result into the repository. Report in the eight-item format.

### Task 4-3: Claims list, then the paper draft

What to do. Write the claims list first, then the first draft of the paper.
Purpose. Every claim must carry its evidence type and strength, and the novelty, limitations and limits literature must be stated as set in the research plan.
Basis. docs/results/*.md; docs/theory/*.md; paper/references.bib; docs/inventory_20_step2_painpoints.md; docs/inventory_20_step3_facets.md.
Expected output. Paper/claims.md (written first) and paper/main.tex
Acceptance criteria. The claims list is finished first, with an evidence type and strength for every claim; the abstract has at most three numbers; every section opens with its conclusion; novelty uses the four-condition statement, qualified with "in what we read"; the limitations section includes the narrow evidence base; every citation key is in references.bib and every bib entry is cited.
Pain points and facets served. All facets; the four-condition novelty statement, the narrow-evidence limitation, and the treatment of the limits literature.
Prompt:

    Task: Write the claims list first, then the first draft of the paper.
    Inputs: docs/results/*.md, docs/theory/*.md, paper/references.bib, docs/inventory_20_step2_painpoints.md, docs/inventory_20_step3_facets.md.
    Output format:
      (1) paper/claims.md: each claim with its evidence type (analytic, noiseless simulation, noisy simulation, device-parameter simulation, hardware), its strength, and the file it comes from;
      (2) paper/main.tex in the same format as the previous report; at most three numbers in the abstract; every section opens with its conclusion; each number appears in one place only.
    Do not: claim general laws (claim existence only); write "earlier work did not do X" (write "not seen in what we read"); cite anything outside references.bib; commit or push.
    Write the result into the repository. Report in the eight-item format, and attach a two-way consistency check between citation keys and references.bib.

## Freeze rules

Must be fixed in writing before any noisy simulation (in Part 1d, through the frozen protocol and the registration):
  the error structures, their parameter grid, and the grid of bias-to-gap ratios;
  each probe's specification, cost formula and form of alarm rule;
  the main threshold values and their sensitivity ranges (section 6 of the plan);
  the split between development and holdout seeds, and the rule that the holdout is read once;
  the single primary endpoint (agreement rate of visibility predictions) and its success threshold, and which endpoints are secondary or exploratory;
  every prediction in 06_matrix;
  the scope-cutting rule and its order of priority;
  the pilot procedure, estimators and decision rule for the Proposition 1 prediction test (the predictions themselves are written and registered in step one of task 3-3);
  the time limit and reduction order for the hardware experiment, if it happens.

May be adjusted, but every change is logged in the run log and the change record:
  engineering details that do not affect results, such as file layout, how functions are split, and performance improvements;
  fixes to implementation errors found on the development set, made before the holdout is read, with the before-and-after difference recorded;
  figure layout and colours, as long as the values shown do not change.

Change rules:
  delays only move later tasks later; the content and order of Parts do not change;
  no rule or threshold changes after holdout results are seen;
  when theory and simulation disagree, it is recorded as a failed prediction; the theory is not revised.

## Outside the scope of this phase

Narrow evidence base and unclear generalization (former pain point 7). This project is mainly simulation and has the same problem. It is acknowledged in the limitations section, and conclusions are limited to existence claims.

Pain point 4 (benchmarks stop at estimator accuracy) gets no facet of its own. Scavino 2026 already addresses "accuracy is not the same as a good decision". It stays as background and is covered by the secondary endpoint for Proposition 1.

Minor pain point 1 (limits theory has no decision-level counterpart). Only two sources support it. It is addressed only when writing, to answer the expected examiner question about limits of error mitigation.

Full readout-correlation correction. This project detects bias; it does not mitigate it.

A full proof of randomized compiling under general noise. That belongs to the theory of randomized compiling itself.

Worst-case versus typical-case limits of error mitigation. That belongs to estimator-level limits research.

Scalability of characterization protocols. Dedicated work already exists.

Statistical rigour of error-mitigation benchmarking as a topic. Koster and Mauerer (arXiv 2605.29872) already address it; this project only adopts their recommended practices.
