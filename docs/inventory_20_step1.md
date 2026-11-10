# Inventory of 20 Key Papers

This inventory selects 20 papers from the verified entries of the literature library and records, for each one, how deeply it was read, what it leaves open, what can be cited from it, and how it relates to this project.

## Method

Selection pool. Only verified entries in docs/literature/library.csv are eligible.

Reading depth is stated as it actually is:
  relevant passages: the passages relevant to this project were read in the original;
  full text, extracted: a reading tool scanned the full text and extracted passages; this is not a word-for-word reading;
  abstract: only the abstract or an abstract-level page was read.
No paper was read word for word in full. Chen et al. (2023) and Imbens and Manski (2004) are also read in full by the project owner.

Open issues record only what was read. "Stated by the authors" marks a limitation the paper itself states. "Not seen" means it did not appear in what was read; it does not mean the paper lacks it.

Counting rule. When pain points are counted across these papers, a series of papers by the same author counts as one source. Entries 8 and 9 (Scavino Alfaro; Scavino) therefore count as one source, giving 19 independent sources.

## Selection criteria

1. Papers that directly support the theoretical definitions of this project: identifiability, partial identification, bias-aware intervals, negative controls.
2. The method source of each probe (P1, P2, P3, P5, and the readout probe P4), because each probe needs a stated failure condition.
3. The closest competing or contrasting work, because every cell of the related-work comparison must be traceable to the original paper.
4. The literature on limits of error mitigation, needed to answer the expected examiner question on that topic.

Composition: statistical decision 3; benchmarking and characterization 9 (two competing: entries 9 and 10; entry 8 contrasting); QEM limits 2; QEM methods 4; hardware experiments 1; readout 1.

## Entries

1. Chen et al. 2023, The learnability of Pauli noise
Category: benchmarking and characterization
Reading depth: abstract (read in full by the project owner)
Open issues: the result concerns Pauli noise on Clifford gates; the abstract does not say whether it extends to non-Clifford targets or to coherent noise. The abstract reports that assuming perfect state preparation and measurement gave unphysical results, and a lower bound on state-preparation noise was given instead.
Citable points: the learnable part equals the cycle space of the pattern transfer graph, and the unlearnable part equals the cut space (theorem conditions to be confirmed in the full text).
Relation to this project: support.

2. Nielsen et al. 2021, Gate set tomography
Category: benchmarking and characterization
Reading depth: abstract
Open issues: the abstract says only that gauge freedom and gauge fixing are covered; how gauge freedom affects observables and decision quantities was not read and cannot be judged.
Citable points: the existence of gauge freedom and the self-consistent characterization framework of GST (sections to be read).
Relation to this project: support.

