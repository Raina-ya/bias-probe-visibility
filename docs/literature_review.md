# Literature Review: Visibility Boundary of Bias Probes

Library: literature/library.csv (86 entries, each with a verification status and a three-line note).
Bibliography: ../paper/references.bib (81 entries, verified sources only; can be imported directly into Zotero).
Close reading of key passages: reading_notes_key_sources.md.

## 1. Summary

1. The library contains 86 entries. 81 are verified and citable; 5 have incomplete bibliographic records and are kept out of the bibliography.
2. The literature supplies four existing theoretical anchors, so "the probe can see it" and "the probe cannot see it" can be defined in established terms rather than invented ones:
   (A) Learnability and gauge freedom of noise: part of Pauli noise cannot be learned in principle (Chen et al. 2023), and gate set tomography has a gauge freedom (Nielsen et al. 2021).
   (B) Partial identification: when bias cannot be fully identified, the decisive gap is identified only up to a set (Imbens and Manski 2004; Tamer 2010).
   (C) Negative controls: the original condition is U-comparability, meaning the negative control and the target share the same set of unobserved common causes and the negative control is not affected by the exposure (Lipsitch et al. 2010). Applied to probes, it can only be an analogy.
   (D) Bias-aware confidence intervals: the critical value is adjusted by a bias bound so that coverage holds (Armstrong and Kolesar 2020).
3. These anchors shape the research plan (section 5). The most important consequence is that Lemma 1 must be defined over the pair (ideal gap, noise), not over the noise alone.
4. Novelty is stated narrowly (section 6): runtime diagnostics for specific failure modes already exist, and the claim of this project is limited to a specific combination of four properties.

## 2. Verification method and limitations

Each entry was found through web search and then checked against one publicly accessible record: an arXiv abstract page, DOAJ, Crossref, RePEc, a publisher page, or an institutional repository. The fields checked are recorded in the source_checked column of library.csv.

Status categories:
  verified: authors, venue, volume and DOI (where one exists) match an online record. For some APS and Quantum articles, the volume and article number are read from the DOI; this is noted in source_checked.
  verified (previous project): carried over from the verified bibliography of the previous project.
  verified-preprint: available only as an arXiv preprint.
  partial: volume or DOI is missing. These entries are not in references.bib.

Limitation 1: no full text has been read word for word. The basis of each note is recorded in the note_basis column:
  relevant passages read: the passages relevant to this project were read in the original;
  abstract read: only the abstract or an abstract-level page was read;
  previous project: the judgement of the previous project is carried over;
  background knowledge, abstract not read, to be confirmed: the note is only a lead.
Accordingly, numbers from new sources are not cited until the source has been read closely.

Limitation 2: automated bibliographic APIs (Crossref, arXiv) were not reachable from the working environment, so every record was checked page by page rather than in batch.

The previous bibliography cited Bultrini et al. as an arXiv preprint. It has since been published in Quantum 7, 1034 (2023), and the published version (bultrini2023) is used.

Items previously flagged as unverified, now verified:

| Item | Result |
|---|---|
| TREX (twirled readout) | van den Berg, Minev and Temme, PRA 105, 032620 (2022) |
| Zhou et al. 2020 (PRX) | PRX 10, 021067 (the QAOA paper) |
| Kim and Nelson | Handbooks in OR and MS 13, 501-534 (2006) |
| OCBA (Chen et al.) | Discrete Event Dynamic Systems 10, 251-270 (2000) |
| Kaufmann et al. 2016 | JMLR 17, 1-42 |

## 3. Map of the literature (six categories)

| Category | Entries | Most important for this project |
|---|---|---|
| QEM methods | 23 | Temme 2017, Giurgica-Tiron 2020 (P1 folding); Wallman and Emerson 2016 (P3 randomized compiling); Czarnik 2021, Lowe 2021 (P2 Clifford); Bonet-Monroig 2018 (symmetry check) |
| Statistical decision | 20 | Imbens and Manski 2004, Tamer 2010 (partial identification); Armstrong and Kolesar 2020 (bias-aware intervals); Lipsitch 2010 (negative controls); Kaufmann 2016, Chen 2000 (budget allocation) |
| Benchmarking and characterization | 21 | Chen 2023 (learnability), Nielsen 2021 (GST gauge); Proctor 2022 (mirror circuits); Sarovar 2020 (crosstalk detection); Kueng 2016, Sanders 2016 (coherent error and average metrics); Scavino 2026 and Scavino Alfaro 2026 (decision kernels, operating windows); Koster and Mauerer 2026 (artefacts in ZNE benchmarks) |
| Hardware experiments | 9 | Hashim 2021 (randomized compiling on hardware); Kim 2023, Nature Physics (large-scale ZNE); Sagastizabal 2019 (symmetry verification on hardware) |
| Readout | 7 | van den Berg 2022 (TREX); Maciejewski 2021 (readout crosstalk); Chen 2019 (detector tomography) |
| QEM limits | 6 | Takagi 2022 and 2023, Quek 2024, Tsubouchi 2023 |

