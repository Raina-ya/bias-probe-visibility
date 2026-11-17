# Hardware go / no-go review, protocol v4 (Task 4-2)

Status: review only, 2026-11-17. No job was submitted, no IBM Quantum account
or API key was used, and nothing here authorizes a run. Protocol v4 Section 14
and the project plan, Section 13, govern any future run.

## Verdict: **NO-GO** under current conditions

Four of the seven go conditions are not met (Section 2). Two of them cannot be
met by this review: the owner's explicit authorization, and registered
predictions with a frozen analysis. The scientific case is real but narrow:
whether real readout has pair correlation that marginal checks miss bears on
whether the synthetic E5 and E5' models are plausible. It does not bear on the
holdout decision results, where uniform readout never flips a QAOA-MaxCut
decision and readout structures produced no CI-only false certification.

## 1. Provider terms (checked 2026-11-17)

| Item | Current statement | Source |
|---|---|---|
| Open Plan allowance | "the RU equivalent of up to 10 minutes per 28-day rolling window" | [IBM Quantum docs, Plans overview](https://quantum.cloud.ibm.com/docs/guides/plans-overview) |
| Unit | Resource units; "for standard QPU workloads, 1 RU = 1 minute of QPU compute time", introduced "as of November 2026" | same |
| Region | Open Plan instances only in us-east | same |
| Promotion | From 16 March 2026, an opt-in of an extra 180 minutes over 12 months for qualifying Open Plan users; the base 10 minutes per 28 days is unchanged | [IBM Quantum blog, Open Plan updates (16 March 2026)](https://www.ibm.com/quantum/blog/open-plan-updates) |

The protocol cap of 360 reported QPU seconds (6 minutes, plus a 30-second
reserve in the shot formula) fits inside the base allowance. The unit changed
to RUs this month, so the RU-to-second conversion for this workload must be
re-read from the provider immediately before any run. This review does not
rely on the promotion.

## 2. Go conditions

| # | Condition (protocol v4 Section 14, plan Section 13) | Status | Evidence |
|---|---|---|---|
| 1 | Explicit, run-specific authorization by the owner | **Not met** | Hardware is unauthorized by protocol v4. |
| 2 | Renewed provider-terms check | Met (for this date) | Section 1; must be repeated on the run day. |
| 3 | Registered predictions and a frozen analysis for the readout test | **Not met** | No hardware prediction or statistic is registered. Matched nulls do not exist on hardware, so a null for "pair correlation beyond the product of marginals" (for example a parametric bootstrap under independence of the observed marginals) must be frozen first. |
| 4 | Only P4a/P4b circuits; total at most 360 reported QPU seconds | Satisfiable | Section 14 shot formula. |
| 5 | At least 100 shots per circuit after the measured pilot | **Unknown** | Section 14 forbids an assumed time per shot. Feasibility can be known only after the pilot, which itself spends QPU time. At width 8, P4b needs 4 x C(8,2) = 112 preparations. |
| 6 | Enough power for a decision-relevant effect | **Not met by current evidence** | In simulation at n_P = 1,638, P4b/E5 (pair correlation, tau = 0.01 on a 0.10 marginal) had holdout power 0.010 (main) and 0.026 (smallest), labelled blind. P4b/E5' had 0.052. The test that would decide the question is untested at any hardware budget. |
| 7 | A result changes a registered conclusion | **Not met** | Readout structures produced zero R0 false certifications on the holdout (primary endpoint, per structure). Uniform readout cannot flip a decision (analytic, freeze review v2 Section 3.1). A hardware correlation finding would inform model transportability, not the endpoints. |

## 3. No-go triggers present

- **No authorization.** This is decisive by itself.
- **No registered prediction.** A run now would be exploratory hardware data
  with no confirmatory status.
- **No measured time per shot.** The budget cannot be planned without spending
  QPU time, and the protocol forbids an assumed value.
- **Simulation power for the target effect is low** at the protocol's probe
  budget. Whether 360 s buys enough shots per pair is unknown.

## 4. What would change the verdict to GO

1. The owner explicitly authorizes one run, naming the backend and date.
2. Before the run, a short protocol amendment is registered on OSF with:
   - the statistic (pair total-variation distance from the product of
     observed marginals, per pair and preparation);
   - the null (parametric bootstrap under independence, with a frozen seed);
   - the multiplicity rule;
   - the reduction order (shots first, then width), the 100-shot floor, and the
     Section 14 formula;
   - a directional prediction, for example "no pair exceeds the null at
     alpha = 0.05 after Bonferroni", with the simulation basis stated.
3. A simulation-only power check of that statistic at plausible shot counts
   per circuit (planning only, split 99) shows that a decision-relevant pair
   correlation would be detectable.
4. The provider terms and the RU conversion are re-read on the run day, and
   the job records backend, calibration timestamp, job IDs, and reported
   quantum seconds.

## 5. How this is reported

The paper states that no hardware experiment was run, that a go/no-go review
returned NO-GO, and why (Sections 2 and 3). The decision-level conclusions are
labelled noisy simulation only. The E5' channel remains a synthetic stress test
without hardware evidence.
