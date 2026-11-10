Inventory of 20 papers, step 4: task list

This file turns the research facets from step 3 into an ordered list of tasks. Each task says what it produces, when it counts as done, which pain point or facet it serves, and gives a prompt that can be pasted directly into an AI assistant.

There are no dates or day estimates here. The order of tasks matters; the calendar does not. If anything slips, later tasks move later, but their content does not change.

Sources for this file
  Step 3 decisions: A2, A3 to A6 and A7 adopted. A1 deferred and must be decided before Part 1a starts; if not decided by then, it counts as rejected.
  Research facets: F1 visibility boundary (primary endpoint), F2 certificate with a data-driven bias bound (secondary), F3 comparison with existing diagnostics (exploratory).
  Pain points are numbered as in docs/inventory_20_step2_painpoints.md: pain points 1 to 6, minor pain points 1 and 2.
  Part 2 can start only after Part 1d is frozen and the previous project (adaptive-qem-benchmark) is closed.


Rules that apply to every task

Each prompt below already repeats these rules. They are listed here once so a person can check them in one place.

  R1. Never commit, push or reset. Give the git commands to the user instead. Never run git on the user's computer.
  R2. No machine learning. No hardware runs unless the user explicitly authorizes that specific run.
  R3. Never invent citations, numbers or results. Check every new citation online (authors, venue, volume, DOI). If it cannot be checked, mark it "unverified" and keep it out of references.bib.
  R4. A probe must never read the ideal value of the target circuit. Every probe states its cost in circuits and shots.
  R5. Analytic predictions are frozen before any noisy simulation. Simulation results never change the theory; a mismatch is reported as a failed prediction.
  R6. Every claim that a probe works must also list the error structures where it fails.
  R7. Label evidence by type: analytic, noiseless simulation, noisy simulation, device-parameter simulation (fake backend), hardware. A fake backend is not hardware evidence.
  R8. Write results directly into the repository unless there is a specific reason not to; in that case, say why.
  R9. When finished, report in eight items: files created or changed, experiment grid actually run, verification results, supported findings, negative or inconclusive findings, remaining scientific concerns, whether the next task can start, commit hash if the user has committed.


Stage W0: before Part 1a


Task W0-1. Plan v0.5: apply A2 to A6
Status: done. Claude applied it directly under the collaboration rules; the user only needs to review it.
Output: docs/project_plan_v0.md (v0.5) and section 6 of docs/literature_review.md.
Done when: the only changes are the A2 to A6 text, the recorded decisions in sections 11 and 12, and the schedule note. Endpoints, thresholds, probes and the number and order of Parts are unchanged.
Serves: A2 to A6; pain points 1 and 5; minor pain point 1.
Prompt: none needed (already done).


Task W0-2. Read Scavino, Appendix C: what does theta contain?
Output: an addendum to section 4 of docs/reading_notes_2026-11-10.md, or a new dated notes file.
Done when: the question "does theta include noise parameters?" is answered with verbatim quotes. If the paper does not say, the answer is "not stated in what we read", with the range of text read.
Serves: F1, pain point 5, A2.
Prompt:

    Task: Read Appendix C and Section 9 of arXiv 2607.02888 (Scavino, "Decision Kernels for Quantum Error Mitigation") and answer one question: what does theta in the primitive laws p_{s,theta} contain, and in particular, does it include noise parameters?
    Inputs: https://arxiv.org/pdf/2607.02888 ; section 4 of docs/reading_notes_2026-11-10.md in the bias-probe-visibility repository.
    Output:
      (a) verbatim quotes, each with its section or equation number;
      (b) a one-line conclusion that is exactly one of: "theta includes noise parameters", "theta does not include noise parameters", "not stated in what we read";
      (c) what this means for the relation between Corollary C.1 and this project's definition of "blind" (if theta includes noise parameters, Corollary C.1 is a local, point-value version of our "visible" condition).
    Do not: use speculative wording; present a paraphrase as a quote; write "the paper does not do X" (write "not stated in what we read"); commit or push.
    Write the result into the repository. Report in the eight-item format.


