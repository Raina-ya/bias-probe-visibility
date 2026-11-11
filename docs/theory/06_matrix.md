# Probe-by-error-structure visibility matrix

Status: task 1b-1 complete, including the analytic E3 closure on 2026-11-11; analytic predictions only. No simulation or hardware evidence is used here. P1b and GVS are exploratory F3 baselines and are excluded from the primary endpoint.

## Decision rule and validity condition

Let the target's observed decision gap under noise parameter (e) be (g(e)=\Delta+\beta(e)), and let probe (j) have population statistic (t_j(e)). For a component (e_r), define

\[
\kappa_{j,r}=\frac{\partial t_j(e)}{\partial e_r},
\qquad
b_r=\frac{\partial g(e)}{\partial e_r}.
\]

A nonzero (\kappa_{j,r}) is not enough. A cell is called **visible** only when the probe has a known reference, constrains the same decision-relevant component for which (b_r\ne0), and the transfer from probe to target is identified under the stated model. This is **this project's quantum condition, by analogy with the U-comparability of Lipsitch et al. 2010**. It is this project's condition, not a condition stated by Lipsitch et al.

Predictions mean:

- **visible**: the frozen structure supplies the shared, identifiable sensitivity needed by the condition;
- **blind**: an allowed direction changes the target gap while leaving the probe statistic invariant, or the statistic contains no bias information;
- **partial**: only a specified component is visible, or visibility needs an additional transfer/context condition;
- **?**: the frozen structure is not parameterized enough to determine even conditional sensitivity.

E0 is a negative control: by definition its common-mode component is annihilated by the decision contrast and cannot flip the decision. A probe classified blind under E0 may still fluctuate; it cannot identify decision-flipping bias there.

### Frozen primary-endpoint model for E3

E3 is a static coherent ZZ insertion model on a fixed physical layout. After
each scheduled hard two-qubit cycle \(\ell\), the device applies

\[
V_\ell(e)=\exp\!\left[-\frac{i}{2}
\sum_{r=(i,j)} e_r h_{\ell r} Z_iZ_j\right].
\tag{E3.1}
\]

The coefficients \(h_{\ell r}\), active pairs, layout, and schedule are fixed
before simulation. The parameter vector \(e\) is constant within a run and is
shared by both candidates and their probe circuits; differential bias comes
from their different sensitivities, not from assigning them different noise
parameters. E3 is decision relevant only for components with
\(b_r=\partial g/\partial e_r\ne0\).

The probe transformations are also fixed. P1 uses scale 1 and local unitary
folding at scale 3; E3.1 is applied after every physical hard cycle, including
inserted inverse cycles. P2 changes only the non-Clifford single-qubit angles
to their nearest Clifford values while preserving the physical qubits, hard
two-qubit-cycle locations, and schedule length. P3 uses logically equivalent
versions with independent, uniform single-qubit Pauli frames on active qubits;
the frame set is exactly balanced for every sampled ZZ term, while layout and
hard-cycle locations remain fixed.

This is a synthetic, falsifiable model boundary, not a claim that every device
crosstalk process has this form. Time variation, spectator-dependent
coefficients, frame-dependent noise, and changed layouts are model violations
and are reported as such. Wallman and Emerson (2016) supply the randomized-
compiling noise-tailoring result; the componentwise sensitivities below are
this project's derivation for E3.1.

## Compact matrix

| Probe | E0 | E1 | E2 | E3 | E4 | E5 | E5' | E6 |
|---|---|---|---|---|---|---|---|---|
| P0 | blind | blind | blind | blind | blind | blind | blind | blind |
| P1 | blind | visible | partial | partial | blind | blind | blind | partial |
| P2 | blind | partial | partial | partial | partial | partial | partial | partial |
| P3 | blind | blind | visible | visible | blind | blind | blind | partial |
| P4a | blind | blind | blind | blind | visible | blind | blind | partial |
| P4b | blind | blind | blind | blind | visible | visible | blind | partial |
| P1b | blind | partial | partial | ? | blind | blind | blind | ? |
| GVS | blind | blind | blind | blind | blind | blind | blind | blind |
| P5 | blind | partial | partial | partial | partial | partial | partial | partial |

## P0: confidence-interval-only baseline

### P0 / E0 — blind (high)

Invariance: (L b_{\mathrm{common}}=0); P0 adds no statistic beyond the target sample. Failure condition: the classification changes only if E0 is redefined to contain a differential component.

