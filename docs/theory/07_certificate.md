# Bias-aware certificate with a probe-derived bound

Status: task 1c-1 complete. This is an analytic result; no simulation or hardware evidence is used.

## Setup

Let

\[
\mu=\Delta+\beta
\]

be the population gap observed through the noisy target circuit, where \(\Delta\) is the ideal decision gap and \(\beta\) is the differential bias. A strict top-1 decision is certified only when \(\Delta>0\).

Write \(D_T\) for the target data and \(D_P\) for the probe data. The target procedure returns a one-sided lower confidence bound \(L_T(D_T)\) for \(\mu\). The probe procedure returns an upper confidence bound \(B(D_P)\) for the harmful bias:

\[
\inf_{\theta\in\Theta}
\Pr_\theta\!\left\{\mu(\theta)\ge L_T(D_T)\right\}
\ge 1-\alpha_T,
\tag{1}
\]

\[
\inf_{\theta\in\Theta}
\Pr_\theta\!\left\{\beta(\theta)\le B(D_P)\right\}
\ge 1-\alpha_P.
\tag{2}
\]

Here \(\Theta\) is the complete prespecified class of target distributions, noise structures, and probe-transfer relations. Equation (2), not the mere observation of a probe statistic, is the substantive validity requirement.

An absolute bound \(|\beta|\le B\) is sufficient but stronger than necessary. For certifying \(\Delta>0\), only an upper bound on \(\beta\) is needed because positive bias is the harmful direction.

## Constructing \(B\) from probe data

One valid construction starts with a probe confidence set

\[
\mathcal C_P(D_P)\subseteq\mathcal E,
\qquad
\inf_{\theta\in\Theta}
\Pr_\theta\!\left\{e(\theta)\in\mathcal C_P(D_P)\right\}
\ge 1-\alpha_P.
\tag{3}
\]

Before data are observed, specify a transfer envelope \(b(e)\) satisfying

\[
\beta(\theta)\le b(e(\theta))
\quad\text{for every }\theta\in\Theta.
\tag{4}
\]

Then set

\[
B(D_P)=\sup_{e\in\mathcal C_P(D_P)} b(e).
\tag{5}
\]

Equations (3)--(5) imply (2). The envelope in (4) is where the visibility condition enters: the probe must constrain the same decision-relevant noise component as the target bias. If no validated finite envelope exists for a direction, that direction must retain its prior worst-case bound; it cannot be set to zero because the probe was quiet.

The confidence set, envelope, confidence allocation, and handling of an empty or unbounded set must all be frozen before noisy simulation.

### Initial executable envelope for this project

The v2 protocol intentionally implements only the readout case for which a
finite envelope can be checked exhaustively. For P4a/E4 and P4b/E4,E5 (and the
declared E6 paths built from those channels), simultaneous probe intervals
retain a finite set of compatible assignment channels. For normalized MaxCut
score vector (c) and channel (M_e), define

\[
v_e=c^T(M_e-I),\qquad
b_G(e)=\max_j v_{e,j}-\min_j v_{e,j}.
\]

The second expression is a worst-case upper bound on differential readout bias
over two arbitrary candidate input distributions. The implementation enumerates
every retained grid channel and every basis column, then uses (5). For all other
probe/structure cells, or when the compatible set is empty or enumeration
fails, the operational choice is (B(D_P)=+\infty) and the result is
unresolved. This conservative scope is necessary: the general theorem does not
create a transfer envelope where none has been proved.

## Certification rule

Define the bias-aware lower bound

\[
L_\Delta(D_T,D_P)=L_T(D_T)-B(D_P).
\tag{6}
\]

The rule is

\[
\boxed{\text{certify the designated winner only if }
L_T(D_T)>B(D_P).}
\tag{7}
\]

Otherwise the output is **unresolved**. Failure to certify is not evidence that the designated winner is wrong.

## Joint-coverage theorem

### Theorem 1

Suppose (1) and (2) hold uniformly over the same prespecified class \(\Theta\). Then

\[
\inf_{\theta\in\Theta}
\Pr_\theta\!\left\{
\Delta(\theta)\ge L_\Delta(D_T,D_P)
\right\}
\ge 1-\alpha_T-\alpha_P.
\tag{8}
\]

Consequently, the false-certification probability of rule (7) satisfies

\[
\sup_{\theta:\Delta(\theta)\le0}
\Pr_\theta\{\text{certify}\}
\le\alpha_T+\alpha_P.
\tag{9}
\]

No independence between \(D_T\) and \(D_P\) is required for this union-bound result.

### Proof

Let

\[
\mathcal A_T=\{\mu\ge L_T\},
\qquad
\mathcal A_P=\{\beta\le B\}.
\]

