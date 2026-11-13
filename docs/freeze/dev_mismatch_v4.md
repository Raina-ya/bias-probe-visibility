# Development mismatch report, protocol v4 (Task 2-3)

Evidence type: noisy simulation, development split 10 only (50 graphs, two
per width-depth stratum, 32 repeats). These labels are descriptive. Under
protocol v4 Section 16.3 a disagreement is a failed prediction and does not
revise the matrix, a probe, a threshold, or a tolerance. An
invariant-stratum disagreement indicates an implementation or derivation
error (Section 5.2); its investigation is in
`docs/freeze/dev_mismatch_investigation_v4.md`.

Power is the main-operating-point alarm rate and false alarm is the
matched-null alarm rate, both against the per-stratum matched-null
thresholds computed from the same development null rows. The false-alarm
rate is therefore in-sample and optimistic by construction; holdout uses
these thresholds on new graphs. Each distance is `value - threshold`.

Main operating points (strength map): E1 `0.04`, E2 `-0.04`, E3 `-0.04`, E4 `(0.08,0.12)`, E5 `-0.01`, E5' `-0.015625`, E6 `-0.03`.

## Agreement by stratum (main thresholds)

| Stratum | Agreeing cells | Cells |
|---|---:|---:|
| invariant | 22 | 23 |
| sensitive | 11 | 19 |

Disagreeing cells: 9 (invariant 1, sensitive 8).

## All 42 cells

Sensitivity columns change one value at a time (Section 8): alpha 0.01 with
blind boundary 0.06; alpha 0.10 with blind boundary 0.15; power for
visible 0.50 and 0.90; false alarm for visible 0.05 and 0.15.

