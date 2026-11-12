# Proposition 2: when is a probe worth its budget?

Status: task 1c-2 complete. This is an analytic result; no simulation or hardware evidence is used.

## Scope and decision policy

Fix a total shot budget \(N\). A fraction \(f\in[0,1)\) is assigned to a probe and the remainder to the target decision:

\[
n_P=fN,
\qquad
n_T=(1-f)N.
\tag{1}
\]

The policy studied here is:

1. run the probe and target under the fixed allocation;
2. if the probe alarms, return **unresolved**;
3. otherwise, return the target decision.

This is the policy used by the bias-aware certificate in 07_certificate.md. The proposition does not cover a probe that directly corrects the target estimate or chooses a replacement method after alarming.

Let

- \(W_f\) be the event that the target decision based on \(n_T\) shots is wrong;
- \(A_f\) be the event that the probe alarms;
- \(q_f=\Pr(W_f)\) be the target error if the alarm were ignored;
- \(u_f=\Pr(A_f)\) be the unresolved probability;
- \(d_f=\Pr(A_f\cap W_f)\) be the probability that the probe intercepts a decision that would otherwise be wrong.

The all-target baseline has \(f=0\), no alarm, and error

\[
R_0=q_0.
\tag{2}
\]

Under the probe policy, the wrong-decision probability is

\[
R_f=\Pr(W_f\cap A_f^c)=q_f-d_f.
\tag{3}
\]

Equation (3) is exact. It does not require Gaussian observations or independence between target and probe data.

## Proposition 2: exact fixed-budget condition

### Proposition

Under the policy above, allocating fraction \(f\) to the probe lowers the wrong-decision probability if and only if

\[
\boxed{
d_f>q_f-q_0.
}
\tag{4}
\]

Equivalently, when \(q_f>0\), define the error-conditional interception probability

\[
\eta_f=\Pr(A_f\mid W_f).
\tag{5}
\]

Then the probe is worthwhile for wrong-decision risk if and only if

\[
\boxed{
\eta_f>1-\frac{q_0}{q_f}.
}
\tag{6}
\]

### Proof

From (3),

\[
R_f<R_0
\quad\Longleftrightarrow\quad
q_f-d_f<q_0
\quad\Longleftrightarrow\quad
d_f>q_f-q_0.
\]

Because \(d_f=\eta_f q_f\), division by \(q_f>0\) gives (6). ∎

### Interpretation

The right side of (4) is the **allocation cost**: the additional target errors caused by reducing the target budget from \(N\) to \((1-f)N\). The left side is the **useful detection benefit**: alarms that occur specifically on runs that would otherwise be wrong.

Unconditional alarm power is not enough. A probe can alarm frequently on correct runs, making \(u_f\) large while \(d_f\) remains small. Proposition 2 therefore uses error-conditional interception rather than raw alarm probability.

## Corollary: Gaussian independent-probe approximation

Assume the target gap estimator is approximately normal with population noisy gap

\[
m=\Delta+\beta
\]

and per-shot standard deviation \(\sigma\). Then

\[
q_f
=
\Phi\!\left(
-\frac{m\sqrt{(1-f)N}}{\sigma}
\right).
\tag{7}
\]

Write

\[
s=\frac{m\sqrt N}{\sigma}.
\]

Then

\[
q_0=\Phi(-s),
\qquad
q_f=\Phi\!\left(-s\sqrt{1-f}\right).
\tag{8}
\]

For the probe, assume a standardized statistic with harmful-alternative mean

\[
a\sqrt f,
\qquad
a=\frac{\kappa|\beta|\sqrt N}{\sigma_T},
\tag{9}
\]

and a one-sided level-\(\alpha\) threshold \(z_{1-\alpha}\). Its alarm probability is

\[
\pi_f
=
\Phi\!\left(
a\sqrt f-z_{1-\alpha}
\right).
\tag{10}
\]

If \(A_f\) and \(W_f\) are independent under this approximation, then

\[
d_f=\pi_f q_f,
\qquad
\eta_f=\pi_f.
\]