Task W0-3. Decide A1 (user decision)
Output: one line recording the decision in section 11 of the plan.
Done when: the user answers "adopt" or "reject". No answer before Part 1a starts counts as reject.
Serves: F3, pain point 6.
Prompt:

    Task: Before Part 1a starts, remind the user to decide A1: whether to add the W_neg diagnostic of Koster and Mauerer (arXiv 2607.09360) to the probe set as P1b, with Scavino's GVS as a reference baseline.
    Input: the A1 row in section 2 of docs/inventory_20_step3_facets.md.
    Output: one short message stating the cost (more derivation work in Part 1b; the probe set grows from 7 to 9; the scope-cutting rule must be rewritten) and the benefit (it directly supports the four-condition novelty statement). Ask for a plain answer, adopt or reject.
    Do not: decide for the user; change the plan before the user answers.
    Report: the user's answer verbatim and the line to add to section 11 of the plan.


Part 1a: definitions and Lemma 1 (analytic only)


Task 1a-1. Definitions
Output: docs/theory/01_definitions.md
Done when:
  the identification region, blind in principle, blind within budget, and visible are all defined;
  each definition is marked either with its source (Imbens and Manski 2004, Section 2) or as "this project's definition";
  two assumptions are stated: (i) given the observable distribution P and the noise e, the ideal gap is uniquely determined; (ii) the ideal gap is a fixed number in principle, and treating it as unknown is a modelling choice;
  the user's review of Imbens and Manski has been included.
