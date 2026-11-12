# Extension of Proposition 1: \(K\) candidates and estimated overhead

Status: task 1c-3 complete. The propositions below are analytic. No simulation or hardware result is reported.

Source note. The requested file <code>paper/main_v2.tex</code> is not present in the local copy of the previous repository. The read-only source used here is <code>paper/main.tex</code>, lines 194--217, which states the two-candidate condition

\[
\Delta_{\rm m}>\sqrt{\gamma}\,\Delta_{\rm r}.
\tag{1}
\]

## Setup

Consider \(K\ge 2\) candidates in a minimization problem. Label the unique ideal minimizer as candidate \(0\), set \(d=K-1\), and define its ideal gaps against the other candidates by

\[
\Delta_i=F_i-F_0>0,
\qquad i=1,\ldots,d.
\tag{2}
\]

For method \(j\in\{\mathrm r,\mathrm m\}\), where \(\mathrm r\) denotes raw and \(\mathrm m\) denotes mitigated, assume the Gaussian finite-shot gap model

\[
\widehat{\boldsymbol\Delta}_j(B)
=\boldsymbol\mu_j+B^{-1/2}Z_j,
\qquad
Z_j\sim\mathcal N(0,\Sigma_j).
\tag{3}
\]

Here \(B\) is the same total charged budget for both methods, \(\boldsymbol\mu_j\) is the population noisy gap vector, and \(\Sigma_j/B\) is the covariance of the estimated gaps. Ties count as failures. The method selects candidate \(0\) correctly exactly when every estimated gap is positive.

Let

\[
\Phi_d(x;\Sigma)=\Pr\{Z_1\le x_1,\ldots,Z_d\le x_d\},
\qquad Z\sim\mathcal N(0,\Sigma).
\tag{4}
\]

## Proposition 1K: exact Gaussian comparison

### Proposition

Under (2)--(3), the decision-error probability of method \(j\) is

\[
R_j(B)
=1-\Phi_d\!\left(\sqrt B\,\boldsymbol\mu_j;\Sigma_j\right).
\tag{5}
\]

Consequently, mitigation has lower \(K\)-candidate decision error at budget \(B\) if and only if

\[
\boxed{
\Phi_d\!\left(\sqrt B\,\boldsymbol\mu_{\rm m};\Sigma_{\rm m}\right)
>
\Phi_d\!\left(\sqrt B\,\boldsymbol\mu_{\rm r};\Sigma_{\rm r}\right).
}
\tag{6}
\]

Equation (6), rather than \(d\) separate marginal comparisons, is the exact \(K\)-candidate extension.

### Proof

Candidate \(0\) is selected correctly exactly on the event

\[
\boldsymbol\mu_j+B^{-1/2}Z_j>0
\]

coordinatewise. By central Gaussian symmetry, its probability is

\[
\Pr\{Z_j<\sqrt B\,\boldsymbol\mu_j\}
=\Phi_d(\sqrt B\,\boldsymbol\mu_j;\Sigma_j).
\]

Taking the complement gives (5), and comparing the two success probabilities gives (6). ∎

### Why the two-candidate scalar rule does not extend automatically

For \(K=2\), \(d=1\), so the covariance has only one variance and (6) reduces exactly to (1). For \(K>2\), off-diagonal covariance affects the probability that all gaps are positive. Improving every one-dimensional error probability therefore need not order the joint top-1 error when the correlation structures differ.

The budget cancellation in the previous proposition is also not general. It remains available under the shared-correlation condition below, but with arbitrary \(\Sigma_{\rm r}\) and \(\Sigma_{\rm m}\), the ordering in (6) can depend on \(B\).

## Corollary: a usable componentwise sufficient condition

Write

\[
D_j=\operatorname{diag}(\sigma_{j,1},\ldots,\sigma_{j,d}),
\qquad
\mathcal R_j=D_j^{-1}\Sigma_jD_j^{-1},
\tag{7}
\]

and assume all marginal standard deviations are positive. Suppose the two methods have the same standardized gap correlation matrix,

\[
\mathcal R_{\rm r}=\mathcal R_{\rm m}=\mathcal R.
\tag{8}
\]

Define the marginal variance-overhead ratios

\[
\gamma_i=\frac{\sigma_{\rm m,i}^2}{\sigma_{\rm r,i}^2}.
\tag{9}
\]

If

\[
\boxed{
\mu_{\rm m,i}\ge \sqrt{\gamma_i}\,\mu_{\rm r,i}
\quad\text{for every }i,
}
\tag{10}
\]