On \(\mathcal A_T\cap\mathcal A_P\),

\[
\Delta=\mu-\beta\ge L_T-B=L_\Delta.
\]

By the union bound,

\[
\Pr_\theta(\mathcal A_T\cap\mathcal A_P)
\ge 1-\Pr_\theta(\mathcal A_T^c)
       -\Pr_\theta(\mathcal A_P^c)
\ge 1-\alpha_T-\alpha_P.
\]

This proves (8). If the rule certifies, then \(L_\Delta>0\). For any state with \(\Delta\le0\), certification is impossible on the joint event in (8); therefore it can occur only on its complement, whose probability is at most \(\alpha_T+\alpha_P\). This proves (9). ∎

### Corollary: a single nominal level

For total false-certification level \(\alpha\), any prespecified split satisfying

\[
\alpha_T+\alpha_P\le\alpha
\]

gives an honest one-sided certificate at level \(1-\alpha\). The equal split is simple but is not asserted to be optimal.

## What “never certifies in a blind direction” can validly mean

Let the exact observable population law be \(P\), with noisy gap \(\mu(P)\). Define the population compatible noise fiber

\[
\mathcal E(P)=\{e\in\mathcal E:e\text{ is compatible with }P\}
\]

and its exact one-sided bias envelope

\[
B_\infty(P)=\sup_{e\in\mathcal E(P)}\beta(P,e).
\tag{10}
\]

### Proposition 2: population structural abstention

If the design is blind in principle at \(P\), then

\[
\mu(P)-B_\infty(P)\le0.
\tag{11}
\]

Hence the population version of rule (7) never certifies at a blind \(P\).

### Proof

Blindness means that \(\mathcal E(P)\) contains an \(e_-\) for which

\[
\Delta(P,e_-)=\mu(P)-\beta(P,e_-)\le0.
\]

Thus

\[
B_\infty(P)\ge\beta(P,e_-)\ge\mu(P),
\]

which gives (11). ∎

### Proposition 3: finite-sample retained-direction abstention

For a realized dataset, suppose the probe set \(\mathcal C_P(D_P)\) still contains a compatible \(e_-\) with \(\Delta(P,e_-)\le0\), and the target coverage event \(\mu\ge L_T\) holds. Then rule (7) does not certify.

### Proof

Because \(e_-\in\mathcal C_P\), equations (4)--(5) give

\[
B\ge\beta(P,e_-)\ge\mu\ge L_T.
\]

Therefore \(L_T>B\) is false. ∎

This is the precise finite-sample meaning used by the project: a blind direction that remains compatible forces abstention. A confidence procedure with positive error level cannot guarantee that sampling fluctuation never excludes the true blind state. Under Theorem 1, such a mistaken certification has probability at most \(\alpha_T+\alpha_P\). Literal probability-one abstention would require an almost-sure probe envelope and an almost-sure target lower bound, which generally reduces to a deterministic prior worst-case bound and may be uninformative.

The observational-equivalence argument gives the same limit from another direction: if a positive-gap and a non-positive-gap state induce exactly the same complete data law, any certificate fires with the same probability in both states. Uniform false-certification control at level \(\alpha\) therefore limits its certification probability at that population law to at most \(\alpha\).

## Analytic example: a bounded linear probe link

Evidence type: analytic.

Let target observations \(Y_1,\ldots,Y_{n_T}\in[-1,1]\) have mean

\[
\mathbb E[Y_i]=\mu=\Delta+\beta,
\]

and probe observations \(X_1,\ldots,X_{n_P}\in[-1,1]\) have mean \(\tau\). Suppose the prespecified physical model proves

\[
\beta\le b_\perp+c|\tau|,
\qquad b_\perp\ge0,\quad c\ge0.
\tag{12}
\]

The term \(b_\perp\) is the prior bound on the probe-blind component. It cannot be learned from \(X\).

Let

\[
\widehat\mu=\frac1{n_T}\sum_iY_i,
\qquad
\widehat\tau=\frac1{n_P}\sum_jX_j,
\]

\[
r_T=\sqrt{\frac{2\log(1/\alpha_T)}{n_T}},
\qquad
r_P=\sqrt{\frac{2\log(2/\alpha_P)}{n_P}}.
\]

Hoeffding's inequality for variables in \([-1,1]\) gives

\[
\Pr\{\mu\ge\widehat\mu-r_T\}\ge1-\alpha_T,
\qquad
\Pr\{|\tau-\widehat\tau|\le r_P\}\ge1-\alpha_P.
\]

Therefore

\[
L_T=\widehat\mu-r_T,
\qquad
B(D_P)=b_\perp+c\bigl(|\widehat\tau|+r_P\bigr)
\tag{13}
\]