Serves: F1, pain point 5.
Prompt:

    Task: Write the core definitions for this project. Analytic work only.
    Inputs: section 2 of docs/project_plan_v0.md; section 2 of docs/reading_notes_2026-11-10.md (the check of Imbens and Manski); the user's own review notes on Imbens and Manski and on Chen et al. 2023. Ask the user for these notes; do not guess their content.
    What to do: following the form used by Imbens and Manski, write the gap as Delta = f(P, e) and define the identification region as {f(P, e') : e' in E}. Then define "blind in principle", "blind within budget" and "visible". P is the joint observable distribution of the target and probe outputs.
    Output format: Markdown with LaTeX. After each definition write either "Source: ..." or "This project's definition". End with a section "Assumptions that must be stated" listing (i) and (ii), and stating that the probes change P while the noise set E stays fixed; say clearly that this last step is our own derivation.
    Do not: present our derivation as the source's; cite unverified work (for example, Rothenberg 1971 must not be cited until verified); run any simulation; commit or push.
    Write the result into the repository. Report in the eight-item format, and also list every "this project's definition" so the user can approve each one.


Task 1a-2. Lemma 1 and its proof
Output: docs/theory/02_lemma1.md
Done when:
  the statement and proof are complete: if the identification region contains points of opposite sign, then for any rule P1(error) + P2(error) >= 1;
  the corollary is stated: a certificate that looks only at the target is blind to any bias large enough within the allowed noise set;
  any source for the two-point argument is verified before it is cited.
Serves: F1, pain points 3 and 5.
Prompt:

    Task: Write the statement and full proof of Lemma 1.
    Inputs: docs/theory/01_definitions.md; item 1 of section 3 of docs/project_plan_v0.md.
    What to do: prove that when the identification region contains both a point with Delta > 0 and a point with Delta <= 0, every decision or certification rule satisfies P_theta1(error) + P_theta2(error) >= 1. Then derive the corollary that a confidence-interval-only certificate is blind.
    Output format: Markdown with LaTeX, in this order: statement, proof, corollary, conditions under which it holds, cases where it does not apply.
    Do not: cite page numbers of Le Cam 1973 or any unverified source (if you cite the two-point method, verify the source online first; if you cannot, mark it "unverified" and call it "the standard two-point argument"); use simulation to support the proof; commit or push.
    Write the result into the repository. Report in the eight-item format, and also list every assumption used in the proof.


Task 1a-3. Finite-shot lower bound
Output: docs/theory/03_finite_shot_bound.md
Done when: a lower bound on the number of shots needed to tell two parameter values apart is written using total variation or Hellinger distance, and the text clearly separates distance zero (blind in principle) from small distance (blind within budget).
Serves: F1.
Prompt:

    Task: Extend Lemma 1 to a finite number of shots and give a lower bound on the shots needed to distinguish two parameter values.
    Inputs: docs/theory/01_definitions.md and docs/theory/02_lemma1.md.
    What to do: using total variation or Hellinger distance between product distributions of N independent shots, derive a lower bound on the error probability and turn it into a condition for "blind within budget".
    Output format: Markdown with LaTeX, plus one small analytic example (for instance two single-qubit Pauli channels), labelled as analytic evidence.
    Do not: run noisy simulations; cite an unverified source for any inequality (textbook inequalities must be verified before they are cited); commit or push.
    Write the result into the repository. Report in the eight-item format.


Task 1a-4. Local versus global identifiability, with two counterexamples (A2)
Output: docs/theory/04_local_vs_global.md
Done when:
  a proposition states that the two conditions do not contain each other;
  counterexample one shows a case that is locally identifiable but globally blind;
  counterexample two shows a case that is not locally identifiable but globally not blind;
  both counterexamples can be checked analytically or by noiseless computation, with the evidence type labelled;
  the relation to Scavino's Corollary C.1 is written according to the result of task W0-2.
Serves: F1, pain point 5, A2.
Prompt:

    Task: Prove that local identifiability (a Fisher-information null-space condition of the kind in Scavino's Corollary C.1) and this project's global sign criterion (whether the identification region contains points of opposite sign) do not contain each other, and give one counterexample in each direction.
    Inputs: docs/theory/01_definitions.md; section 4 of docs/reading_notes_2026-11-10.md and the addendum from task W0-2; the verbatim text of Corollary C.1.
    Output format: Markdown with LaTeX: proposition; proof; counterexample one (locally identifiable but globally blind); counterexample two (not locally identifiable but globally not blind); how the two conditions relate in the small-margin limit. Each counterexample comes with closed-form expressions that can be recomputed. Any numerical check must use noiseless computation only and be labelled "noiseless simulation".
    Do not: claim that theta includes noise parameters before task W0-2 settles it; restate Scavino's condition in a form the paper does not use; run noisy simulations; commit or push.
    Write the result into the repository. Report in the eight-item format, and also write a short comparison paragraph for the related-work table in which every sentence cites its source.


Task 1a-5. Learnability criterion, draft
Output: docs/theory/05_learnability.md
Done when: based on the user's reading of Chen et al. 2023, either a criterion is written ("the projection of the differential bias onto the cut space"), or the text states that the theorem conditions of Chen et al. 2023 do not apply to this project's target circuits. Either outcome counts as done.
Serves: F1, pain point 5.
Prompt:

    Task: Connect the unlearnable noise components in Chen et al. 2023 ("The learnability of Pauli noise") to this project's definition of the identification region.
    Inputs: the user's reading notes on Chen et al. 2023 (ask the user for them); docs/theory/01_definitions.md; item 1b of section 3 of docs/project_plan_v0.md.
    Output format: Markdown with LaTeX: (a) the exact meaning of "unlearnable" in Chen et al. 2023, quoted from the paper; (b) whether it can be written as a special case of the identification region; (c) if yes, the criterion; if no, the reason.
    Do not: assume the theorem conditions without the user's reading notes; present content known only from the abstract as a theorem; commit or push.
    Write the result into the repository. Report in the eight-item format, and state plainly whether the conclusion is "can be connected" or "cannot be connected".


Part 1b: the probe by error-structure matrix (analytic only)


Task 1b-1. Probe by error-structure matrix, P0 to P5 against E0 to E6
Output: docs/theory/06_matrix.md and docs/theory/06_matrix.csv (columns: probe, structure, prediction, derivation_summary, failure_condition, confidence).
Done when:
  every cell has an invariance proof, a sensitivity (kappa) derivation, or an explicit "?" with the reason;
  every visible cell is paired with the cells where the same probe is blind (rule R6);
  the validity condition is this project's own quantum condition, stated as an analogy to U-comparability, and labelled as an analogy.
Serves: F1, pain point 1.
Prompt:

    Task: Derive the visibility prediction for probes P0 to P5 under error structures E0 to E6. Analytic work only.
    Inputs: section 4 of docs/project_plan_v0.md; docs/theory/01 to 05; section 1 of docs/reading_notes_2026-11-10.md (the original wording of Lipsitch et al. 2010); the limitations admitted by the authors of Giurgica-Tiron et al. 2020 and Wallman and Emerson 2016 (see docs/inventory_20_step1.md).
    Output format:
      (1) 06_matrix.md, one subsection per cell, with the prediction (visible, blind, partial, or ?), the derivation, and the failure condition;
      (2) 06_matrix.csv with columns probe, structure, prediction, derivation_summary, failure_condition, confidence.
    State the validity condition as "this project's quantum condition, by analogy with the U-comparability of Lipsitch et al. 2010".
    Do not: use simulation results to decide a prediction; describe Lipsitch's condition as "a shared bias mechanism"; mark any cell visible without listing the matching blind cells; commit or push.
    Write the result into the repository. Report in the eight-item format, and also list every "?" cell with its reason.


Task 1b-2. P5 symmetry probe: repositioning and blind-spot derivation (A3)
Output: the P5 subsection of docs/theory/06_matrix.md.
Done when: the text cites the "residual undetectable-sector bias" of arXiv 2606.15464, explains that this project differs by working under a fixed budget, at the decision level, with a global sign criterion, and derives why P5 is blind to errors that preserve the symmetry.
Serves: F1, A3.
Prompt:

    Task: Write the visibility derivation for P5 (symmetry check) and reposition its novelty as decided in A3.
    Inputs: entries 8 and 17 of docs/inventory_20_step1.md; section C.1 of docs/inventory_20_step2_painpoints.md; the relevant passages of arXiv 2606.15464 (re-read them and quote verbatim if you need quotes).
    Output format: one Markdown subsection with: positioning (one paragraph that first says what earlier work already showed), derivation, prediction, failure condition.
    Do not: claim this project was first to find the P5 blind spot; describe 2606.15464 as runtime detection (its residual bias is computed from a noise model and the ideal state); commit or push.
    Write the result into the repository. Report in the eight-item format.


Task 1b-3. Text-level comparison of existing diagnostics (only if A1 is rejected)
Output: docs/related_work_table.md
Done when: W_neg, GVS, DRI and GRI, and the symmetry-verification clip monitoring are compared column by column (needs ideal values or not, what failure it targets, whether its cost is charged to a budget, threshold, whether it targets differential bias between candidates). Every cell can be traced to the original paper. Nothing is marked "no" without a source.
Serves: F3, pain point 6.
Prompt:

    Task: Build a comparison table of existing runtime diagnostics. Text only, no simulation.
    Inputs: section C.1 of docs/inventory_20_step2_painpoints.md; the original papers: Koster and Mauerer 2026 (arXiv 2607.09360), Scavino 2026 (arXiv 2607.02888), Scavino Alfaro 2026 (arXiv 2606.15464).
    Output format: a Markdown table with columns: diagnostic, source, needs ideal values, failure mode targeted, cost charged to a fixed budget, threshold frozen in advance, targets differential bias between candidates, quote.
    Do not: write "no" without a source (write "not seen in what we read"); commit or push.
    Write the result into the repository. Report in the eight-item format.


Part 1c: certificate and Proposition 2 (analytic only)


Task 1c-1. Bias-aware certificate and joint coverage
Output: docs/theory/07_certificate.md
Done when:
  the rule is written: certify only if the lower confidence bound of the gap exceeds B, where B is set by the probe data;
  joint coverage is derived (for example, a union bound that controls the probe interval and the target interval together);
  the difference from Armstrong and Kolesar (whose bias bound is fixed in advance) is stated;
  it is proved that the rule never certifies in a blind direction.
Serves: F2, pain points 2 and 3.
Prompt:

    Task: Derive a bias-aware certificate whose bias bound B is set by the probe data, and prove its joint coverage.
    Inputs: docs/theory/01 to 03; section 3 of docs/reading_notes_2026-11-10.md (Armstrong and Kolesar, original wording) and section 2 (Imbens and Manski).
    Output format: Markdown with LaTeX: the rule; a coverage theorem with proof; the differences from Armstrong and Kolesar, point by point with quotes; a proof that the rule never certifies in a blind direction; one analytic example.
    Do not: claim that coverage is inherited directly from Armstrong and Kolesar; replace a proof with simulation; commit or push.
    Write the result into the repository. Report in the eight-item format, and also list every condition the coverage proof needs.


Task 1c-2. Proposition 2: when is spending budget on probes worth it?
Output: docs/theory/08_prop2.md
Done when: using Proposition 1 as a template, a condition on the probe fraction f is derived. Budget-allocation language cites only verified entries (Kaufmann et al. 2016, Garivier and Kaufmann 2016, Chen et al. 2000).
Serves: F2, minor pain point 2.
Prompt:

    Task: Derive Proposition 2. Out of a total budget N, a fraction fN goes to probes and (1 - f)N to the decision. Find the conditions under which the overall decision error goes down.
    Inputs: Proposition 1 of the previous project (Section 2 of paper/main_v2.tex in adaptive-qem-benchmark; read only, do not edit); item 4 of section 3 of docs/project_plan_v0.md; docs/theory/07_certificate.md.
    Output format: Markdown with LaTeX: proposition, proof, comparison with Proposition 1, conditions under which it holds. Budget-allocation citations may only use verified entries in docs/literature/library.csv.
    Do not: edit the previous repository; cite unverified work; commit or push.
    Write the result into the repository. Report in the eight-item format.


Task 1c-3. Extending Proposition 1: K candidates, estimated gamma, link to the limits literature
Output: docs/theory/09_prop1_ext.md
Done when:
  a version for K candidates is given;
  the correction for gamma and a being estimated from data is given;
  a bound or correction for small samples or non-normal data is given;
  the text explains that gamma is an instance, for a single estimator, of the lower bounds in Takagi et al. and Quek et al.;
  Scavino's effective margin is cited and compared.
Serves: secondary endpoint (the Proposition 1 prediction test), minor pain point 1.
Prompt:

    Task: Extend Proposition 1 of the previous project (Delta_m > sqrt(gamma) Delta_r) to K candidates, to gamma and a estimated from data, and to small samples, and explain its relation to the literature on limits of error mitigation.
    Inputs: Proposition 1 in paper/main_v2.tex of the previous repository (read only); the abstracts and, if read, relevant passages of Takagi et al. 2022 and Quek et al. 2024; Scavino 2026's definition of the effective margin mu_m = Delta + L a_m, with quotes.
    Output format: Markdown with LaTeX: the extended proposition; proof; comparison with Scavino's effective margin; a paragraph linking to Takagi and Quek in which every sentence states its source and how deeply that source was read. Also attach a draft of the pilot estimators and decision rule for the Part 3 prediction test, labelled "to be frozen in Part 1d".
    Do not: state theorem details of Takagi or Quek that are known only from their abstracts; change the primary or secondary endpoints; commit or push.
    Write the result into the repository. Report in the eight-item format.


Task 1c-4. Grow the literature library to at least 90 verified papers
Output: docs/literature/library.csv and paper/references.bib
Done when: at least 90 papers are verified; each has a three-line note; the five partial entries are either completed or stay excluded; the original sources for cluster bootstrap and mixed-effects models are verified.
Serves: literature requirements of the project specification.
Prompt:

    Task: Bring the verified entries in docs/literature/library.csv to at least 90.
    Inputs: docs/literature/library.csv; the open topics in section 8 of docs/literature_review.md (biased or misspecified bandits; model uncertainty in error mitigation; original sources for cluster bootstrap and mixed-effects models).
    What to do: check each paper online (authors, venue, volume, DOI) and record how it was checked in the source_checked column. If a paper cannot be fully checked, mark it partial and keep it out of references.bib.
    Output format: the updated library.csv and references.bib, plus a list of additions (for each paper: how it was checked, how deeply it was read, the three-line note).
    Do not: fill in bibliographic details from memory; put partial entries into references.bib; work around a site that refuses access; commit or push.
    Write the result into the repository. Report in the eight-item format, and attach a consistency check between references.bib and library.csv.


Part 1d: freeze


Task 1d-1. Power analysis by simulation (only after the predictions are frozen)
Output: experiments/power/ (code, raw rows, run log) and docs/freeze/power_analysis.md
Done when:
  it runs only after 06_matrix has been committed;
  it sets a holdout of at least 100 circuits, at least 50 QAOA graphs from at least 3 graph families, and at least 2 circuits for each width and depth;
  the run log records the numpy version and BLAS configuration;
  the scope is set using the frozen scope-cutting rule.
Serves: F1, the power-analysis requirement of the specification.
Prompt:

    Task: Run a power analysis by simulation to set the holdout size and number of repeats.
    Precondition: confirm that docs/theory/06_matrix.csv has been committed by the user. If not, stop and report.
    Inputs: docs/theory/06_matrix.csv; sections 5 and 6 of docs/project_plan_v0.md (endpoints and thresholds).
    Output format: code under experiments/power/ (all seeds derived from ROOT_SEED), raw rows as CSV, a run log (including the numpy version and the output of np.show_config()); docs/freeze/power_analysis.md stating each design parameter chosen and its power, and for every value-versus-threshold decision, how far the value is from the threshold.
    Do not: change any prediction in 06_matrix after seeing the power results; use machine learning; run hardware; overwrite raw rows; commit or push.
    Write the result into the repository. Report in the eight-item format, with the full experiment grid.


Task 1d-2. Frozen protocol
Output: docs/freeze/frozen_protocol_v1.md (with its content hash)
Done when: the structures and parameter grid, probe specifications and cost formulas, thresholds and sensitivity table, development and holdout seed split, primary endpoint, scope-cutting rule, and the pilot procedure and decision rule for the Proposition 1 test are all fixed in writing; items that may be adjusted but must be logged are listed separately.
Serves: pain point 6 and all facets.
Prompt:

    Task: Assemble the frozen protocol.
    Inputs: docs/theory/01 to 09, 06_matrix.csv, docs/freeze/power_analysis.md, docs/project_plan_v0.md.
    Output format: docs/freeze/frozen_protocol_v1.md with these sections in order: scope; definitions; prediction matrix (cite the hash of 06_matrix.csv); probe specifications and costs; thresholds and sensitivity table; data split and seeds; primary and secondary endpoints; scope-cutting rule; Proposition 1 prediction procedure; items that may be adjusted but must be logged; change rules (delays only move later). End with the command that computes the file's content hash.
    Do not: add probes or endpoints the user has not approved; include any simulation result as the basis for a prediction; commit or push.
    Write the result into the repository. Report in the eight-item format.


Task 1d-3. Registration draft for OSF or AsPredicted
Output: docs/freeze/registration_draft.md
Done when: the draft matches the frozen protocol; the user submits it personally and records the timestamp in the repository.
Serves: the registration requirement of the specification.
Prompt:

    Task: Write a draft of the OSF (or AsPredicted) registration form based on docs/freeze/frozen_protocol_v1.md.
    Output format: fill in the platform's fields in their order; for each field, note the matching section of the frozen protocol.
    Do not: submit on the user's behalf; use the word "preregistration" before an independent timestamp exists (write "frozen and committed in this repository" instead).
    Report in the eight-item format, and remind the user to record the timestamp in the repository after submitting.


Part 2: implementation and development set
Starts only after Part 1d is frozen and the previous project is closed.


Task 2-1. Probe implementation and cost ledger
Output: src/probes/ and tests/test_probes.py
Done when: P0 to P5 are implemented (plus P1b and GVS if A1 was adopted); tests confirm that total shots in every run equal the budget; a test enforces that probes never receive ideal values.
Serves: F1, F2.
Prompt:

    Task: Implement the probes and the cost ledger exactly as specified in the frozen protocol.
    Input: the probe specifications and cost formulas in docs/freeze/frozen_protocol_v1.md.
    Output format: a src/probes/ module (one function per probe, returning its statistic and the number of circuits and shots it actually used); tests/test_probes.py with at least these tests: total shots equal the budget; probe functions take no ideal-value argument; results are reproducible from the seed.
    Do not: change any specification in the frozen protocol; use machine learning; run ruff format on the whole repository (format new files only); commit or push; run git on the user's computer.
    Write the result into the repository. Report in the eight-item format, and give the pytest command (on Windows add --basetemp="$env:TEMP\qem-pytest").


Task 2-2. Positive and negative controls, and cross-checks with independent code
Output: experiments/dev_controls/ and docs/dev/controls_report.md
Done when: cases with an analytically known bias trigger the alarm; the false-alarm rate under E0 is close to alpha; P1 is cross-checked with Mitiq's folding; the Clifford ideal values used by P2 are cross-checked with two different stabilizer simulators.
Serves: pain point 6, the cross-validation requirement of the specification.
Prompt:

    Task: Run positive and negative controls and cross-checks on the development set.
    Inputs: docs/freeze/frozen_protocol_v1.md; src/probes/.
    Output format: code, raw rows and run log under experiments/dev_controls/; docs/dev/controls_report.md listing each check as passed or failed, with its value and its distance from the threshold.
    Do not: read any data from holdout seeds; change probe specifications or loosen tolerances when a check fails; delete failed runs; commit or push.
    Write the result into the repository. Report in the eight-item format, grouping failures by cause (method, resources, model, design).


Task 2-3. Calibrate alarm thresholds from E0 only, then commit
Output: docs/dev/thresholds_v1.md and a list of development-set mismatches.
Done when: thresholds are calibrated from the E0 null distribution following the frozen procedure; every cell where the development data disagree with the prediction is listed; the theory is not changed.
Serves: pain point 6, F1.
Prompt:

    Task: Following the frozen procedure, calibrate the alarm thresholds using only the E0 (common-mode) null distribution, and list the cells where the development data disagree with the predictions.
    Inputs: docs/freeze/frozen_protocol_v1.md; raw rows in experiments/dev_controls/.
    Output format: docs/dev/thresholds_v1.md (threshold, calibration sample size and sensitivity for each probe); docs/dev/dev_mismatch.md (for each mismatched cell: prediction, observation, possible cause).
    Do not: change predictions in 06_matrix or any theory document because of mismatches; read the holdout; commit or push.
    Write the result into the repository. Report in the eight-item format, and remind the user to commit the threshold file before Part 3.


Part 3: confirmatory holdout


Task 3-1. One-time holdout scoring (primary endpoint)
Output: results/holdout/ (raw rows, summary, run log) and docs/results/primary_endpoint.md
Done when: it runs exactly once; the agreement rate between predicted and observed visibility is reported with a Wilson interval; it can be recomputed independently from the raw rows; it is run on both Windows and Linux and the two are compared.
Serves: F1 (primary).
Prompt:

    Task: Compute the primary endpoint on the holdout. Run it exactly once.
    Precondition: confirm that the threshold file and the frozen protocol have been committed. If not, stop and report.
    Inputs: docs/freeze/frozen_protocol_v1.md; docs/dev/thresholds_v1.md; src/probes/.
    Output format: raw rows in results/holdout/ (never overwritten); a summary script that recomputes everything from the raw rows; a run log (numpy version and BLAS configuration); docs/results/primary_endpoint.md (agreement rate, Wilson interval, result for every cell, distance from each threshold).
    Do not: change any rule or threshold after seeing results; rerun the holdout; delete rows that fail checks; commit or push.
    Write the result into the repository. Report in the eight-item format, and report unfavourable results plainly.


Task 3-2. Bias-aware certificate versus confidence-interval-only (secondary, F2)
Output: docs/results/secondary_certificate.md
Done when: false-certification rate and unresolved rate are reported for both rules under the same total budget, with intervals.
Serves: F2.
Prompt:

    Task: On the holdout data, compare the bias-aware certificate with the confidence-interval-only certificate. This is a secondary endpoint.
    Inputs: raw rows in results/holdout/; the frozen rule in docs/theory/07_certificate.md.
    Output format: docs/results/secondary_certificate.md with the false-certification rate, unresolved rate and Wilson intervals for both rules, clearly labelled as a secondary endpoint.
    Do not: change the certificate rule; present secondary results as the main conclusion; commit or push.
    Write the result into the repository. Report in the eight-item format.


Task 3-3. Proposition 1 prediction test (secondary, run once)
Output: docs/results/prop1_prediction_test.md and a predictions file that is committed and registered before the scoring data are run.
Done when: the steps happened in this order: pilot; predictions written to a file; the user commits and registers them; scoring data; hit rate reported once.
Serves: secondary endpoint.
Prompt:

    Task: Run the Proposition 1 prediction test, exactly once.
    Step one (then stop): run the pilot, compute a and gamma for each new graph using the frozen estimators, write the prediction (raw better or ZNE better) for each graph using the frozen decision rule, and save it as results/prop1/predictions.csv. Then stop and ask the user to commit and register it.
    Step two: only after the user reports the commit hash and the registration timestamp, run the scoring data and compute the hit rate.
    Output format: predictions.csv; docs/results/prop1_prediction_test.md (hit rate, interval, result for each graph).
    Do not: run the scoring data before the user reports back after step one; change any prediction; rerun; commit or push.
    Write the result into the repository. Report in the eight-item format.


Part 4: synthesis and paper


Task 4-1. Boundary map and failure causes
Output: figures/boundary_map.* and docs/results/boundary_synthesis.md
Done when: the boundary map (structure by bias-to-gap ratio by required probe fraction) is drawn; every failure is grouped by cause (method, resources, model, design); the F3 comparison is done by simulation or as text, depending on the A1 decision.
Serves: F1, F3.
Prompt:

    Task: Produce the visibility boundary map and the classification of failure causes.
    Inputs: results/holdout/, docs/results/*.md, docs/theory/06_matrix.csv.
    Output format: figures/boundary_map.png whose caption starts with the conclusion; docs/results/boundary_synthesis.md (for each cell: prediction, observation, cause category, evidence type). Compare figures at the pixel level, and run provenance --write only after all generation steps.
    Do not: present exploratory results as confirmatory; hide mismatched cells; commit or push.
    Write the result into the repository. Report in the eight-item format.


Task 4-2. Hardware go or no-go review
Output: docs/hardware/review_v1.md
Done when: the review follows the time budget and reduction rules in section 13 of the plan; IBM's current plan terms have been checked; the verdict is no-go if evidence is insufficient; a go verdict still needs the user's explicit authorization before anything runs.
Serves: the hardware review requirement of the specification.
Prompt:

    Task: Review whether the readout hardware experiment (P4a and P4b) should go ahead. Do not run any hardware.
    Inputs: section 13 of docs/project_plan_v0.md; IBM Quantum's current official plan terms, looked up online (record the date and URL).
    Output format: docs/hardware/review_v1.md: each go condition checked one by one, the no-go triggers, a time-budget estimate (never using an unmeasured time per shot), and the verdict.
    Do not: submit any job; ask for, print or store an API key; treat the experiment as approved without the user's explicit authorization; commit or push.
    Write the result into the repository. Report in the eight-item format.


Task 4-3. Claims list, then the paper draft
Output: paper/claims.md (written first) and paper/main.tex
Done when: the claims list is finished first, with an evidence type and strength for every claim; the abstract has at most three numbers; every section opens with its conclusion; novelty uses the four-condition statement, qualified with "in what we read"; the limitations section includes the narrow evidence base; every citation key is in references.bib and every bib entry is cited.
Serves: all facets; A4, A5, A6.
Prompt:

    Task: Write the claims list first, then the first draft of the paper.
    Inputs: docs/results/*.md, docs/theory/*.md, paper/references.bib, docs/inventory_20_step2_painpoints.md, docs/inventory_20_step3_facets.md.
    Output format:
      (1) paper/claims.md: each claim with its evidence type (analytic, noiseless simulation, noisy simulation, device-parameter simulation, hardware), its strength, and the file it comes from;
      (2) paper/main.tex in the same format as the previous report; at most three numbers in the abstract; every section opens with its conclusion; each number appears in one place only.
    Do not: claim general laws (claim existence only); write "earlier work did not do X" (write "not seen in what we read"); cite anything outside references.bib; commit or push.
    Write the result into the repository. Report in the eight-item format, and attach a two-way consistency check between citation keys and references.bib.


Freeze rules

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


Not done in this round

Narrow evidence base and unclear generalization (former pain point 7). This project is mainly simulation and has the same problem. It is acknowledged in the limitations section, and conclusions are limited to existence claims. The user decided this on 2026-11-10.

Pain point 4 (benchmarks stop at estimator accuracy) gets no facet of its own. Scavino 2026 already addresses "accuracy is not the same as a good decision". It stays as background and is covered by the secondary endpoint for Proposition 1.

Minor pain point 1 (limits theory has no decision-level counterpart). Only two sources support it. It is addressed only when writing, to answer the expected examiner question about limits of error mitigation.

A1 (W_neg as a probe) is deferred. It must be decided before Part 1a starts. If rejected, F3 is a text-level comparison only (task 1b-3).

Full readout-correlation correction. This project detects bias; it does not mitigate it.

A full proof of randomized compiling under general noise. That belongs to the theory of randomized compiling itself.

Worst-case versus typical-case limits of error mitigation. That belongs to estimator-level limits research.

Scalability of characterization protocols. Dedicated work already exists.

Statistical rigour of error-mitigation benchmarking as a topic. Koster and Mauerer (arXiv 2605.29872) already address it; this project only adopts their recommended practices.