then \(R_{\rm m}(B)\le R_{\rm r}(B)\) for every \(B>0\). The inequality is strict if \(\mathcal R\) is nondegenerate and at least one inequality in (10) is strict.

### Proof

Let \(X\sim\mathcal N(0,\mathcal R)\). Under (8), the success event of method \(j\) has the same probability as

\[
X_i>-\sqrt B\,\frac{\mu_{j,i}}{\sigma_{j,i}}
\quad\text{for every }i.
\tag{11}
\]

Condition (10) is equivalent to

\[
\frac{\mu_{\rm m,i}}{\sigma_{\rm m,i}}
\ge
\frac{\mu_{\rm r,i}}{\sigma_{\rm r,i}}
\quad\text{for every }i.
\]

Using the same \(X\) to couple the two events, the raw success orthant is contained in the mitigated success orthant. This proves weak dominance. A nondegenerate Gaussian assigns positive probability to the additional open region created by a strict threshold inequality, which proves strict dominance. ∎

Condition (10) is sufficient but not necessary for \(K>2\): an improvement in one critical gap can outweigh a deterioration in another. If (8) is not justified, equation (6) or a confidence-set version of it must be used instead.

## Complete-debiasing attenuation form

If mitigation removes the population gap bias completely, so that

\[
\boldsymbol\mu_{\rm m}=\boldsymbol\Delta,
\]

define the raw attenuation of each ideal gap by

\[
a_i=\frac{\mu_{\rm r,i}}{\Delta_i}.
\tag{12}
\]

Under the shared-correlation condition (8), the componentwise certificate

\[
\boxed{
a_i\sqrt{\gamma_i}<1
\quad\text{for every }i
}
\tag{13}
\]

is sufficient for mitigation to have lower decision error at every budget. With a common variance multiplier \(\gamma_i=\gamma\), this becomes

\[
\max_i a_i<\frac{1}{\sqrt\gamma}.
\tag{14}
\]

For \(K=2\), (13) is the previous proposition's necessary-and-sufficient attenuation rule. For \(K>2\), it is a simultaneous sufficient certificate, not a necessary condition for the joint orthant probability.

## Correction when \(a\) and \(\gamma\) are estimated

A plug-in statement such as

\[
\widehat a_i\sqrt{\widehat\gamma_i}<1
\]

ignores pilot uncertainty and is not a certificate. Let the pilot construct simultaneous one-sided bounds

\[
a_i\le \overline a_i,
\qquad
\gamma_i\le \overline\gamma_i,
\qquad i=1,\ldots,d,
\tag{15}
\]

with joint coverage at least \(1-\alpha_{\rm pilot}\). Under complete debiasing and (8), the uncertainty-corrected attenuation rule is

\[
\boxed{
\max_i \overline a_i\sqrt{\overline\gamma_i}<1.
}
\tag{16}
\]

On the joint-coverage event, (16) implies (13). The confidence bounds must therefore be simultaneous over candidates and over both parameter families; multiplying two separately reported 95% intervals does not give a 95% joint statement.

The same correction can be written without assuming complete debiasing. Let simultaneous bounds satisfy

\[
\mu_{\rm m,i}\ge\underline\mu_{\rm m,i},
\qquad
\mu_{\rm r,i}\le\overline\mu_{\rm r,i},
\qquad
\gamma_i\le\overline\gamma_i.
\tag{17}
\]

When the raw gaps are known to be positive, a sufficient pilot conclusion is

\[
\boxed{
\underline\mu_{\rm m,i}
>
\sqrt{\overline\gamma_i}\,\overline\mu_{\rm r,i}
\quad\text{for every }i.
}
\tag{18}
\]

If the shared-correlation model is not imposed, let \(C_j\) be a joint confidence set for \((\boldsymbol\mu_j,\Sigma_j)\). A direct conservative comparison is

\[
\sup_{(\mu,\Sigma)\in C_{\rm m}}
R^{G}(B;\mu,\Sigma)
<
\inf_{(\mu,\Sigma)\in C_{\rm r}}
R^{G}(B;\mu,\Sigma),
\tag{19}
\]

where

\[
R^{G}(B;\mu,\Sigma)
=1-\Phi_d(\sqrt B\,\mu;\Sigma).
\]

Equation (19) protects the full joint decision probability and permits the two methods to have different correlation matrices. Failure of (16), (18), or (19) means **not certified by the pilot**; it does not prove that raw is better.

## Small-sample and non-normal correction

Scavino (2026), Proposition 7.1, gives a finite-shot gap central-limit approximation for independent bounded per-shot outcomes under fixed positive allocation fractions, bounded mitigation-map norm, covariance convergence, fixed dimension, and uniformly bounded third moments. For convex polyhedral events, its stated Berry--Esseen error is \(O(B^{-1/2})\).

