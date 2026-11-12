# Lemma 1: observational equivalence implies decision blindness

Status: task 1a-2 complete. Analytic result; no simulation or hardware evidence is used.

## Statement

Let \(X\) contain every runtime observation available to a frozen decision or certification rule, including target and probe outputs. Consider two admissible states

\[
\vartheta_+=(P,e_+),
\qquad
\vartheta_-=(P,e_-),
\]

that induce the same probability law \(P\) for \(X\), but whose ideal decision gaps satisfy

\[
\Delta_+=f(P,e_+)>0,
\qquad
\Delta_-=f(P,e_-)\le 0.
\]

Let \(\phi(X)\in\{+,-\}\) be any possibly randomized rule, where \(+\) asserts a strict top-1 decision and \(-\) asserts that this decision is not certified. Define

\[
\operatorname{err}_+=\Pr_{\vartheta_+}(\phi=-),
\qquad
\operatorname{err}_-=\Pr_{\vartheta_-}(\phi=+).
\]

Then

\[
\operatorname{err}_+ + \operatorname{err}_- = 1.
\]

Consequently,

\[
\max\{\operatorname{err}_+,\operatorname{err}_-\}\ge \frac12.
\]

More generally, if a rule may return additional outputs such as `abstain`, and an error means any output other than the correct conclusion for the corresponding state, then

\[
\operatorname{err}_+ + \operatorname{err}_-\ge 1.
\]

This is this project's sign-decision consequence of the identification-region definition in `01_definitions.md`. The proof below is self-contained; no external two-point theorem is cited.

## Proof

First consider the binary rule. Because \(\vartheta_+\) and \(\vartheta_-\) induce the same law \(P\) for all observations available to \(\phi\), the probability of every event determined by \(X\) and the rule's private randomization is the same under the two states. In particular,

\[
\Pr_{\vartheta_+}(\phi=+)=\Pr_{\vartheta_-}(\phi=+).
\]

Therefore,

\[
\begin{aligned}
\operatorname{err}_+ + \operatorname{err}_-
&=\Pr_{\vartheta_+}(\phi=-)
  +\Pr_{\vartheta_-}(\phi=+)\\
&=1-\Pr_{\vartheta_+}(\phi=+)
  +\Pr_{\vartheta_-}(\phi=+)\\
&=1.
\end{aligned}
\]

At least one of two nonnegative numbers summing to one is at least \(1/2\), which gives the minimax-error statement.

Now allow an output space \(\mathcal A\) containing `abstain` or other actions. Let \(C_+\subseteq\mathcal A\) be the outputs counted as correct when \(\Delta_+>0\), and let \(C_-\subseteq\mathcal A\) be the outputs counted as correct when \(\Delta_-\le0\). A rule cannot correctly assert both incompatible conclusions, so assume \(C_+\cap C_-=\varnothing\). Under the common observation law,

\[
\begin{aligned}
\operatorname{err}_+ + \operatorname{err}_-
&=\bigl[1-P(\phi\in C_+)\bigr]
  +\bigl[1-P(\phi\in C_-)\bigr]\\
&=2-P(\phi\in C_+)-P(\phi\in C_-)\\
&\ge1,
\end{aligned}
\]

because the two correct-output events are disjoint. This proves the general form. \(\square\)

## Corollary: target-only confidence intervals cannot resolve an unidentified bias

Suppose a target-only procedure observes an estimator whose sampling law depends on the noisy gap

\[
g=\Delta+\beta(e),
\]

and on any additional nuisance quantities included in its target-data distribution. Assume the allowed noise class contains two admissible decompositions \((\Delta_+,e_+)\) and \((\Delta_-,e_-)\) such that

\[
\Delta_+>0,
\qquad
\Delta_-\le0,
\]

while the complete target-data distributions are identical. A sufficient special case is that both decompositions have the same \(g\) and the same remaining sampling-law nuisance quantities.

Then every certificate computed only from target data obeys Lemma 1. In particular, a confidence interval that controls only the sampling error around \(g\) cannot determine whether the ideal gap is positive. Making the target-only interval arbitrarily narrow does not separate \(\Delta\) from \(\beta(e)\) when their observationally equivalent decompositions have different decision signs.

A bias being numerically large is not, by itself, sufficient for this corollary. The required condition is that the allowed model class contains sign-disagreeing states with the same complete distribution of the observations available to the certificate.

This project's corollary.

## Conditions under which the result holds

1. **Admissibility.** Both states satisfy the frozen model class, target definition, probe design, and decision convention.
2. **Common observable law.** The states induce exactly the same distribution for every observation available to the rule, not merely the same mean.
3. **Sign disagreement.** One ideal gap is strictly positive and the other is non-positive.
4. **Information restriction.** The rule uses no side information that distinguishes the two states, including no ideal target value.
5. **Common rule.** The same measurable, possibly randomized rule is applied under both states; its private randomization is independent of the unknown state.
6. **Loss convention.** For a binary rule, choosing the wrong sign is an error. For a rule with abstention, the inequality \(\ge1\) uses a loss that counts failure to return the correct conclusion as an error.
7. **Well-defined gap.** Conditional on \((P,e)\), \(\Delta=f(P,e)\) is uniquely determined, as required by `01_definitions.md`.

## Cases where it does not apply

- **Different observable laws.** If the two states induce different distributions, the exact equality argument does not apply. Their finite-shot distinguishability belongs to task 1a-3.
- **Same decision sign.** Nonidentification of the numerical gap does not imply decision blindness when every feasible gap has the same sign.
- **Informative probes or side information.** If additional allowed observations distinguish the states, they must be included in \(X\); the premise may then fail.
- **Free abstention.** If abstention is allowed and is not counted as an error under either state, an always-abstain rule has zero false decisions. Lemma 1 then cannot lower-bound the sum of errors without a coverage, decisiveness, or abstention-cost requirement.
- **Bias without observational equivalence.** A large allowed bias alone does not prove blindness if it also produces a detectable change in the available data distribution.
- **Undefined conditional recovery.** If \((P,e)\) does not uniquely determine \(\Delta\), the state space and identification region must first be enlarged as described in `01_definitions.md`.