| Probe | Structure | Stratum | Predicted | Power | Power-0.80 | Power-0.10 | False alarm | FA-0.10 | Observed | Agree | a0.01 | a0.10 | pv0.50 | pv0.90 | fa0.05 | fa0.15 |
|---|---|---|---|---:|---:|---:|---:|---:|---|---|---|---|---|---|---|---|
| P1 | E1 | sensitive | visible | 0.4531 | -0.3469 | +0.3531 | 0.0312 | -0.0688 | partial | NO | partial | partial | partial | partial | partial | partial |
| P1 | E2 | invariant | blind | 0.0344 | -0.7656 | -0.0656 | 0.0312 | -0.0688 | blind | yes | blind | blind | blind | blind | blind | blind |
| P1 | E3 | sensitive | partial | 0.6150 | -0.1850 | +0.5150 | 0.0312 | -0.0688 | partial | yes | partial | partial | visible | partial | partial | partial |
| P1 | E4 | invariant | blind | 0.0462 | -0.7538 | -0.0538 | 0.0312 | -0.0688 | blind | yes | blind | blind | blind | blind | blind | blind |
| P1 | E5 | invariant | blind | 0.0494 | -0.7506 | -0.0506 | 0.0312 | -0.0688 | blind | yes | blind | blind | blind | blind | blind | blind |
| P1 | E5' | invariant | blind | 0.0550 | -0.7450 | -0.0450 | 0.0312 | -0.0688 | blind | yes | blind | blind | blind | blind | blind | blind |
| P1 | E6 | sensitive | blind | 0.0425 | -0.7575 | -0.0575 | 0.0312 | -0.0688 | blind | yes | blind | blind | blind | blind | blind | blind |
| P2 | E1 | sensitive | partial | 0.1550 | -0.6450 | +0.0550 | 0.0312 | -0.0688 | partial | yes | partial | partial | partial | partial | partial | partial |
| P2 | E2 | sensitive | partial | 0.3762 | -0.4238 | +0.2762 | 0.0312 | -0.0688 | partial | yes | partial | partial | partial | partial | partial | partial |
| P2 | E3 | sensitive | partial | 0.1713 | -0.6288 | +0.0713 | 0.0306 | -0.0694 | partial | yes | partial | partial | partial | partial | partial | partial |
| P2 | E4 | sensitive | partial | 0.1688 | -0.6313 | +0.0688 | 0.0312 | -0.0688 | partial | yes | partial | partial | partial | partial | partial | partial |
| P2 | E5 | sensitive | partial | 0.0413 | -0.7588 | -0.0588 | 0.0312 | -0.0688 | blind | NO | blind | blind | blind | blind | blind | blind |
| P2 | E5' | invariant | blind | 0.0444 | -0.7556 | -0.0556 | 0.0312 | -0.0688 | blind | yes | blind | blind | blind | blind | blind | blind |
| P2 | E6 | sensitive | partial | 0.0450 | -0.7550 | -0.0550 | 0.0312 | -0.0688 | blind | NO | blind | blind | blind | blind | blind | blind |
| P3 | E1 | invariant | blind | 0.0406 | -0.7594 | -0.0594 | 0.0312 | -0.0688 | blind | yes | blind | blind | blind | blind | blind | blind |
| P3 | E2 | invariant | blind | 0.0375 | -0.7625 | -0.0625 | 0.0312 | -0.0688 | blind | yes | blind | blind | blind | blind | blind | blind |
| P3 | E3 | sensitive | visible | 0.3300 | -0.4700 | +0.2300 | 0.0312 | -0.0688 | partial | NO | partial | partial | partial | partial | partial | partial |
| P3 | E4 | invariant | blind | 0.0375 | -0.7625 | -0.0625 | 0.0312 | -0.0688 | blind | yes | blind | blind | blind | blind | blind | blind |
| P3 | E5 | invariant | blind | 0.0325 | -0.7675 | -0.0675 | 0.0312 | -0.0688 | blind | yes | blind | blind | blind | blind | blind | blind |
| P3 | E5' | invariant | blind | 0.0531 | -0.7469 | -0.0469 | 0.0312 | -0.0688 | blind | yes | blind | blind | blind | blind | blind | blind |
| P3 | E6 | sensitive | blind | 0.0356 | -0.7644 | -0.0644 | 0.0312 | -0.0688 | blind | yes | blind | blind | blind | blind | blind | blind |
| P4a | E1 | invariant | blind | 0.0000 | -0.8000 | -0.1000 | 0.0000 | -0.1000 | blind | yes | blind | blind | blind | blind | blind | blind |
| P4a | E2 | invariant | blind | 0.0000 | -0.8000 | -0.1000 | 0.0000 | -0.1000 | blind | yes | blind | blind | blind | blind | blind | blind |
| P4a | E3 | invariant | blind | 0.0000 | -0.8000 | -0.1000 | 0.0000 | -0.1000 | blind | yes | blind | blind | blind | blind | blind | blind |
| P4a | E4 | sensitive | visible | 1.0000 | +0.2000 | +0.9000 | 0.0000 | -0.1000 | visible | yes | visible | visible | visible | visible | visible | visible |
| P4a | E5 | invariant | blind | 0.0494 | -0.7506 | -0.0506 | 0.0288 | -0.0713 | blind | yes | blind | blind | blind | blind | blind | blind |
| P4a | E5' | invariant | blind | 0.0413 | -0.7588 | -0.0588 | 0.0281 | -0.0719 | blind | yes | blind | blind | blind | blind | blind | blind |
| P4a | E6 | sensitive | partial | 0.7200 | -0.0800 | +0.6200 | 0.0312 | -0.0688 | partial | yes | partial | visible | visible | partial | partial | partial |
| P4b | E1 | invariant | blind | 0.0000 | -0.8000 | -0.1000 | 0.0000 | -0.1000 | blind | yes | blind | blind | blind | blind | blind | blind |
| P4b | E2 | invariant | blind | 0.0000 | -0.8000 | -0.1000 | 0.0000 | -0.1000 | blind | yes | blind | blind | blind | blind | blind | blind |
| P4b | E3 | invariant | blind | 0.0000 | -0.8000 | -0.1000 | 0.0000 | -0.1000 | blind | yes | blind | blind | blind | blind | blind | blind |
| P4b | E4 | sensitive | visible | 1.0000 | +0.2000 | +0.9000 | 0.0000 | -0.1000 | visible | yes | visible | visible | visible | visible | visible | visible |
| P4b | E5 | sensitive | partial | 0.0100 | -0.7900 | -0.0900 | 0.0294 | -0.0706 | blind | NO | blind | blind | blind | blind | blind | blind |
| P4b | E5' | invariant | blind | 0.0550 | -0.7450 | -0.0450 | 0.0306 | -0.0694 | blind | yes | blind | blind | blind | blind | blind | blind |
| P4b | E6 | sensitive | partial | 0.1100 | -0.6900 | +0.0100 | 0.0206 | -0.0794 | partial | yes | blind | partial | partial | partial | partial | partial |
| P5 | E1 | invariant | blind | 0.1694 | -0.6306 | +0.0694 | 0.0312 | -0.0688 | partial | NO | partial | partial | partial | partial | partial | partial |
| P5 | E2 | invariant | blind | 0.0400 | -0.7600 | -0.0600 | 0.0275 | -0.0725 | blind | yes | blind | blind | blind | blind | blind | blind |
| P5 | E3 | sensitive | partial | 0.9675 | +0.1675 | +0.8675 | 0.0306 | -0.0694 | visible | NO | visible | visible | visible | visible | visible | visible |
| P5 | E4 | sensitive | partial | 1.0000 | +0.2000 | +0.9000 | 0.0312 | -0.0688 | visible | NO | visible | visible | visible | visible | visible | visible |
| P5 | E5 | invariant | blind | 0.0406 | -0.7594 | -0.0594 | 0.0294 | -0.0706 | blind | yes | blind | blind | blind | blind | blind | blind |
| P5 | E5' | invariant | blind | 0.0431 | -0.7569 | -0.0569 | 0.0306 | -0.0694 | blind | yes | blind | blind | blind | blind | blind | blind |
| P5 | E6 | sensitive | partial | 1.0000 | +0.2000 | +0.9000 | 0.0294 | -0.0706 | visible | NO | visible | visible | visible | visible | visible | visible |

Rows per cell: 1600 main and 1600 matched-null (50 graphs x 32 repeats).

The smallest-strength sensitivity operating point was not run in
development; its labels are evaluated on the holdout only.