## 4. Research anchors drawn from the literature

### (A) Learnability and gauge freedom: physical content for "blind in principle"

What it says. According to the abstract of Chen et al. (2023), for Pauli noise on Clifford gates the learnable part corresponds to the cycle space of the pattern transfer graph, and the cut-space part cannot be learned at all. Nielsen et al. (2021) treat gauge freedom as a core issue of gate set tomography.
How it is used. Probe data can identify only the learnable part of the noise. If the differential bias of a decision is sensitive to an unlearnable component, and that sensitivity is large enough to offset Delta, then no combination of probes can see it. This is a first class of blindness in principle, arising from the non-identifiability of the noise itself rather than from poor probe design.
Falsifiable prediction (to be derived in Part 1). The projection of the differential bias beta onto the cut-space components can serve as a criterion for blindness.
Reading priority: first.

### (B) Partial identification: a statistical definition of "visible" and "blind"

What it says. The parameter is written as (Delta, e), where Delta is the ideal gap and e is the noise. The data (target plus probes) restrict (Delta, e) only to an identification set.
Definition of blind. The identification set contains both a point with Delta > 0 and a point with Delta <= 0. Probes act by adding constraints on e, which shrinks the identification set.
Why this form. A formulation of the form "there exist e1, e2 with the same observable distribution but different sign(Delta + beta)" can never hold, because the observable distribution itself determines Delta + beta. The real question is whether Delta + beta can be separated from Delta, that is, whether beta can be identified when Delta is unknown.
Use. Imbens and Manski (2004) give confidence intervals for identification sets, which apply directly to the bias-aware certificate.

### (C) Negative controls: a validity condition for each probe cell

What it says. A negative control is a comparison whose true effect is known to be zero; a nonzero result signals bias.
Original condition. The condition in Lipsitch et al. (2010) is called U-comparability: the negative control and the target have the same, or as nearly as possible the same, set of unobserved common causes, and the negative control is not affected by the exposure. The original text does not describe it as a "shared bias mechanism". The original wording is in section 1 of the reading notes. Applied to quantum probes, it can only be an analogy.
Correspondence with this project:
  the P2 Clifford twin is a negative control, because its ideal value is known;
  P1 folding and P3 twirling change the bias without changing the ideal value and can be viewed as another kind of control;
  the P5 symmetry check uses a component whose ideal value is known to be zero.
Use. The visible or blind prediction for each probe-by-structure cell can be stated through one quantum condition defined by this project, by analogy with U-comparability (research plan, section 3.5).
Reporting. The sensitivity analyses of Rosenbaum (1987) and VanderWeele and Ding (2017) provide a format for "how large a bias would overturn the conclusion". For each decision, this project reports the minimum differential bias needed to flip it.

### (D) Bias-aware intervals: coverage guarantees for the certificate

What it says. According to Armstrong and Kolesar (2020), when an estimator may be biased, adjusting the critical value by a bias bound guarantees coverage.
Use. The bias-aware certificate of this project (certify only if the lower confidence bound of the gap exceeds the largest probe-compatible bias B) has this form. Because B comes from probe data rather than from a bound fixed in advance, the coverage argument must be extended (research plan, section 3.7).

### (E) Budget allocation: language for Proposition 2

What it says. Best-arm identification (Kaufmann et al. 2016; Garivier and Kaufmann 2016) and OCBA (Chen et al. 2000) deal with how a finite sample is split among candidates.
Use. This project adds one dimension: whether to spend samples on probes or on the target.

### Other findings that bear directly on probe design

Coherent error hides in averages. Kueng et al. (2016) and Sanders et al. (2016) show that average fidelity does not constrain the worst case of coherent error. This supports treating E2 as a key structure and justifies P3 (randomized-compiling contrast).
Crosstalk can be detected through conditional dependence. Sarovar et al. (2020) detect crosstalk from conditional dependences in observed probabilities. This is a design reference for an E3 (ZZ) probe, where the prediction is least certain.
The symmetry check is an existing zero-cost probe. Bonet-Monroig et al. (2018) include a zero-cost post-processing version. Its blind spot for symmetry-preserving errors is the clearest example of blindness caused by invariance; it is included as P5.
Correlated readout may exist on real devices. Chen et al. (2019) report suspected measurement crosstalk on IBM five-qubit devices and recommend joint modelling (hardware evidence from others, abstract only). This motivates the Part 4 hardware experiment but is not evidence for this project.

