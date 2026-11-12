# Local identifiability versus global sign identification

Status: task 1a-4 complete. Both counterexamples are analytic; no simulation or hardware evidence is used.

## Definitions used in this comparison

Consider a smooth statistical model \(\{P_\theta:\theta\in\Theta\}\), a scalar decision gap \(g(\theta)\), Fisher information \(I(\theta)\), and row Jacobian \(G(\theta)=Dg(\theta)\).

At \(\theta_0\), define the **local Fisher null-space condition**

\[
G(\theta_0)h=0
\quad\text{for every }h\in\ker I(\theta_0).
\tag{L}
\]

For the population law \(P_{\theta_0}\), define the global identification region

\[
\mathcal I_g(P_{\theta_0})
=
\{g(\theta):P_\theta=P_{\theta_0}\}.
\tag{G}
\]

The decision is globally blind when this set contains both a positive and a non-positive value. It is globally sign-identified when the entire set lies on one side of zero.

Condition (L) abstracts the Fisher null-space condition appearing in Scavino Alfaro's current arXiv v2, Corollary D.4. It is not presented here as a statement about unknown noise parameters: Appendix D.1 calls \(\theta\) an ideal-landscape instance, and the text read does not specify that noise or channel parameters are components of \(\theta\).

## Proposition

The local condition (L) and global sign identification do not imply one another:

1. (L) can hold at \(\theta_0\) while \(\mathcal I_g(P_{\theta_0})\) contains both signs.
2. (L) can fail at \(\theta_0\) while \(\mathcal I_g(P_{\theta_0})\subset(0,\infty)\).

## Proof

Counterexample 1 below establishes item 1, and Counterexample 2 establishes item 2. Together they prove non-containment in both directions. \(\square\)

## Counterexample 1: locally identifiable but globally blind

Evidence type: analytic.

Let \(\theta\in\mathbb R\), observe one draw

\[
X\mid\theta\sim\mathcal N(\theta^2,1),
\]

and define the gap

\[
g(\theta)=\theta.
\]

The score is

\[
\partial_\theta\log p_\theta(X)=2\theta(X-\theta^2),
\]

so the one-shot Fisher information is

\[
I(\theta)=4\theta^2.
\]

Fix \(\theta_0=a>0\). Then \(I(a)>0\), hence

\[
\ker I(a)=\{0\}.
\]

Because \(G(a)=1\), condition (L) holds: the only Fisher-null direction is zero.

Globally, however,

\[
P_a=P_{-a}
\]

because both distributions have mean \(a^2\), while

\[
g(a)=a>0,
\qquad
g(-a)=-a<0.
\]

Indeed, equality of the normal laws implies \(\theta^2=a^2\), so

\[
\mathcal I_g(P_a)=\{-a,a\}.
\]

The model is locally identifiable at \(a\) but globally blind in sign. The obstruction is a distant symmetry that local Fisher information cannot see.

## Counterexample 2: not locally identifiable but globally not blind

Evidence type: analytic.

Fix a known constant \(m>0\). Let

\[
\theta=(u,v)\in\mathbb R\times(-1/2,1/2),
\qquad
X\mid(u,v)\sim\mathcal N(u,1),
\]

and define

\[
g_m(u,v)=m(1+v).
\]

The observation law does not depend on \(v\), so

\[
I(u,v)=
\begin{pmatrix}
1&0\\
0&0
\end{pmatrix},
\qquad
\ker I(u,v)=\operatorname{span}\{(0,1)^\top\}.
\]

The gap Jacobian is

\[
G_m(u,v)=(0,m).
\]

For the null direction \(h=(0,1)^\top\),

\[
G_mh=m\ne0,
\]

so condition (L) fails everywhere.

For a fixed observed law \(P_u=\mathcal N(u,1)\), every \(v\in(-1/2,1/2)\) is observationally equivalent. Nevertheless,

\[
\mathcal I_{g_m}(P_u)
=
(m/2,3m/2)
\subset(0,\infty).
\]