### P0 / E1 — blind (high)

Invariance: a target-only interval quantifies sampling error, while observationally equivalent stochastic-noise explanations can leave opposite ideal-gap signs admissible. Failure condition: an external validated bias bound excludes sign crossing.

### P0 / E2 — blind (high)

Invariance: no auxiliary statistic constrains coherent bias, so the target-only identification fiber is unchanged. Failure condition: the coherent parameter is independently identified or bounded below the margin.

### P0 / E3 — blind (high)

Invariance: P0 adds no crosstalk-sensitive observation; allowed ZZ directions remain in the target-only fiber. Failure condition: E3 is point identified by external calibration.

### P0 / E4 — blind (high)

Invariance: the same observed distribution can be factored into different pre-readout distributions and asymmetric assignment channels. Failure condition: the assignment channel is externally known and stable.

### P0 / E5 — blind (high)

Invariance: compensating pre-readout distributions and pair-correlated assignment channels remain observationally equivalent to P0. Failure condition: the pair channel is externally identified.

### P0 / E5' — blind (high)

Invariance: no higher-order readout constraint is added. Failure condition: a full readout channel is externally identified.

### P0 / E6 — blind (high)

Invariance: the execution-time CI has no independent calibration-to-execution contrast. Failure condition: repeated calibration supplies a prespecified drift bound.

## P1: gap folding slope

### P1 / E0 — blind (high)

Invariance: folding preserves a common-mode shift, and (L b_{\mathrm{common}}=0). Failure condition: the nominal E0 component becomes differential.

### P1 / E1 — visible (medium)

Sensitivity: if folding maps (r\mapsto r(\lambda)), then (\kappa=\partial_\lambda g(r(\lambda))\ne0) when candidates have different stochastic attenuation. Failure condition: folding does not scale the relevant rate or candidate sensitivities are equal. Matching blind cells for P1 are E0, E4, E5, and E5'.

### P1 / E2 — partial (medium)

Sensitivity is construction-dependent: unitary folding may amplify, cancel, or reorient coherent accumulation. Failure condition: exact cancellation or a symmetry-preserving coherent direction gives (\kappa=0).

### P1 / E3 — partial (medium)

Let \(b_{r,\lambda}=\partial g_\lambda/\partial e_r\rvert_{e=0}\)
under the frozen folded schedule. For
\(t_1=(g_3-g_1)/(3-1)\),

\[
\kappa_{1,r}=\frac{b_{r,3}-b_{r,1}}{2}.
\tag{E3.2}
\]

The component is visible when the inserted hard cycles change its accumulated
decision sensitivity, so \(b_{r,3}\ne b_{r,1}\), and the folding-to-target
transfer is stable. It is blind when inverse cycles, echoing, commutation, or
equal candidate sensitivities give \(b_{r,3}=b_{r,1}\). E3.1 therefore fixes a
testable derivative but does not force it to be nonzero, so the cell is
partial. Matching blind cells for P1 remain E0, E4, E5, and E5'.

### P1 / E4 — blind (high)

Invariance: stable terminal independent readout is applied after, and is not scaled by, unitary folding. Failure condition: readout varies systematically with scale or runtime.

### P1 / E5 — blind (high)

Invariance: stable pair-correlated terminal readout is unchanged by inserted folds. Failure condition: folding changes measurement context or timing-dependent readout.

### P1 / E5' — blind (high)

Invariance: the same argument holds for stable higher-order terminal readout. Failure condition: scale changes the measurement context.

### P1 / E6 — partial (medium)

Sensitivity: sequential scale runs can acquire a slope from drift, but that slope is not attributable to folded noise. Failure condition: common drift remains invisible; randomized or interleaved scale order is required even for a drift interpretation.

## P2: nearest-Clifford twin

### P2 / E0 — blind (high)

Invariance: E0 cannot flip the target contrast and a truly shared common mode cancels. Failure condition: twin and target do not actually share the nominal common mode.

### P2 / E1 — partial (medium)

Sensitivity: the known twin ideal value supplies a residual, but transfer requires nonzero aligned target/twin sensitivities to the same stochastic parameter. Failure condition: gate counts, supports, or Pauli sensitivities differ.

### P2 / E2 — partial (medium)

Sensitivity: a coherent component is constrained only when the twin derivative is aligned with the target derivative. Failure condition: target-only non-Clifford directions or orthogonal sensitivities.

### P2 / E3 — partial (medium)