satisfy Theorem 1, and the explicit rule is

\[
\widehat\mu-r_T
>
b_\perp+c\bigl(|\widehat\tau|+r_P\bigr).
\tag{14}
\]

As \(n_P\) grows, the visible contribution \(c|\tau|\) can be bounded more tightly. The blind contribution \(b_\perp\) does not shrink. If \(\tau=0\) and the population noisy gap obeys \(\mu\le b_\perp\), the identification region contains

\[
\Delta=\mu-b_\perp\le0,
\]

so the infinite-shot rule remains unresolved. This is structural abstention, not a power failure.

The example does not assert that equation (12) holds for every quantum probe. Each implemented probe needs its own analytic or validated transfer envelope; without one, the corresponding \(B\) is not justified.

## Differences from Armstrong and Kolesár (2020)

The following comparison uses the source wording recorded in section 3 of reading_notes_key_sources.md.

1. **Object and purpose.** Armstrong and Kolesár study “honest confidence intervals” for a scalar parameter under nonparametric restrictions. This project uses the same bias-aware form only as motivation for a one-sided quantum decision certificate.
2. **Treatment of bias.** Their critical value is based on the “1−α quantile of the folded normal distribution” and a worst-case bias over a function class whose smoothness bound is fixed in advance. Here \(B(D_P)\) is random because a separately calibrated probe confidence set narrows a prespecified noise class.
3. **Coverage target.** Their stated goal is to “cover the true parameter asymptotically at the nominal level uniformly.” This project instead requires finite-sample joint control of a target lower bound and a probe-derived bias bound over \(\Theta\).
4. **Proof obligation.** Their coverage theorem does not automatically apply after replacing a fixed worst-case bias with a random probe-derived bound. Equations (1)--(9) provide the additional coverage argument. The union-bound construction may be more conservative than a jointly optimized critical value.

Thus the interval form is borrowed, but coverage is not claimed to be inherited.

## Relation to Imbens and Manski (2004)

Imbens and Manski write a partially identified scalar as \(f(P,A)\), with \(A\) known only to lie in a fixed set, and take the range over admissible \(A\). In this project, \(A\) is the noise \(e\), and the lower population endpoint is

\[
\inf_{e\in\mathcal E(P)}\Delta(P,e)
=\mu(P)-B_\infty(P)
\]

when \(\mu(P)\) is common over the compatible fiber. The probe confidence set is a finite-sample outer set for that fiber. The substitution of quantum noise and the joint target/probe construction are this project's derivation, not a result stated by Imbens and Manski.

## Conditions required by the coverage proof

1. The state/noise class \(\Theta\) is fixed before data are observed.
2. The target lower bound (1) is uniformly valid over \(\Theta\).
3. The probe bias bound (2) is uniformly valid over the same \(\Theta\).
4. If (2) is constructed through (3)--(5), the probe confidence set has uniform coverage and the transfer envelope (4) is valid for every allowed target context.
5. The sign convention is fixed: \(\Delta>0\) certifies; \(\Delta\le0\) does not.
6. Target and probe rules, confidence allocation, selection, stopping, and multiplicity adjustments are frozen or included in their coverage guarantees.
7. Reusing shots is allowed only if the marginal guarantees remain valid; independence is not needed for the union bound.
8. Calibration-to-execution drift, preparation error, or model misspecification is either included in \(\Theta\) and \(b(e)\), or explicitly outside the certificate's scope.
9. Empty confidence sets are handled conservatively, for example by setting \(B=+\infty\) and returning unresolved.
10. Numerical optimization used to compute the supremum in (5) returns a certified upper bound, not an unchecked local optimum.

## Failure conditions and limitations

- A probe statistic correlated with bias is insufficient; equation (4) needs a uniform upper envelope.
- If a decision-relevant component is probe-blind, its prior worst-case contribution remains in \(B\).
- If the bound is so large that \(L_T\le B\), the correct output is unresolved.
- Misspecified transfer, unaccounted drift, post-selection, adaptive probe choice, or an underestimated numerical supremum can invalidate coverage.
- The theorem controls false certification, not the unresolved rate. Whether probe spending improves total decision performance is task 1c-2.
- This certificate covers only the modelled bias class. It is not evidence that unmodelled error is absent.

## Conclusion

The rule \(L_T>B(D_P)\) has joint coverage at least
\(1-\alpha_T-\alpha_P\) when the target and probe bounds are uniformly valid. It structurally abstains whenever the retained compatible set still contains a decision-flipping blind direction. Its scientific value therefore depends on proving a probe-to-bias envelope; probe activity alone is not a certificate.