For \(m>0\), reducing target shots weakly increases target error, so \(q_f\ge q_0\). Proposition 2 becomes

\[
\boxed{
\Phi\!\left(
\frac{\kappa|\beta|\sqrt{fN}}{\sigma_T}
-z_{1-\alpha}
\right)
>
1-
\frac{
\Phi\!\left(-m\sqrt N/\sigma\right)
}{
\Phi\!\left(-m\sqrt{(1-f)N}/\sigma\right)
}.
}
\tag{11}
\]

The minimum worthwhile fraction in this model is

\[
f^\star
=
\inf\left\{
f\in(0,1):
\text{inequality (11) holds}
\right\}.
\tag{12}
\]

If the set in (12) is empty, no positive probe allocation lowers wrong-decision risk under the stated model and budget.

Equation (11) is the planned sensitivity-versus-shot-cost condition. It is an approximation, not the general proposition. In particular, P1b, GVS, and P5 can reuse target counts, so their alarm and target-error events need not be independent; for them, (4) is the relevant condition.

## Unresolved decisions are a separate endpoint

Proposition 2 lowers wrong-decision probability partly by abstaining. It does not claim to lower the unresolved rate:

\[
U_f=u_f.
\tag{13}
\]

If an unresolved result has loss \(\lambda\in[0,1]\), define

\[
\mathcal L_f=R_f+\lambda U_f
=q_f-d_f+\lambda u_f.
\tag{14}
\]

Then the probe lowers this scalar loss if and only if

\[
\boxed{
d_f>q_f-q_0+\lambda u_f.
}
\tag{15}
\]

Under the independence approximation, \(d_f=\pi_fq_f\) and \(u_f=\pi_f\). If \(q_f>\lambda\), equation (15) becomes

\[
\boxed{
\pi_f>
\frac{q_f-q_0}{q_f-\lambda}.
}
\tag{16}
\]

If \(m>0\), \(q_f\ge q_0\), and \(q_f\le\lambda\), no alarm probability can satisfy (15): abstention is valued as at least as costly as the target error it replaces.

The project reports false-certification and unresolved rates separately, so its primary use of Proposition 2 is the two-dimensional pair \((R_f,U_f)\), not a post hoc choice of \(\lambda\).

## Sign-flipped and common-mode cases

### Sign-flipped observed gap

If \(m=\Delta+\beta<0\) while \(\Delta>0\), then

\[
q_f=\Phi\!\left(
\frac{|m|\sqrt{(1-f)N}}{\sigma}
\right)>\frac12.
\]

Reducing target shots moves this error toward \(1/2\), so it can produce \(q_f<q_0\) even without a useful probe. That mechanical reduction is not evidence of visibility: it only makes the wrong noisy decision less certain. A useful probe must still provide an alarm or certificate that resolves the bias mechanism. Equation (4) remains correct, but the term \(q_f-q_0\) is then negative and should not be interpreted as a detection benefit.

### Common-mode bias

For common-mode error, the decision contrast has \(\beta=0\). A correctly calibrated differential-bias probe has only its false-alarm probability, while target shots are removed. When \(m=\Delta>0\), \(q_f\ge q_0\) and \(d_f\) contains no mechanism-specific advantage. If unresolved outcomes have zero loss, even random alarms can mechanically lower the recorded wrong-decision rate by declining to decide; they simultaneously increase \(U_f\). Thus E0 cannot supply a strict Pareto improvement in both wrong-decision and unresolved rates, and any claimed scalar improvement must use the prespecified loss in (14), not raw error alone. This is the negative-control role of E0.

## Comparison with Proposition 1 of adaptive-qem-benchmark

The requested file paper/main_v2.tex is not present in the local previous repository. The current read-only source is paper/main.tex, Section “Estimator Quality Versus Decision Reliability”; it was not modified.

Proposition 1 there compares a raw gap mean \(\Delta_{\rm r}\) with a mitigated gap mean \(\Delta_{\rm m}\), when mitigation multiplies variance by \(\gamma\). Under its normal approximation, mitigation improves the decision exactly when