For the frozen twin construction, let
\(b^{\mathrm{twin}}_r=\partial g_{\mathrm{twin}}/
\partial e_r\rvert_{e=0}\). Its known ideal value makes the twin residual's
sensitivity

\[
\kappa_{2,r}=b^{\mathrm{twin}}_r.
\tag{E3.3}
\]

Preserving layout and hard-cycle locations makes \(e_r\) shared, but it does
not make the target and twin state sensitivities equal. The component is
visible only when a prespecified nonzero transfer relation between
\(b^{\mathrm{twin}}_r\) and \(b_r\) holds. It is blind when the snapped angles
make \(b^{\mathrm{twin}}_r=0\), reverse its direction without a known map, or
move it into an orthogonal sensitivity. The cell is therefore partial.

### P2 / E4 — partial (medium)

Sensitivity: a known twin ideal can expose readout error, but target transfer depends on matching output-state weighting. Failure condition: twin and target populate differently weighted states.

### P2 / E5 — partial (medium)

Sensitivity: only pair modes jointly excited by twin and target satisfy the quantum condition. Failure condition: the decision-relevant pair mode is absent from the twin distribution.

### P2 / E5' — partial (low)

Sensitivity: the same transfer requirement applies to higher-order modes and is not guaranteed by Clifford proximity. Failure condition: the relevant higher-order mode is absent from the twin.

### P2 / E6 — partial (low)

Sensitivity: an interleaved twin may bracket drift. Failure condition: a noninterleaved twin does not identify target-time drift.

## P3: plain versus randomized-compiling versions

### P3 / E0 — blind (high)

Invariance: randomized frames do not make a common-mode decision shift differential. Failure condition: compilation changes the physical mapping and creates a differential component.

### P3 / E1 — blind (medium)

Invariance: an already-stochastic Pauli channel is in the randomized-compiling target class, so version averaging supplies no first-order mechanism contrast. Failure condition: the channel is context dependent across versions.

### P3 / E2 — visible (medium)

Sensitivity: coherent accumulation changes under randomized frames, so the plain-minus-version-mean gap has nonzero sensitivity for frame-sensitive coherence. Failure condition: frame-invariant or symmetry-preserving coherence. Matching blind cells for P3 are E0, E1, E4, E5, and E5'.

### P3 / E3 — visible (medium)

For Pauli frame \(F_\ell\), each sampled component obeys

\[
F_\ell^\dagger Z_iZ_jF_\ell=s_{\ell r}(F)Z_iZ_j,
\qquad s_{\ell r}(F)\in\{-1,+1\}.
\]

The frozen full-Pauli frame design is balanced, so
\(\mathbb E_F[s_{\ell r}(F)]=0\). Consequently the ensemble-mean compiled gap
has zero first-order derivative for the coherent E3 component, whereas the
plain gap has derivative \(b_r\). For
\(t_3=g_{\mathrm{plain}}-\mathbb E_F g_F\),

\[
\kappa_{3,r}=b_r-0=b_r\ne0.
\tag{E3.4}
\]

Thus the frozen decision-relevant coherent ZZ component is visible at the
population level. Failure conditions are an incomplete or unbalanced frame
set, frame- or gate-dependent E3 coefficients, changed layout or schedule,
non-Markov temporal correlations outside E3.1, or too few versions to resolve
the contrast within budget. Matching blind cells for P3 are E0, E1, E4, E5,
and E5'.

### P3 / E4 — blind (high)

Invariance: stable independent terminal readout is common to logically equivalent versions. Failure condition: layout, mapping, or measurement context changes.

### P3 / E5 — blind (high)

Invariance: stable pair-correlated terminal readout is not randomized by gate frames on a fixed layout. Failure condition: physical mapping changes across versions.

### P3 / E5' — blind (high)

Invariance: stable higher-order terminal readout is likewise unchanged. Failure condition: version-dependent layout or readout context.

### P3 / E6 — partial (low)

Sensitivity: interleaving can expose time variation, but version and temporal effects are not separately identified. Failure condition: common drift or blocked version ordering.

## P4a: one-qubit marginal readout check

### P4a / E0 — blind (high)

Invariance: marginal readout parameters have no sensitivity to a purely common-mode target shift. Failure condition: E0 includes readout asymmetry or differential bias.

### P4a / E1 — blind (high)

Invariance: computational-basis preparation does not reproduce the target gate path. Failure condition: unmodelled preparation gates import the target mechanism, which also confounds interpretation.