## 5. Consequences for the research plan

1. Lemma 1 is written in partial-identification form, following Imbens and Manski as Delta = f(P, e) (anchor B).
2. P5, the symmetry check, is included as a zero-cost baseline probe with no extra shots. If the Part 1 power analysis shows the scope is too large, the frozen scope-cutting rule applies.
3. The validity condition of each probe is stated through a quantum condition defined by this project, by analogy with U-comparability (anchor C). The bias-aware certificate takes the form of an honest confidence interval (anchor D), with its own coverage derivation.
4. The learnability criterion (anchor A) is a theoretical goal, as a first class of blindness in principle. Together with the estimator-level lower bounds of Takagi, Quek and Tsubouchi, it shows what this project adds at the decision level.

## 6. Novelty: what can and cannot be claimed

Cannot be claimed: that runtime detection has never been done. The W_neg diagnostic of Koster and Mauerer (2026) is a runtime diagnostic that needs no ideal values; it targets a single failure mode (Richardson ZNE when the signal reaches the floor), and its authors state that it has no formal threshold. Scavino Alfaro (2026, arXiv 2606.15464) has already stated that symmetry verification leaves a "residual undetectable-sector bias", although that bias is computed from a model and the ideal state, not detected at runtime.

Can be claimed, qualified by "in what we read": no existing diagnostic does all of the following:
  1. targets the differential bias between candidates and the top-1 decision;
  2. charges the probe cost to a fixed total budget;
  3. uses an alarm threshold frozen in advance and open to falsification;
  4. determines under which error structures every probe is blind in principle.

Local versus global. Corollary C.1 of Scavino (2026) is a local identifiability condition; the notion of "blind" in this project is a global sign condition. The two do not contain each other. This is an inference that Part 1a turns into a proposition with counterexamples.

Limits literature. It answers the expected examiner question about limits of error mitigation and is not a pillar of novelty; within the 20-paper inventory, it has only two sources.

The detailed basis is in inventory_20_step2_painpoints.md.

## 7. Reading list

| Order | Source | Question to answer |
|---|---|---|
| 1 | Chen et al. 2023 (learnability) | Definition of the cut space; whether the differential bias can be projected onto it |
| 2 | Imbens and Manski 2004 | Construction and conditions of the confidence interval for an identification set |
| 3 | Armstrong and Kolesar 2020 | How the bias bound enters the critical value; whether it applies directly to the gap |
| 4 | Lipsitch et al. 2010 | Original statement of the validity condition for negative controls |
| 5 | Scavino Alfaro 2026 | Differences from this project (decision risk) |
| 6 | Koster and Mauerer 2026 | Whether artefactual ZNE improvement is the same as the P1 blind spot |
| 7 | Nielsen et al. 2021 (GST) | What gauge freedom means for probes |
| 8 | Wallman and Emerson 2016 | Exact conditions of twirling invariance (P3 blind spot) |
| 9 | Proctor et al. 2022 (mirror circuits) | Whether mirror structure can implement P1 or P2 |
| 10 | Sarovar et al. 2020 | Whether the conditional-dependence test can become an E3 probe |
| 11 | Czarnik 2021, Lowe 2021 | When Clifford training circuits stop being representative (P2 failure) |
| 12 | Bonet-Monroig 2018 | Exact form of the zero-cost symmetry check (P5) |
| 13 | Kueng 2016 | Whether the square-root relation for coherent error can be used in E2 sensitivity |
| 14 | Takagi 2022, Tsubouchi 2023 | Relation between their lower bounds and the shot lower bound of this project |
| 15 | Kaufmann 2016 | Form of the sample-complexity lower bound; whether it applies to Proposition 2 |

## 8. Remaining gaps

The 5 partial entries need volume or DOI: Le Cam 1973, Kim 2023 (Nature Physics), Russo 2023, Gambetta 2012, Magesan 2011.
Topics not yet searched: best-arm identification with biased arms (biased or misspecified bandits); model uncertainty and robust inference in QEM; original sources for cluster bootstrap and mixed-effects models.
Target: at least 90 verified entries by the end of Part 1, and close reading of the first 15 sources on the reading list, with the citability field updated.