\[
\Delta_{\rm m}>\sqrt\gamma\,\Delta_{\rm r}.
\tag{17}
\]

The comparison with Proposition 2 is:

| Feature | Previous Proposition 1 | This Proposition 2 |
|---|---|---|
| Action | replace one estimator with another | reserve fraction \(f\) for a diagnostic and abstain on alarm |
| Cost | mitigation variance multiplier \(\gamma\) | target budget falls to \((1-f)N\) |
| Benefit | changed mean gap \(\Delta_{\rm m}\) | intercepted wrong decisions \(d_f\) |
| Exact condition | \(\Delta_{\rm m}>\sqrt\gamma\,\Delta_{\rm r}\) | \(d_f>q_f-q_0\) |
| Budget dependence | \(\sqrt N\) cancels in the stated model | both detection and target cost depend on \(fN\), so the preference can change with \(N\) |
| Failure mode | debiasing too small for its variance cost | probe catches fewer errors than the target-shot cost it creates |

Both propositions express the same principle: an auxiliary procedure is worthwhile only when its decision-relevant benefit exceeds its fixed-budget variance or allocation cost. Proposition 2 differs because the benefit is selective abstention rather than a new point estimator.

## Conditions under which Proposition 2 holds

1. Total budget \(N\) and fraction \(f\) include every target and probe shot.
2. The action after an alarm is unresolved; correction or method switching requires a different proposition.
3. The target decision rule and alarm rule are fixed before evaluation.
4. Wrong decisions and unresolved outcomes are recorded separately unless a prespecified \(\lambda\) defines their relative loss.
5. Equation (4) is general, but evaluating it requires the joint law of \((A_f,W_f)\).
6. Equations (7)--(12) additionally require the stated Gaussian approximation, constant per-shot variances, fixed \(m\), and the standardized probe model.
7. Replacing \(d_f\) by \(\pi_fq_f\) additionally requires independence between alarm and target-error events.
8. The sensitivity \(\kappa\), noise-to-probe link, threshold, and variance \(\sigma_T\) must be frozen or estimated using a separately valid procedure.
9. The allocation must leave enough target and probe shots for the approximations and rules to be defined.
10. Drift, shared shots, adaptive stopping, and multiple probes must be included in the joint law rather than silently treated as independent.

## Failure conditions

- **Blind probe:** if the harmful direction leaves the probe statistic invariant, \(d_f\) cannot exceed the allocation cost uniformly.
- **Low power:** a visible population effect may still yield too small \(d_f\) at budget \(fN\).
- **Wrong alarms:** high \(u_f\) with low \(d_f\) increases unresolved outcomes without intercepting enough errors.
- **Too much probe budget:** as \(f\to1\), the target decision loses resolution; the Gaussian \(q_f\) approaches \(1/2\).
- **Model mismatch:** the approximate power in (10) is invalid if \(\kappa\), \(\sigma_T\), or the alternative distribution is wrong.
- **Shared-data dependence:** using unconditional power in place of \(d_f/q_f\) can reverse the conclusion.

## Budget-allocation literature positioning

The allocation terminology is supported only by the verified entries already in docs/literature/library.csv:

- Kaufmann, Cappé, and Garivier (2016) distinguish fixed-budget and fixed-confidence best-arm identification and study their sample complexity.
- Garivier and Kaufmann (2016) study fixed-confidence best-arm identification and allocation proportions.
- Chen, Lin, Yücesan, and Chick (2000) is the verified OCBA background source for simulation-budget allocation.

These works motivate the allocation language. Equation (4), the interception interpretation, and the specialization to probe-versus-target shots are this project's derivation; they are not attributed to those sources.

## Conclusion

At a fixed total budget, a probe is worth fraction \(f\) precisely when the wrong decisions it intercepts exceed the extra target errors caused by removing \(fN\) target shots. Under the independent Gaussian approximation this gives inequality (11); in the actual project, the exact joint condition (4) is primary because several zero-extra-shot probes share data with the target.