### P4a / E2 — blind (high)

Invariance: target coherent evolution is absent from the probe. Failure condition: the same coherent gates are inserted, changing P4a's definition.

### P4a / E3 — blind (medium)

Invariance: the target entangling schedule is absent. Failure condition: probe preparation uses the same crosstalk-generating schedule.

### P4a / E4 — visible (high)

Sensitivity: all-zero/all-one counts identify the two marginal assignment rates per qubit, hence (\kappa\ne0) for stable E4. Failure condition: state, context, or time dependence. Matching blind cells for P4a are E0, E1, E2, E3, E5, and E5'.

### P4a / E5 — blind (high)

Invariance: E5 is defined to preserve every checked one-qubit marginal. Failure condition: the implemented structure leaks into a marginal.

### P4a / E5' — blind (high)

Invariance: unchanged pairwise marginals imply unchanged one-qubit marginals. Failure condition: the implementation violates that constraint.

### P4a / E6 — partial (medium)

Sensitivity: bracketed or repeated checks constrain marginal drift inside the bracket. Failure condition: drift occurs after the last probe or only in unmeasured correlations.

## P4b: pairwise readout check

### P4b / E0 — blind (high)

Invariance: pair readout statistics have no decision relevance for a purely common-mode target shift. Failure condition: E0 contains readout structure.

### P4b / E1 — blind (high)

Invariance: basis-state pair checks do not reproduce target stochastic gate noise. Failure condition: preparation error imports and confounds that mechanism.

### P4b / E2 — blind (high)

Invariance: pair basis probes omit target coherent evolution. Failure condition: target coherent gates are inserted, changing the probe.

### P4b / E3 — blind (medium)

Invariance: the frozen statistic characterizes terminal pair readout, not target ZZ evolution. Failure condition: its preparation schedule carries the same ZZ interaction.

### P4b / E4 — visible (high)

Sensitivity: four preparations per pair contain the single-qubit assignment rates. Failure condition: context or time mismatch. Matching blind cells for P4b are E0, E1, E2, E3, and E5'.

### P4b / E5 — visible (high)

Sensitivity: pair output distributions have nonzero derivative with respect to correlation parameters that preserve one-body marginals. Failure condition: the relevant pair is unmeasured or changes after calibration. Matching blind cells for P4b are E0, E1, E2, E3, and E5'.

### P4b / E5' — blind (high)

Invariance: under the frozen pairwise-statistic interpretation, E5' leaves every checked pairwise marginal unchanged. Failure condition and width caveat: at (w=3), retaining full joint outputs from all preparations can amount to full tomography; that is not the frozen statistic. A higher-order unprobed-column construction needs (w\ge4) or explicit marginalization.

### P4b / E6 — partial (medium)

Sensitivity: bracketed pair probes constrain measured pair-parameter drift. Failure condition: change after the bracket or drift only in higher-order components.

## P1b: negative Richardson probability weight

For per-scale distributions (P_s(\lambda_k)), Richardson gives (\widehat P(s)=\sum_k c_kP_s(\lambda_k)) and

\[
W_{\mathrm{neg}}=\sum_{s:\widehat P(s)<0}|\widehat P(s)|.
\]

Köster and Mauerer use this as a zero-extra-shot diagnostic of signal-destruction artefacts, not as a general error-mechanism identifier.

### P1b / E0 — blind (high)

Invariance: a common-mode decision shift need not create negative extrapolated probabilities. Failure condition: E0 is redefined to drive folded distributions to their floor.

### P1b / E1 — partial (medium)

Sensitivity: when amplified stochastic noise destroys per-state signal, negative Richardson coefficients can make (W_{\mathrm{neg}}>0). Failure condition: before floor collapse, the same E1 may flip a decision without a flag; no universal formal threshold is supplied by the source.

### P1b / E2 — partial (low)

Sensitivity: coherent amplification can yield negative extrapolated weights, but the statistic diagnoses extrapolation invalidity rather than coherent decision bias. Failure condition: probabilities remain physical or the decision flips away from floor collapse.

### P1b / E3 — ? (low)

Reason: the frozen E3 class has no map from ZZ strength to scale-dependent floor collapse. Resolution requires an E3 scale map.

### P1b / E4 — blind (medium)

Invariance: stable terminal readout is not amplified by folding, so there is no E4-specific (W_{\mathrm{neg}}) contrast. Failure condition: scale-dependent readout may trigger the statistic but destroys mechanism attribution.