Let \(R_j^{G}(B)\) be the Gaussian risk in (5), and suppose an explicit finite-sample calculation supplies

\[
\left|R_j(B)-R_j^{G}(B)\right|
\le \varepsilon_j(B).
\tag{20}
\]

Then the corrected sufficient comparison is

\[
\boxed{
R_{\rm m}^{G}(B)+\varepsilon_{\rm m}(B)
<
R_{\rm r}^{G}(B)-\varepsilon_{\rm r}(B).
}
\tag{21}
\]

With estimated parameters, combine the corrections:

\[
\boxed{
\sup_{(\mu,\Sigma)\in C_{\rm m}}
\left[R^{G}(B;\mu,\Sigma)+\varepsilon_{\rm m}(B)\right]
<
\inf_{(\mu,\Sigma)\in C_{\rm r}}
\left[R^{G}(B;\mu,\Sigma)-\varepsilon_{\rm r}(B)\right].
}
\tag{22}
\]

The constants in \(\varepsilon_j(B)\) depend on dimension, covariance conditioning, outcome bounds, third moments, and the fixed allocation. Writing only \(O(B^{-1/2})\) is not enough to apply (21) in a finite pilot; those constants or valid numerical upper bounds must be frozen before Part 3.

If the assumptions needed for a useful Berry--Esseen bound fail, a distribution-free alternative is to construct simultaneous confidence regions for the primitive categorical probabilities and optimize the exact finite-sample decision risk over those regions. That approach avoids normality but can be computationally expensive. No asymptotic Gaussian ordering should be reported as a finite-sample guarantee when neither correction is available.

## Comparison with Scavino's effective margin

Scavino (2026), arXiv:2607.02888v1, calls \((\mu_m,\Sigma_m)\) the “effective margin–kernel pair” and defines

\[
\mu_m=\Delta+La_m,
\qquad
\Sigma_m=LK_mL^\top.
\tag{23}
\]

Its exact Gaussian argmin risk is the same orthant probability as (5). Thus the substantive \(K\)-candidate object here is not a new gap representation: \(\boldsymbol\mu_j\) is Scavino's effective margin, and \(\Sigma_j\) is its decision kernel.

The narrower contribution of this extension is to connect the previous project's scalar Raw-versus-mitigation threshold to that multivariate object. Equation (6) gives the exact comparison, (10) gives a transparent sufficient rule under shared standardized correlation, and (16)--(22) state what must change when the margins and overheads are estimated rather than known. Scavino's formulation also makes clear why a variance ratio alone cannot decide the \(K>2\) case: the off-diagonal decision kernel can change the orthant risk.

## Relation to the QEM-limits literature

[Source: Takagi et al. (2022); reading depth: arXiv abstract only.] The abstract states that the paper derives bounds relating error reduction to sampling overhead for a general class of QEM protocols, including exponential depth scaling for local depolarizing noise and an optimality statement for probabilistic error cancellation under local dephasing noise.

[Source: Quek et al. (2024); reading depth: arXiv abstract only.] The abstract states that, for broad classes of QEM schemes, estimating noiseless observable expectation values can require a superpolynomial number of samples in the worst case even at shallow depth.

[Source: the present derivation compared with the Takagi and Quek abstracts; reading depth: this derivation plus those abstracts only.] In the limited single-estimator sense used here, \(\gamma\) is the finite-instance variance or sampling-overhead parameter of the same resource type whose unavoidable growth is lower-bounded in those works.

[Source: the present derivation; reading depth: complete derivation in this file.] The quantity \(\gamma\) is not itself either paper's universal lower bound, and this file claims neither their theorem hypotheses nor their asymptotic scaling for the present experiment.

[Source: the present derivation compared with the Takagi and Quek abstracts; reading depth: this derivation plus those abstracts only.] Equations (6), (10), and (21) add a decision-level consequence for one declared estimator and candidate set, but they do not convert estimator-level sampling lower bounds into a new universal decision lower bound.

## Draft Part 3 pilot estimators and decision rule — to be frozen in Part 1d

This subsection is a draft only. It does not run the secondary endpoint, alter the endpoint, or authorize access to scoring data.

### Data and estimators

1. Freeze the \(K\) candidates, ZNE noise scales, extrapolation weights, total pilot budget, number of independent pilot blocks, and the Raw/ZNE allocation within each block.
2. In every pilot block, reproduce the future scoring allocation once for Raw and once for ZNE. For each method, record the full vector of candidate values and all \(K-1\) gaps against the pilot anchor.
3. Obtain the pilot anchor and an ideal-gap proxy from the frozen ZNE response model fitted only to pilot noisy-scale data. No noiseless or ideal target value may be read. Candidate-selection uncertainty must be handled by simultaneous all-pair bounds; if the pilot cannot isolate one anchor, the rule defaults to Raw.
4. Across independent pilot blocks, estimate