3. Imbens and Manski 2004
Category: statistical decision
Reading depth: relevant passages (Sections 1 to 3)
Open issues: the paper does not formally define "partially identified" (it refers to Manski 2003); the set of admissible A is fixed in advance; stated by the authors: the coverage of the simplest interval does not converge uniformly across widths of the identification region, so a modified interval is proposed.
Citable points: theta = f(P, A); identification region {f(P, A') : A' in the admissible set}; an interval that covers the true value rather than the whole region.
Relation to this project: support.

4. Armstrong and Kolesar 2020
Category: statistical decision
Reading depth: relevant passages (Sections 1 and 2)
Open issues: the worst-case bias comes from a function class F(M) fixed in advance, so M must be known; the setting is a single scalar parameter in nonparametric regression.
Citable points: interval = estimate plus or minus cv_{1-alpha}(t) times the standard error, where cv is a quantile of |N(t,1)|; coverage holds uniformly over the parameter space.
Relation to this project: support.

5. Lipsitch et al. 2010
Category: statistical decision
Reading depth: relevant passages (section on the choice of negative controls)
Open issues: the condition is stated in degrees ("To the extent that … overlaps", "as nearly identical as possible"); no quantitative test was seen; the setting is observational epidemiology.
Citable points: the original definition of U-comparable; the requirement that the negative control is not affected by the exposure.
Relation to this project: support, by analogy.

6. Takagi et al. 2022
Category: QEM limits
Reading depth: abstract
Open issues: the abstract says the bounds apply to a "general class" of protocols but does not define that class; only estimation error and sampling cost are treated, not decisions.
Citable points: for layered circuits under local depolarizing noise, the sampling cost to reach a fixed accuracy grows exponentially with depth; under local dephasing, PEC is optimal within a broad class of strategies.
Relation to this project: contrast (estimator level).

7. Quek et al. 2024
Category: QEM limits
Reading depth: abstract level (opening of the arXiv HTML)
Open issues, stated by the authors: worst-case bounds; the hard circuits are highly entangling and the main construction uses all-to-all connectivity; the non-unital case uses a simplified 2-design model; QEM at small noise is not ruled out; typical cases are left for further study.
Citable points: the distinction between weak and strong mitigation; coverage of VD, CDR, ZNE and PEC; under local depolarizing noise the sample cost grows superpolynomially with qubit number and depth (worst case).
Relation to this project: contrast (estimator level).

8. Scavino Alfaro 2026, Certified Finite-Shot Operating Windows for Virtual Distillation and Symmetry Verification
Category: benchmarking and characterization
Reading depth: full text, extracted
Open issues: certification mainly addresses sampling error; bias is handled by a local first-order expansion ("The noisy state is assumed to admit the first-order expansion in Equation (4)"); the bias coefficients depend on the ideal state, the observable and the noise model; estimator MSE is compared, not decisions; no general runtime detection of model misspecification was seen. Stated by the authors: "The hardware layer is qualitative and budget-limited"; the strict all-instance validation criterion was not met in one Level 1 family.
Citable points: the symmetry-verification result explicitly reports a "residual undetectable-sector bias"; a sample-size threshold for trusting the virtual-distillation denominator; a selection trichotomy for comparing two methods.
Relation to this project: contrast. It is existing evidence for the predicted P5 blind spot, not runtime detection. Same author series as entry 9.

9. Scavino 2026, Decision Kernels for Quantum Error Mitigation
Category: benchmarking and characterization
Reading depth: full text, extracted
Open issues: in what we read, how â_m is obtained is not stated; the identifiability condition is local; what theta contains is not stated; the hardware decision criterion was not met; future work listed by the author includes sequential allocation, stopping rules and best-arm-identification guarantees.
Citable points: decisions depend only on gaps; common-mode shifts are removed by the contrast map L; the original statement of the condition in Corollary C.1.
Relation to this project: competing (closest).

10. Koster and Mauerer 2026
Category: benchmarking and characterization
Reading depth: full text, extracted
Open issues, stated by the authors: hardware evidence from one device and one circuit family; simulations assume ideal depolarizing noise; W_neg has no formal threshold and was validated only on the circuits studied; the onset depth and noise level depend on the device.
Citable points: when the signal sits at the floor, Richardson ZNE reduces to a fixed rescaling Ê(0) = (15/8)E(lambda_1) - (7/8)f; W_neg needs no ideal values; garbage folding is used as a negative control.
Relation to this project: competing and contrasting (an existing runtime diagnostic, close to P1).

11. Bultrini et al. 2023
Category: benchmarking and characterization
Reading depth: abstract
Open issues: only estimation accuracy is compared, not decisions; the noise model is a simulated trapped-ion model.
Citable points: the performance of each method depends strongly on the shot budget; UNITED is most accurate at the largest budget.
Relation to this project: contrast.

12. Cirstoiu et al. 2023
Category: benchmarking and characterization
Reading depth: abstract
Open issues: the journal page does not say whether shot or resource costs are accounted for; how the guidance on when mitigation helps was validated was not seen.
Citable points: the volumetric benchmarking method and Qermit; median and worst-case performance are reported.
Relation to this project: contrast.

13. Giurgica-Tiron et al. 2020
Category: QEM methods
Reading depth: abstract and relevant passages
Open issues, stated by the authors: folding may fail to amplify systematic and coherent errors (inverse gates cancel them); it is not suitable for scaling state preparation and measurement noise; part of the derivation holds only for depolarizing noise and odd scale factors; extrapolated values can exceed physical bounds.
Citable points: the original wording of the limitations above; the definition of unitary folding.
Relation to this project: support (original source of the P1 blind spot).

14. Czarnik et al. 2021
Category: QEM methods
Reading depth: abstract
Open issues: the abstract does not say when Clifford training data fail to represent a non-Clifford target; the main demonstration is a single ground-state energy problem.
Citable points: the method of near-Clifford training circuits with a linear fit; an order-of-magnitude error reduction on 16-qubit hardware (hardware evidence from others).
Relation to this project: support (P2).

15. Wallman and Emerson 2016
Category: QEM methods
Reading depth: abstract and relevant passages
Open issues, stated by the authors: Theorem 1 requires the noise on easy gates to be gate independent; for general noise, approximate tailoring is only "expected", and a full proof is left open; the additional error bound for gate-dependent errors is not tight.
Citable points: under the theorem conditions, randomized compiling tailors noise into stochastic Pauli errors.
Relation to this project: support (principle of P3).

16. Hashim et al. 2021
Category: hardware experiments
Reading depth: abstract
Open issues: the abstract states no limitations; the demonstration covers only a four-qubit QFT and random circuits.
Citable points: randomized compiling improves performance on superconducting hardware; cycle-benchmarking error rates predict algorithm performance (hardware evidence from others).
Relation to this project: support.

17. Bonet-Monroig et al. 2018
Category: QEM methods
Reading depth: abstract
Open issues: demonstrated only in H2 simulation; the abstract does not address errors that preserve the symmetry (this is what this project derives, not what the paper states).
Citable points: mitigation by measuring conserved symmetries, including a zero-cost post-processing version; up to an order-of-magnitude error reduction on the H2 dissociation curve (simulation).
Relation to this project: support (P5).

18. Proctor et al. 2022, Scalable randomized benchmarking using mirror circuits
Category: benchmarking and characterization
Reading depth: abstract
Open issues: the benchmarked gates are Clifford; what is measured is the layer error rate, not the differential bias of a specific pair of circuits.
Citable points: mirror circuits can estimate multi-qubit layer error and detect crosstalk; simulations to 225 qubits and hardware to 16 qubits.
Relation to this project: support (implementation of P1 and P2).

19. Maciejewski et al. 2021
Category: readout
Reading depth: abstract
Open issues, stated by the authors: only marginal distributions are corrected; residual error is only bounded; correlations are assumed not to be too nonlocal; the QAOA results are numerical only.
Citable points: k-local readout crosstalk is characterized with O(k 2^k log N) circuits; measured correlations do not follow the physical layout (IBM 15 qubits, Rigetti 23 qubits).
Relation to this project: support (E5 and the motivation for the Part 4 hardware experiment).

20. Sarovar et al. 2020
Category: benchmarking and characterization
Reading depth: abstract
Open issues: the abstract covers only detection and localization of crosstalk, not its effect on decisions, the cost of detection, or a budget.
Citable points: a rigorous operational definition of crosstalk; detection through conditional dependences in observed probabilities.
Relation to this project: support and contrast (E3 probe).

## Closely related papers not included

Tamer 2010, close to Imbens and Manski 2004. Both supply identification-set language, and Tamer is a review; this project applies the theta = f(P, A) form of Imbens and Manski directly.

Takagi, Tajima and Gu 2023, close to Takagi et al. 2022. The same group's series of lower bounds; one representative is enough for the examiner question, and Quek et al. add a different angle.

Tsubouchi et al. 2023, close to Takagi 2022 and Quek 2024. Takagi and Quek suffice for the limits question, while the Certified Operating Windows paper (entry 8) bears more directly on this project through certification and the undetectable residual bias of P5.

Scavino 2026, Finite-shot operating windows for PEC and CDR (arXiv 2606.21686), close to Czarnik 2021 and entries 8 and 9. It can support the P2 failure condition (affine noise response), but it belongs to the same author series as entries 8 and 9 and would be merged with them when counting.

Koster and Mauerer 2026, Claim against Measurement (arXiv 2605.29872), close to entry 10. It is a review of evaluation methodology, not a diagnostic; it can be cited as supporting evidence in the pain-point analysis.

Temme et al. 2017, close to Giurgica-Tiron 2020. Temme is the original source of ZNE, but the P1 blind spot (coherent error is not amplified by folding) is stated in Giurgica-Tiron.

Lowe 2021 and Strikis 2021, close to Czarnik 2021. Both are variants of the Clifford-training approach; the method source and failure conditions of P2 follow the original CDR paper.

Kueng 2016 and Sanders 2016, close to Wallman and Emerson 2016 and Hashim 2021. The theory of coherent error and average metrics matters, but this inventory focuses on probe methods; both papers are used again in the E2 derivation.

van den Berg 2022 (TREX) and Chen 2019, close to Maciejewski 2021. TREX is model-free mitigation, not detection; Maciejewski gives the more complete direct evidence for E5 (correlated readout).

Kaufmann 2016, Garivier and Kaufmann 2016, Chen 2000 (OCBA). Budget allocation is an optional element and is reviewed together with the Proposition 2 derivation.

Rosenbaum 1987 and VanderWeele and Ding 2017, close to Lipsitch 2010. They concern a reporting format (the minimum bias needed to flip a decision), not the core of the pain-point analysis.

McArdle 2019 and Sagastizabal 2019, close to Bonet-Monroig 2018. Bonet-Monroig represents the symmetry-verification method.

Erhard 2019 and Gambetta 2012, close to Proctor 2022 and Sarovar 2020. They are characterization protocols of the same kind; Gambetta 2012 is still a partial entry and is not eligible.

Kim 2023 (Nature) and Kandala 2019, close to Hashim 2021. Large-scale ZNE hardware evidence is background; the hardware part of this project covers readout only.