The numerical gap is not locally identifiable, but its sign is globally identified. An unobservable direction matters to the magnitude without threatening the decision.

## Small-margin limit

The non-containment is not removed merely by making the margin small.

In Counterexample 1, choose any \(a>0\) and let \(a\downarrow0\). At every nonzero \(a\), condition (L) holds while the globally equivalent point \(-a\) reverses the sign. The Fisher information \(4a^2\) becomes ill-conditioned as the margin shrinks, but it remains positive for every \(a>0\).

In Counterexample 2, let the known scale \(m\downarrow0\). Condition (L) continues to fail because \(G_m(0,1)^\top=m\ne0\) for every \(m>0\), while the global region \((m/2,3m/2)\) remains strictly positive. Thus a locally unidentified magnitude can remain decision-safe at arbitrarily small positive margins.

The two notions become closely related only with additional assumptions that localize all relevant global alternatives to one regular neighborhood and control nonlinear remainders. A pointwise null-space condition alone does not exclude distant sign-reversing alternatives, and failure of that condition alone does not imply that an unidentified direction reaches the decision boundary.

## Relation to Scavino Alfaro (2026)

The frozen project notes refer to arXiv v1, Corollary C.1; the current arXiv v2 is retitled *Accuracy, Decision Risk, and Sampling Cost in Quantum Error Mitigation* and places the corresponding null-space condition in Corollary D.4.

Corollary D.4 fixes an allocation, defines the Fisher information \(I\), the gap Jacobian \(G\), and assumes \(Gh=0\) for every \(h\in\ker I\) before deriving a local quadratic tangent benchmark. Appendix D.3 further states that annihilating \(\ker I\) at one point is insufficient without regular coordinates and uniform/localization conditions. Appendix D.1 describes \(\theta\) as an ideal-landscape instance indexing primitive shot laws. Neither the v1 passages recorded in `reading_notes_key_sources.md`, section 4.6, nor the checked v2 passages state that noise or channel parameters are components of \(\theta\).

Therefore, the proposition above is a comparison with a condition **of the same mathematical kind**, not a claim that Scavino's result is a local version of this project's channel-level noise identification region.

## Related-work paragraph

Scavino Alfaro formulates a local Fisher condition \(Gh=0\) for every \(h\in\ker I\) and uses it in a quadratic tangent benchmark for decision-gap crossings (Scavino Alfaro 2026, arXiv:2607.02888v2, Corollary D.4). The same appendix warns that annihilating the Fisher null space at one point is insufficient without an appropriate regular parameterization and uniform localization control (Scavino Alfaro 2026, arXiv:2607.02888v2, Appendix D.3). Its shot-level model describes \(\theta\) as an ideal-landscape instance under fixed primitive measurements and allocation (Scavino Alfaro 2026, arXiv:2607.02888v2, Appendix D.1). In the passages checked for this project, whether \(\theta\) contains noise or channel parameters is not stated (`docs/reading_notes_key_sources.md`, section 4.6). This project instead defines a channel-level global sign region over admissible noise models and proves by analytic counterexamples that its sign criterion and the abstract Fisher null-space condition do not imply one another (`docs/theory/04_local_vs_global.md`).

## Assumptions and limits

1. These are statistical counterexamples, not physical quantum-noise models.
2. The comparison uses the scalar-gap form; vector gaps require applying the sign boundary coordinatewise or specifying another decision region.
3. Fisher information is a local object, whereas \(\mathcal I_g(P)\) uses exact global equality of population laws.
4. Counterexample 1 uses a global symmetry; restricting the parameter space to one branch would remove that global blindness.
5. Counterexample 2 relies on a known sign-preserving parameter restriction; enlarging the allowed range of \(v\) could make the model globally blind.
6. The source comparison is version-specific: Corollary C.1 in the frozen v1 notes corresponds in mathematical role, but not numbering or surrounding assumptions, to Corollary D.4 in arXiv v2.