### P1b / E5 — blind (medium)

Invariance: stable pair readout is present equally at each scale. Failure condition: scale-dependent readout or an already-unphysical extrapolated distribution.

### P1b / E5' — blind (medium)

Invariance: the same argument holds for stable higher-order readout. Failure condition: scale-dependent measurement context.

### P1b / E6 — ? (low)

Reason: drift across scale blocks can create negative weights, but direction and size depend on ordering and trajectory. Resolution requires a frozen temporal design and drift model.

## GVS: covariance-survival reference baseline

Scavino v1 defines

\[
\mathrm{GVS}(\mathcal C)=
\frac{\operatorname{tr}(L_{\mathcal C}K L_{\mathcal C}^{\top})}
{\operatorname{tr}(K_{\mathcal C})+\epsilon_0}.
\]

The source expressly describes GVS as a covariance diagnostic that does not include margins. Therefore a deterministic bias field can change at fixed (K), proving blindness to bias for every row below. GVS may still describe variance geometry; the classification concerns decision-bias visibility.

### GVS / E0 — blind (high)

Invariance: common-mode covariance may vanish under (L), but no systematic margin is learned. Failure condition: adding independently valid margins creates a different diagnostic.

### GVS / E1 — blind (high)

Invariance: two stochastic-noise models can share (K) and differ in systematic gap bias. Failure condition: a model uniquely ties covariance to bias and is independently validated.

### GVS / E2 — blind (high)

Invariance: coherent mean shifts can vary at fixed (K). Failure condition: none within covariance-only GVS.

### GVS / E3 — blind (high)

Invariance: systematic ZZ bias can vary without changing the scalar covariance ratio. Failure condition: GVS may see a stochastic variance effect, not its bias sign.

### GVS / E4 — blind (high)

Invariance: assignment bias can change gap means while GVS remains fixed. Failure condition: margins or a readout model are added.

### GVS / E5 — blind (high)

Invariance: pair-correlated mean bias is not identified by a covariance-survival ratio. Failure condition: full bias information is supplied externally.

### GVS / E5' — blind (high)

Invariance: higher-order mean bias can likewise vary at fixed GVS. Failure condition: full margins and distributional structure are added.

### GVS / E6 — blind (high)

Invariance: deterministic drift moves means at fixed within-block covariance. Failure condition: time-indexed repeated means define a different diagnostic.

## P5: symmetry component from target counts

### Positioning relative to earlier work

The blind spot is not new. Bonet-Monroig et al. (2018) introduced symmetry verification, including a zero-cost post-processing protocol. Scavino Alfaro, arXiv:2606.15464v1--v2, explicitly called the remaining term the “residual undetectable-sector bias”; the current v3 states equivalently that the residual bias comes from symmetry-preserving errors that postselection cannot detect. That work computes the residual coefficient from an assumed noise model, ideal state, and observable; it is not a runtime detector of that residual. This project therefore does **not** claim to discover the P5 blind spot. Its narrower contribution is to place the blind spot on the same probe-by-structure boundary map as the other probes, charge all probes to one fixed total budget, evaluate the target decision rather than estimator MSE, and use the global sign criterion from 01_definitions.md.

### Derivation of the blind sector

Let \(P\) project onto the valid symmetry sector and let the ideal state satisfy

\[
P\rho_\star P=\rho_\star .
\]

P5 reuses the target counts to estimate a symmetry statistic, which can be written as the acceptance probability

\[
t_5(\rho)=\operatorname{Tr}(P\rho)
\]

or an affine equivalent such as the expectation of a two-sector symmetry operator. For a differentiable noise path

\[
\rho_\epsilon=\rho_\star+\epsilon\,\dot\rho+O(\epsilon^2),
\qquad \operatorname{Tr}(\dot\rho)=0,
\]

the probe sensitivity is

\[
\kappa_5=\left.\frac{d}{d\epsilon}t_5(\rho_\epsilon)\right|_{\epsilon=0}
=\operatorname{Tr}(P\dot\rho).
\tag{P5.1}
\]

Decompose the tangent perturbation into an in-sector component and the remainder:

\[
\dot\rho_{\mathrm{in}}=P\dot\rho P,
\qquad
\dot\rho_{\mathrm{out}}=\dot\rho-\dot\rho_{\mathrm{in}}.
\]

If the perturbation is trace preserving and entirely in the valid sector, then

