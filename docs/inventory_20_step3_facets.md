# Research Facets and Plan Settings

This document derives the research facets of the project from the common pain points (docs/inventory_20_step2_painpoints.md) and records the resulting settings of the research plan, each with its rationale and cost.

## 1. Research facets

### Facet F1: visibility boundary (global sign criterion and probe matrix)

What. Under a fixed total budget, for every combination of probe and error structure, use the global sign criterion (whether the identification region contains gaps of both signs) to classify the differential bias as visible, blind within budget, or blind in principle, and test the predictions, frozen in advance, on the holdout.
Purpose. To state where each method fails (pain point 1) and to connect identifiability to concrete decisions in a global rather than local sense (pain point 5).
Basis. Lemma 1 in the form of Imbens and Manski (2004); Scavino (2026), Corollary C.1, as the local condition to be contrasted; the invariance and failure conditions stated by Giurgica-Tiron et al. (2020) and Wallman and Emerson (2016).
Expected output.
  Propositions: the global sign criterion of Lemma 1; a local-versus-global proposition with two counterexamples, contrasted with Scavino's Corollary C.1.
  Boundary conditions: an invariance proof or sensitivity derivation for every cell of the probe-by-structure matrix.
Endpoint level: primary. This is the existing primary endpoint of the plan, the agreement rate between predicted and observed visibility on the holdout.

### Facet F2: bias-aware certificate with a data-driven bias bound

What. Use probe data to set B, the largest differential bias compatible with the data; certify only when the lower confidence bound of the gap exceeds B; derive joint coverage of the probe interval and the target interval.
Purpose. To provide a certificate that does not assume bias is known or computable from ideal values (pain point 2), and that controls bias rather than only sampling error (pain point 3).
Basis. Armstrong and Kolesar (2020), honest confidence intervals with a bias bound fixed in advance; Imbens and Manski (2004), confidence intervals for identification regions.
Expected output.
  Method: the certification rule.
  Proposition: joint coverage, extending the prior bias bound of Armstrong and Kolesar to a data-dependent bound.
  Comparison table: false-certification rate and unresolved rate against the confidence-interval-only certificate under the same total budget.
Endpoint level: secondary, identical to the existing secondary endpoint of the plan.

### Facet F3: existing diagnostics compared on the same visibility matrix

What. Treat the W_neg diagnostic of Koster and Mauerer (no ideal values needed) and the GVS diagnostic of Scavino (no margins included) as existing diagnostics, place them in the matrix next to P0 to P5, and compare them under the same frozen thresholds and budget accounting.
Purpose. To give diagnostics a formal, falsifiable threshold (pain point 6), and to support the restated gap: in what we read, no existing diagnostic combines differential bias, budget accounting, a frozen threshold and a determination of blindness in principle.
Basis. Koster and Mauerer (2026); Scavino (2026), Section 10.
Expected output.
  Comparison table: the visibility and cost of each diagnostic under each structure.
  Boundary conditions: by its definition, W_neg targets only the failure of Richardson ZNE at the floor and is expected to be blind away from the floor and under readout structures (an inference, to be derived in Part 1b).
Endpoint level: exploratory. It is kept out of the primary endpoint so that the testing burden on the holdout does not grow.

### Pain points without a facet of their own

Pain point 4 (benchmarks stop at estimation accuracy). Scavino (2026) already addresses the point that accuracy is not the same as a good decision, so this project has no novelty there. It remains background and positioning and is covered by the existing secondary endpoint for Proposition 1.
Minor pain point 1 (limits theory stops at the estimator level; two sources). Support is insufficient. It is addressed only in writing, to answer the expected examiner question on limits (gamma is an instance of those lower bounds).
Minor pain point 2 (detection cost is not charged to a budget; two sources, inferred). It is already covered by the fixed-budget setting of F1 and F2.

## 2. Settings adopted in the research plan

The order and content of the Parts are fixed before Part 1a begins and are not changed afterwards. All settings below, including the W_neg extension, are made before Part 1a starts.

### Local-versus-global proposition in Part 1a (adopted)

What. Add to Part 1a a proposition that local identifiability and the global sign criterion do not contain each other, with two counterexamples, contrasted with Scavino's Corollary C.1 (F1).
Purpose. Without it, the project cannot answer a reviewer who asks how its notion of blindness differs from Corollary C.1.
Cost. Additional work in Part 1a. It first requires settling whether Scavino's theta includes noise parameters, which needs the full derivation in Appendix C. Under the schedule rule, any overrun moves later stages later.
Effect on frozen rules: none.

### Repositioning of P5 (adopted)

What. The plan states that the P5 blind spot has already been pointed out by Scavino Alfaro (2026, arXiv 2606.15464) as a "residual undetectable-sector bias", and that this project's contribution is to place it on the same boundary map as the other probes, under a fixed budget, at the decision level, and with a global sign criterion.
Purpose. The novelty claim must not include something earlier work has already shown.
Cost. Text only, with almost no research cost; the novelty claim for P5 is weaker.
Affected Parts: Part 1b (statement of the P5 predictions) and Part 4 (writing).
Effect on frozen rules: none. P5 remains in the probe set; only its positioning changes.

### Four-condition novelty statement (adopted)

What. The novelty statement in the research plan (section 0) and the literature review (section 6) uses the four-condition version from C.1 of the pain-point analysis instead of "no runtime detection has been seen".
Purpose. A runtime diagnostic without ideal values (W_neg) already exists, so the broader statement is no longer accurate.
Cost. Text only.
Effect on frozen rules: none.

### Narrow evidence base in the limitations section (adopted)

What. The plan's list of scientific concerns includes the narrow evidence base: this project shares the problem, does not address it, and limits its conclusions to existence claims.
Purpose. The limitation is supported by eight independent sources and applies to this project as well; stating it in advance keeps the conclusions honest.
Cost. Text only.
Effect on frozen rules: none.

### Treatment of the limits literature (adopted)

What. The paper's related work cites Takagi 2022, Takagi 2023, Quek 2024 and Tsubouchi 2023 (all in the library), but "limits theory lacks a decision level" is not used as a main pain point or a pillar of novelty. The 20-paper inventory is not changed for this purpose.
Purpose. The claim has only two sources within the inventory.
Cost. None in research terms.
Effect on frozen rules: none.

### Primary endpoint unchanged (adopted)

What. F1 corresponds to the existing primary endpoint; F2 and the Proposition 1 test remain secondary; F3 is exploratory.
Purpose. The project keeps a single primary endpoint, and the Proposition 1 test remains a secondary endpoint run once.
Cost. None.

### W_neg as probe P1b, with GVS as a reference baseline (adopted)

What. Add W_neg to the probe set as P1b in the P1 family and use GVS as a reference baseline (F3).
Purpose. It most directly supports the restated novelty, because existing diagnostics would be compared on the same map.
Cost. Two more rows in the matrix. Part 1b must derive the visibility of W_neg and GVS under each structure; Part 2 implements two more statistics (W_neg uses existing counts and needs no extra shots); Part 3 needs more computation. The probe set grows from seven to nine, and the priority order of the scope-cutting rule (research plan, section 9, item 4) must be rewritten, with the F3 diagnostics cut first.
Affected Parts: 1b, 2 and 3.
Effect on frozen rules: none.
Consequence. F3 is compared by simulation on the same matrix, and the text-level comparison task (task 1b-3) does not apply. P1b and GVS cells are exploratory and excluded from the primary endpoint.

### Consequence for the schedule

The local-versus-global proposition adds work to Part 1a. Under the schedule rule, later stages move later and their content does not change. The task list is in docs/inventory_20_step4_schedule.md.
