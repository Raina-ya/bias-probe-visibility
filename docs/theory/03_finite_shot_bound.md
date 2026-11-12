# Finite-shot lower bound

Status: task 1a-3 complete. Analytic result; no noisy simulation or hardware evidence is used.

## Setup

Let \(Q_+\) and \(Q_-\) be the one-shot distributions of every observable returned by a frozen target-and-probe design under two admissible states whose ideal gaps satisfy

\[
\Delta_+>0,
\qquad
\Delta_-\le0.
\]

Assume first that \(N\) shots are independent and identically distributed, so the complete data laws are \(Q_+^{\otimes N}\) and \(Q_-^{\otimes N}\). Define total variation by

\[
\operatorname{TV}(P,Q)=\sup_A |P(A)-Q(A)|
=\frac12\int|p-q|\,d\mu,
\]

where \(\mu\) dominates both distributions.

## Two-point error bound

For any possibly randomized binary rule \(\phi\in\{+,-\}\), define

\[
\operatorname{err}_+=Q_+^{\otimes N}(\phi=-),
\qquad
\operatorname{err}_-=Q_-^{\otimes N}(\phi=+).
\]

Then

\[
\operatorname{err}_+ + \operatorname{err}_-
\ge
1-\operatorname{TV}(Q_+^{\otimes N},Q_-^{\otimes N}).
\tag{1}
\]

### Proof

Let \(A=\{\phi=+\}\), including the rule's private randomization in the sample space. Then

\[
\begin{aligned}
\operatorname{err}_+ + \operatorname{err}_-
&=Q_+^{\otimes N}(A^c)+Q_-^{\otimes N}(A)\\
&=1-\bigl[Q_+^{\otimes N}(A)-Q_-^{\otimes N}(A)\bigr]\\
&\ge1-\operatorname{TV}(Q_+^{\otimes N},Q_-^{\otimes N}).
\end{aligned}
\]

This proof is self-contained. When \(Q_+=Q_-\), the total variation is zero and (1) reduces to Lemma 1.

## Hellinger-affinity shot bound

Define the one-shot Hellinger affinity

\[
\rho(Q_+,Q_-)=\int\sqrt{q_+q_-}\,d\mu
\]

and squared Hellinger distance in the convention

\[
H^2(Q_+,Q_-)=1-\rho(Q_+,Q_-).
\]

Independence gives the exact product identity

\[
\rho(Q_+^{\otimes N},Q_-^{\otimes N})=\rho(Q_+,Q_-)^N.
\tag{2}
\]

To connect affinity to total variation, write

\[
|p-q|=|\sqrt p-\sqrt q|\,(\sqrt p+\sqrt q)
\]

and apply Cauchy--Schwarz. Because

\[
\int(\sqrt p-\sqrt q)^2d\mu=2(1-\rho),
\quad
\int(\sqrt p+\sqrt q)^2d\mu=2(1+\rho),
\]

we obtain

\[
\operatorname{TV}(P,Q)\le\sqrt{1-\rho(P,Q)^2}.
\tag{3}
\]

Combining (1)--(3), every binary rule satisfies

\[
\operatorname{err}_+ + \operatorname{err}_-
\ge
1-\sqrt{1-\rho(Q_+,Q_-)^{2N}}.
\tag{4}
\]

Suppose the required operating point demands both errors to be at most \(\varepsilon<1/2\). A necessary condition is

\[
1-\sqrt{1-\rho^{2N}}\le2\varepsilon,
\]

or equivalently

\[
\rho^{2N}\le4\varepsilon(1-\varepsilon).
\]

For \(0<\rho<1\), this yields the necessary shot bound

\[
N\ge
\frac{\log\!\left(4\varepsilon(1-\varepsilon)\right)}
     {2\log\rho}.
\tag{5}
\]

Both logarithms are negative, so the right-hand side is positive. Equation (5) is necessary, not sufficient: passing it does not guarantee that a particular test reaches the desired errors.

## Blind in principle versus blind within budget

- **Blind in principle.** If \(Q_+=Q_-\), then \(\rho=1\) and no finite or infinite number of repeated shots separates the two states. Equation (1) gives \(\operatorname{err}_++\operatorname{err}_-\ge1\).
- **Blind within budget.** If \(0<\rho<1\), the states are distinguishable with enough independent shots. For a frozen budget \(N_{\max}\), they are blind within budget at per-state error target \(\varepsilon\) whenever

\[
N_{\max}<
\frac{\log\!\left(4\varepsilon(1-\varepsilon)\right)}
     {2\log\rho}.
\]

This is a pairwise necessary-condition certificate of budget blindness. Uniform blindness over a composite alternative class follows if at least one sign-disagreeing admissible pair violates the shot requirement.

## Analytic example: two single-qubit readout channels

Evidence type: analytic.

Prepare \(|0\rangle\), measure it once, and let \(Y=1\) denote a readout flip. Under two candidate readout channels,

\[
Q_+=\operatorname{Bernoulli}(0.1),
\qquad
Q_-=\operatorname{Bernoulli}(0.2).
\]

Their one-shot affinity is

\[
\rho
=\sqrt{0.1\cdot0.2}+\sqrt{0.9\cdot0.8}
\approx0.9899495,
\]

so \(H^2\approx0.0100505\). If the two admissible states imply opposite decision signs and both testing errors must be at most \(\varepsilon=0.05\), (5) gives

\[
N\ge82.203\ldots,
\]

hence at least \(83\) independent probe shots are necessary. This does not claim that 83 shots suffice.

The example isolates statistical distinguishability. It does not establish that these two readout channels actually produce opposite decision signs for a particular target; that must be shown separately by the target model.

## Assumptions and limitations

1. The sign-disagreeing pair is admissible under the frozen model class.
2. The rule sees exactly the observations represented by \(Q_+^{\otimes N}\) and \(Q_-^{\otimes N}\).
3. Shots are independent and identically distributed. Drift, adaptation, and correlated shots require a joint-law analysis rather than the tensor-product identity (2).
4. The same fixed sample size \(N\) is used under both states. Sequential stopping requires a separate result.
5. The binary-error convention is the one in `02_lemma1.md`. Free abstention requires a coverage, decisiveness, or abstention-cost constraint.
6. The Hellinger convention is stated explicitly because alternative conventions differ by a factor of two.
7. The bound is pairwise and necessary. It may be conservative and does not construct an optimal test.
8. Probe circuits and target circuits must be charged to the same total budget when this bound is used in later allocation tasks.