\[
\widehat{\boldsymbol\mu}_j
=\frac1{R_p}\sum_{b=1}^{R_p}\widehat{\boldsymbol\Delta}_{j,b},
\qquad
\widehat\Sigma_j
=\frac1{R_p-1}\sum_{b=1}^{R_p}
(\widehat{\boldsymbol\Delta}_{j,b}-\widehat{\boldsymbol\mu}_j)
(\widehat{\boldsymbol\Delta}_{j,b}-\widehat{\boldsymbol\mu}_j)^\top.
\tag{24}
\]

5. Estimate each marginal variance overhead by

\[
\widehat\gamma_i
=\frac{\widehat\Sigma_{\rm m,ii}}
{\widehat\Sigma_{\rm r,ii}}.
\tag{25}
\]

6. Let \(\widehat\Delta_i^{\rm pilot}\) be the intercept gap from the frozen noisy-scale response fit. Estimate attenuation by

\[
\widehat a_i
=\frac{\widehat\mu_{\rm r,i}}
{\widehat\Delta_i^{\rm pilot}}.
\tag{26}
\]

Equation (26) is model-based: it estimates attenuation relative to a noisy-data extrapolated intercept, not a known ideal value. If the response model is wrong, \(\widehat a_i\) need not estimate the attenuation in (12). If a simultaneous confidence interval for any \(\Delta_i^{\rm pilot}\) contains zero, the corresponding ratio is unstable and the rule defaults to Raw.

7. Construct one joint \(1-\alpha_{\rm pilot}\) confidence set for both methods' margins and covariance matrices. Part 1d must freeze the construction, multiplicity correction, covariance regularization if any, and a computable finite-sample error bound \(\varepsilon_j(B)\). These choices may not be selected after seeing Part 3 scoring results.

### Draft binary prediction rule

For each new graph, compute the robust comparison in (22) at the frozen scoring budget.

- Predict **ZNE better** only if (22) holds.
- Otherwise predict **Raw better**.
- Record whether the result was a certified Raw advantage, an uncertified default to Raw, an unstable attenuation ratio, or an unresolved pilot anchor; these labels are diagnostics and do not change the binary prediction or hit-rate endpoint.

Under a separately frozen shared-correlation model, (18) may replace the multivariate optimization, and (16) is the complete-debiasing cross-check. Absence of evidence against equal correlations is not evidence that (8) holds; Part 1d must either justify that structural assumption or use (22).

### Items that Part 1d must freeze

- candidate and anchor construction;
- ZNE response family, noise scales, and weights;
- pilot block count and every shot allocation;
- estimators in (24)--(26);
- confidence-set method and simultaneous coverage level;
- the explicit \(\varepsilon_j(B)\) calculation or the finite-sample alternative;
- the binary default and all tie rules;
- the exact prediction-file fields written before scoring.

## Conditions and limits

- Equations (5)--(6) are exact only under the Gaussian gap model.
- Equation (10) additionally requires a common standardized correlation matrix; it is not valid merely because marginal variance ratios are available.
- Equations (13) and (16) additionally require complete debiasing, or a clearly declared proxy model for it.
- Estimated \(a\) cannot be identified from Raw data alone without information about the ideal gap or a response-model assumption. The pilot draft uses the latter and records that dependence.
- The Berry--Esseen correction is useful only when its finite constant is evaluated; an asymptotic order symbol is not a certificate.
- This extension supports only the already-declared secondary Proposition 1 prediction test. It does not change the project's primary endpoint.

## Sources used

- Previous project, <code>paper/main.tex</code>, lines 194--217 (read only): original two-candidate Proposition 1.
- Scavino, V. (2026), *Decision Kernels for Quantum Error Mitigation: Why Accuracy Gains Need Not Improve Downstream Decisions*, arXiv:2607.02888v1, especially equations (27), (87), and (95), and Proposition 7.1.
- Takagi, R., Endo, S., Minagawa, S., and Gu, M. (2022), *Fundamental Limits of Quantum Error Mitigation*, npj Quantum Information 8, 114; abstract only for the claims above.
- Quek, Y., Stilck França, D., Khatri, S., Meyer, J. J., and Eisert, J. (2024), *Exponentially Tighter Bounds on Limitations of Quantum Error Mitigation*, Nature Physics 20, 1648; abstract only for the claims above.
