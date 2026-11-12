# Core definitions

Status: task 1a-1 complete. The project owner approved all project definitions and assumptions on 2026-11-11.

## Setup

Let \(P\) be the joint observable distribution of target and runtime-probe outputs under a frozen design. Let \(e\in\mathcal E\) be the unknown noise structure, with \(\mathcal E\) fixed before observing data. Assume

\[
\Delta=f(P,e).
\]

For a strict top-1 decision, \(\Delta>0\) supports the designated winner and \(\Delta\le0\) does not certify it.

Source for the abstract form: Imbens and Manski (2004), Section 2. The quantum-noise substitution, joint target-and-probe distribution, and sign interpretation are this project's derivation.

## Identification region

\[
\mathcal I_\Delta(P;\mathcal E)=\{f(P,e'):e'\in\mathcal E\}.
\]

Only compatible values for which \(f(P,e')\) is defined are included. If compatibility is not encoded in the domain of \(f\), it must be written explicitly rather than assumed.

Source: range construction from Imbens and Manski (2004), Section 2; application to a decision gap and noise class is this project's derivation.

## Blind in principle

The design is **blind in principle** at \(P\) relative to \(\mathcal E\) if

\[
\mathcal I_\Delta(P;\mathcal E)\cap(0,\infty)\ne\varnothing,
\qquad
\mathcal I_\Delta(P;\mathcal E)\cap(-\infty,0]\ne\varnothing.
\]

The inclusion of zero on the failure side follows the strict-top-1 endpoint and was approved by the project owner on 2026-11-11.

This project's definition.

## Blind within budget

Fix the total budget, probe allocation, target power, and false-alarm limit. A design is **blind within budget** for a specified alternative class if its population distributions are distinguishable, but no admissible rule using the frozen observations and budget meets both operating requirements uniformly over that class.

The exact quantifiers and lower bound belong to task 1a-3.

This project's definition.

## Visible

A design is **visible under the frozen budget and operating requirements** for a specified alternative class if an admissible rule using only frozen target and probe observations reaches the required power while controlling false alarms uniformly over that class.

This finite-budget property is distinct from point identification: a gap can be identifiable with unlimited data yet blind within budget.

When a protocol averages over a prespecified distribution of graphs and noise
parameters instead of requiring a uniform guarantee, the narrower term
**design-distribution visible** must be used. It means that the distribution-
averaged power and false-alarm requirements are met under that exact frozen
mixture. It does not imply uniform visibility for every graph, width, depth, or
parameter value. The confirmatory protocol uses this mixture-average version
and reports stratum minima only as a limitation analysis.

This project's definition.

## Assumptions that must be stated

1. **Unique recovery conditional on noise.** Given \(P\) and \(e\), \(\Delta=f(P,e)\) is unique. If not, the region must range over additional unresolved quantities.
2. **Fixed but modelled as unknown.** The ideal gap is fixed in principle; it is treated as unknown because probes may not read it and the target is assumed not to be classically simulable at scale.
3. **Fixed noise class, enlarged observables.** A probe enlarges joint \(P\), while prespecified \(\mathcal E\) stays fixed. Fewer noise elements may remain compatible. This is the project's derivation and requires an explicit compatibility construction.
4. **Decision convention.** Zero fails to certify a strict top-1 decision. The project owner approved this convention on 2026-11-11.

## Project-owner approval

On 2026-11-11, the project owner explicitly approved all of the following as this project's definitions or choices:

- positive-versus-non-positive blindness;
- zero as certification failure;
- blind within budget;
- finite-budget visible, separated from point identification;
- joint-\(P\), fixed-\(\mathcal E\) compatibility;
- uniqueness/invertibility and practical-unknown assumptions.
