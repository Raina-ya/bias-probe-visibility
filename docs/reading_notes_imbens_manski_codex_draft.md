# Imbens and Manski (2004): Codex reading-note draft

Status: reviewed and approved by the project owner on 2026-11-11. The source analysis was prepared by Codex; the project choices below were explicitly approved by the project owner.

## Bibliographic record

Guido W. Imbens and Charles F. Manski, "Confidence Intervals for Partially Identified Parameters," *Econometrica* 72(6), 1845--1857 (2004). DOI: 10.1111/j.1468-0262.2004.00555.x. Verified against the Wiley record and author-hosted PDF.

## Section 2: source structure

Section 2 uses an unknown observable distribution \(P\), an additional quantity \(A\) known only to belong to a specified set \(\mathcal A\), and a real target \(\theta=f(P,A)\). It defines the identification region as

\[
\{f(P,A'):A'\in\mathcal A\}.
\]

When extrema exist, the paper studies the interval \([f(P,A_L(P)),f(P,A_U(P))]\). This supports the project's structural substitution \(A=e\), \(\mathcal A=\mathcal E\), and \(\Delta=f(P,e)\), provided the project separately assumes that \(P\) and \(e\) uniquely determine \(\Delta\).

## Confidence-interval distinction

The paper distinguishes a CI covering the entire identification region from a generally narrower CI covering the true partially identified parameter. Lemma 1 observes that set coverage implies parameter coverage. The simplest parameter-covering interval is not uniformly valid as the identification-region width approaches zero; Sections 3--4 modify it under stated regularity assumptions.

Project consequence: the paper does not justify importing a pointwise or asymptotic CI without a separate coverage derivation.

## What the source does not establish

- It does not define blind in principle, blind within budget, or visible.
- It does not connect identification regions to a decision-gap sign.
- It does not study probes, probe costs, quantum noise, or adaptive-QEM.
- It takes \(\mathcal A\) as specified; it does not derive the project's joint target-and-probe \(P\) construction.
- It does not establish that \(\Delta=f(P,e)\) exists for a quantum-noise class.
- It refers to Manski (2003) for the broader partial-identification framework.

## Safe use in this project

The source can support the abstract form and range construction, the separation of identification uncertainty from endpoint sampling uncertainty, and the warning about non-uniform coverage near point identification.

The sign criterion, joint target-and-probe \(P\), fixed \(\mathcal E\), probe compatibility step, and finite-budget visibility criterion must be labelled as this project's definitions or derivations.

## Project-owner review

On 2026-11-11, the project owner approved:

1. \(\Delta=f(P,e)\), subject to explicit uniqueness/invertibility;
2. positive and non-positive feasible gaps as the blindness criterion;
3. zero as failure to certify a strict top-1 decision;
4. separate concepts for point identification and finite-budget visibility;
5. labelling the sign criterion, finite-budget definitions, joint-\(P\) construction, fixed \(\mathcal E\), and associated assumptions as this project's definitions or derivations.
