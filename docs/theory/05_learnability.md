# Learnability criterion: conditional connection

Status: task 1a-5 complete; the project owner approved the stated assumptions and conclusion on 2026-11-11.

## Conclusion

**Can be connected conditionally.** Chen et al.'s unlearnability definition is a special case of population-level observational equivalence and therefore fits this project's identification-region framework. However, its cycle/cut-space theorem is not currently applicable to the project's non-Clifford target family without an additional invariance derivation.

## Source meaning of unlearnable

Chen et al. define a function of noise models as unlearnable if two noise models are indistinguishable in all experiments allowed by their model but give different values of the function (Chen et al. 2023, Definition 1). Their short main-text description is "indistinguishable by any quantum experiment," within the assumptions stated in Appendix B.1.

The assumptions are perfect single-qubit unitaries, multi-qubit Clifford gates with gate-dependent Pauli noise, fixed Pauli SPAM channels, and strictly positive Pauli fidelities and error rates (Chen et al. 2023, Appendix B.1, Assumptions 1--4).

## Identification-region form

Let ℓ be the vector of log Pauli fidelities. Under the source assumptions, decompose

\[
\ell=z+u,
\qquad
z\in Z(G),\quad u\in U(G),
\]

where (Z(G)) and (U(G)) are the pattern-transfer graph's cycle and cut spaces. Chen et al.'s Theorem 2 identifies learnable linear information with (Z(G)) and unlearnable directions with (U(G)).

For fixed learnable component (z), define the physically admissible gauge fiber

\[
U_{\mathrm{phys}}(z)
=
\{u\in U(G):z+u\text{ is a physical noise model satisfying Assumptions 1--4}\}.
\]

If the ideal decision gap under that noise model is

\[
g(\ell)=\Delta+\beta(\ell),
\]

then this project's identification region becomes

\[
\mathcal I_g(z)
=
\{\Delta+\beta(z+u):u\in U_{\mathrm{phys}}(z)\}.
\tag{1}
\]

Equation (1) is this project's derivation, not a result stated by Chen et al.

## Criterion

Within Chen et al.'s model, the decision is blind in principle whenever

\[
\inf_{u\in U_{\mathrm{phys}}(z)}[\Delta+\beta(z+u)]\le0
<
\sup_{u\in U_{\mathrm{phys}}(z)}[\Delta+\beta(z+u)].
\tag{2}
\]

For a differentiable bias, the local sensitivity condition

\[
\Pi_{U(G)}\nabla_\ell\beta\ne0
\tag{3}
\]

shows that the bias varies along an unlearnable direction. Condition (3) is not sufficient for (2): physical constraints may limit the cut displacement before the gap reaches zero.

For a linear bias β(ℓ)=b^⊤ℓ, (3) reduces to Π_U b≠0, while (2) remains the exact global sign-crossing criterion.

## Applicability to the frozen project

The frozen target circuits include non-Clifford parameterized operations. The source theorem concerns Pauli noise attached to a Clifford gate set and does not establish the same gauge fiber for arbitrary non-Clifford noisy gates or coherent errors.

Consequently:

- the abstract mapping from unlearnability to an identification region is supported;
- the statement "nonzero cut projection implies every project probe is blind" is not supported;
- a physical blindness class can be claimed only after proving that Chen's gauge-related models preserve the full target-and-probe distribution used here and can move the decision gap across zero.

Until that proof exists, section 3.2 of the research plan remains a hypothesis rather than an established criterion.

## Assumptions and failure cases

1. All operations relevant to the equivalence must fall inside the source's experiment class.
2. The noise must have the source's gate-dependent Pauli and SPAM structure.
3. Gauge-displaced models must remain physical and inside the prespecified model class.
4. The target decision gap must be a well-defined function of the noise model.
5. A cut-sensitive magnitude need not be sign-sensitive; the admissible fiber must cross zero.
6. Additional probes outside the assumed gate set may break the observational equivalence.
7. Non-Clifford, coherent, leakage, drift, or context-dependent noise is outside the theorem unless separately reduced to the assumed model.