\[
\dot\rho=P\dot\rho P
\quad\Longrightarrow\quad
\kappa_5=\operatorname{Tr}(\dot\rho)=0.
\tag{P5.2}
\]

For a target decision contrast \(C=O_A-O_B\), however,

\[
b_{\mathrm{in}}
=\left.\frac{d}{d\epsilon}\operatorname{Tr}(C\rho_\epsilon)\right|_{\epsilon=0}
=\operatorname{Tr}(C\dot\rho_{\mathrm{in}})
\tag{P5.3}
\]

need not vanish. Thus there can be two admissible in-sector perturbations with identical P5 population statistic but decision gaps on opposite sides of zero. Equations (P5.2)--(P5.3) give the invariance proof required by this project's definition of blind in principle. They are the decision-level counterpart of the residual undetectable sector, not a claim made by the cited papers.

For a symmetry-preserving coherent generator \(H\), \([H,P]=0\) and

\[
\dot\rho=-i[H,\rho_\star]=P\dot\rho P.
\]

Therefore P5 is exactly invariant along this direction even though
\(\operatorname{Tr}(C\dot\rho)\) may be nonzero. For a symmetry-breaking
unitary generator, acceptance loss from an ideal symmetry eigenstate is
generally \(O(\epsilon^2)\), not necessarily first order; it can be visible
in principle but much harder to resolve within a fixed shot budget.

### Prediction and failure conditions

The row-level prediction is **partial** for every broad structure that contains both symmetry-breaking and symmetry-preserving components, and **blind** for E0. “Partial” does not certify the target decision: it says only that some components can change the checked statistic.

### P5 / E0 — blind (high)

Invariance: a common-mode shift preserves the checked symmetry and cannot flip the contrast. Failure condition: the nominal common mode contains a symmetry-breaking differential component.

### P5 / E1 — partial (medium)

Sensitivity: stochastic Pauli components that move population outside the valid sector change \(t_5\), typically at first order in their probability. Failure condition: symmetry-preserving Pauli mixtures satisfy (P5.2) and may still change the decision gap.

### P5 / E2 — partial (high)

Sensitivity: symmetry-breaking coherent rotations can create detectable leakage, but from an ideal symmetry eigenstate the acceptance loss is generally second order in the rotation angle. Failure condition: \([H,P]=0\) gives exact invariance while (P5.3) can remain nonzero.

### P5 / E3 — partial (medium)

Sensitivity: a ZZ term is visible only through a component that leaves the chosen sector. Failure condition: for the global bit-flip symmetry used by QAOA MaxCut, a ZZ generator commutes with that symmetry and lies in P5's blind sector.

### P5 / E4 — partial (medium)

Sensitivity: asymmetric assignment can change the observed sector probability. Failure condition: a readout channel covariant under the symmetry action preserves \(t_5\) while still potentially biasing the decision observable.

### P5 / E5 — partial (medium)

Sensitivity: only the symmetry-breaking projection of pair-correlated readout changes the checked statistic. Failure condition: symmetry-preserving pair correlations remain in the residual blind sector.

### P5 / E5' — partial (medium)

Sensitivity: only the projection of higher-order readout onto the checked symmetry component is visible. Failure condition: a higher-order channel can preserve the checked sector while changing the decision contrast.

### P5 / E6 — partial (low)

Sensitivity: because P5 reuses target counts, it can reflect drift only when the drift changes the checked sector during target acquisition. Failure condition: symmetry-preserving drift is blind, and without time-separated repetitions P5 cannot attribute a change to drift.

## Source and scope notes

- Lipsitch et al. (2010) supplies only the U-comparability analogy; the quantum sensitivity/identification condition above is this project's derivation.
- Köster and Mauerer (2026), arXiv:2607.09360v2, Section VI, defines the full-distribution negative-probability check and (W_{\mathrm{neg}}). Its demonstrated scope is the Richardson signal-destruction regime.
- Scavino (2026), arXiv:2607.02888v1, Section 10, defines GVS and states that it is not a complete decision-risk score because it omits margins. The repository's frozen GVS baseline is therefore version-specific.
- The P3 predictions do not constitute a proof of randomized compiling under general noise. The E3 question marks record precisely where the plan lacks a sufficient physical parameterization.
- E5' is a synthetic stress structure in this project; no verified hardware evidence for decision-important three-body readout correlation is claimed.

The machine-readable counterpart is `docs/theory/06_matrix.csv`. It contains the same 72 predictions, derivation summaries, failure conditions, and confidence labels.
