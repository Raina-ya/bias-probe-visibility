# Chen et al. (2023): Codex reading-note draft

Status: source-checked and approved by the project owner on 2026-11-11.

## Bibliographic record

Senrui Chen, Yunchao Liu, Matthew Otten, Alireza Seif, Bill Fefferman, and Liang Jiang, "The learnability of Pauli noise," *Nature Communications* 14, 52 (2023). DOI: 10.1038/s41467-022-35759-4. The theorem text and assumptions below were checked against the full arXiv HTML and the published open-access article.

## Exact scope of the model

Appendix B.1 states four assumptions:

1. all single-qubit unitary operations are perfect;
2. the available multi-qubit gates are Clifford gates with gate-dependent, (n)-qubit Pauli noise;
3. arbitrary preparation and measurement are available up to fixed Pauli SPAM channels;
4. all relevant Pauli fidelities and Pauli error rates are strictly positive.

The fourth assumption places the model in the interior needed for the physical gauge construction. The model may include (n)-qubit crosstalk, but it remains a Pauli-noise model attached to a Clifford gate set.

## Meaning of learnable and unlearnable

Definition 1 says a function of the noise model is learnable when differing function values imply distinguishable noise models. It calls a function unlearnable when there are indistinguishable models with different function values.

The main-text explanation is: "indistinguishable by any quantum experiment." In the paper, this quantifier is over experiments constructed within its assumed gate/SPAM model.

Thus unlearnability is population-level observational equivalence, not merely low finite-shot power.

## Cycle and cut spaces

The variables are logarithmic Pauli fidelities, one for each edge of the pattern transfer graph. The edge space decomposes orthogonally into cycle and cut spaces. Theorem 2 states that, under the paper's assumptions, the learnable linear functions equal the cycle space and the unlearnable directions equal the cut space.

The cut-space result is proved through gauge transformations that preserve every allowed experiment's output distribution while changing gate and SPAM parameters. Individual unlearnable Pauli fidelities can nevertheless have learnable products; therefore, "an unlearnable parameter occurs" is not enough to decide whether a particular bias functional is unlearnable.

## Conditional connection to this project

Let ℓ collect log Pauli fidelities and write the edge-space decomposition

\[
\ell=z+u,
\qquad z\in Z(G),\quad u\in U(G),
\]

where (Z(G)) is the cycle space and (U(G)) the cut space. Under Chen et al.'s assumptions, population observations identify learnable functions of (z) but do not point-identify (u).

For a decision gap

\[
g(\ell)=\Delta+\beta(\ell),
\]

the identification region along a fixed observable fiber is

\[
\mathcal I_g(z)
=
\{\Delta+\beta(z+u):u\in U_{\mathrm{phys}}(z)\},
\]

where (U_{\mathrm{phys}}(z)) contains only cut displacements that preserve the paper's physical assumptions.

For differentiable β, a nonzero cut-space component of its gradient,

\[
\Pi_{U(G)}\nabla_\ell\beta\ne0,
\]

means that the bias can change along an unlearnable local direction. It does **not** by itself prove decision blindness. Blindness additionally requires the physically admissible fiber to contain values on both sides of zero.

For linear β(ℓ)=b^⊤ℓ, the exact condition is

\[
\inf_{u\in U_{\mathrm{phys}}(z)}[\Delta+b^\top(z+u)]\le0
<
\sup_{u\in U_{\mathrm{phys}}(z)}[\Delta+b^\top(z+u)].
\]

## Why the project cannot yet claim the physical criterion

The project's target family includes non-Clifford parameterized circuits. Chen et al.'s theorem is not stated for arbitrary non-Clifford noisy gates or coherent noise. To apply the criterion, the project would have to show either:

1. every unknown target and probe operation fits the paper's Clifford-plus-Pauli model; or
2. the same gauge transformation leaves the project's complete target-and-probe distribution invariant while moving its decision gap across zero.

Neither derivation currently exists. Therefore the abstract identification connection is valid, but the proposed cut-space criterion is not yet a demonstrated physical class of blindness for the frozen target circuits.

## Project-owner confirmation

On 2026-11-11 the project owner approved: (1) the four theorem assumptions above; (2) the distinction between an unlearnable direction and a sign-crossing identification region; and (3) the conclusion that the result can be connected conditionally but is not established for the project's non-Clifford targets. No additional conclusion was supplied.
