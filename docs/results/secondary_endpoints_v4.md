# Secondary endpoints, protocol v4 holdout (Task 3-2)

Evidence type: noisy simulation, holdout split 20 (the single run of Task
3-1). Secondary endpoints of protocol v4 Sections 11.2--11.5; none of them
changes the primary outcome. Recomputable with
`experiments/holdout/score_secondary_v4.py`, which was committed before it
was first run.

## 1. Coverage and interception (main operating point)

| Structure | C(R0) | C(R1) | Loss R1 [95% CI] | Interception R1 (units) | C(R1, P2) | Loss P2 [95% CI] | Interception P2 (units) |
|---|---:|---:|---|---|---:|---|---|
| E1 | 0.2978 | 0.0147 | +0.2831 [+0.2166, +0.3503] | insufficient (0) | 0.2191 | +0.0788 [+0.0459, +0.1138] | insufficient (0) |
| E2 | 0.6025 | 0.3000 | +0.3025 [+0.2372, +0.3678] | 0.744 (195) | 0.3000 | +0.3025 [+0.2372, +0.3678] | 0.744 (195) |
| E3 | 0.5747 | 0.3109 | +0.2637 [+0.2084, +0.3203] | 1.000 (36) | 0.3984 | +0.1762 [+0.1278, +0.2253] | 0.222 (36) |
| E4 | 0.4906 | 0.0000 | +0.4906 [+0.4084, +0.5716] | insufficient (0) | 0.3728 | +0.1178 [+0.0759, +0.1613] | insufficient (0) |
| E5 | 0.5778 | 0.0000 | +0.5778 [+0.4959, +0.6569] | insufficient (0) | 0.4806 | +0.0972 [+0.0675, +0.1278] | insufficient (0) |
| E5' | 0.4409 | 0.0000 | +0.4409 [+0.3578, +0.5219] | insufficient (0) | 0.3331 | +0.1078 [+0.0672, +0.1503] | insufficient (0) |
| E6 | 0.5650 | 0.0000 | +0.5650 [+0.4856, +0.6428] | insufficient (0) | 0.4525 | +0.1125 [+0.0772, +0.1494] | insufficient (0) |
| pooled R1 | | | +0.4177 [+0.3596, +0.4736] | 0.784 (231) | | | |
| pooled R1_P2 | | | +0.1418 [+0.1113, +0.1727] | 0.662 (231) | | | |

## 2. Flip subset (descriptive; designated probe, decision alarm)

| Structure | Probe | Flipped graphs | Alarm rate, flipped [95% CI] | Alarm rate, not flipped [95% CI] |
|---|---|---:|---|---|
| E1 | P1 | 13 | 0.0649 [0.0288, 0.1106] (n=13) | 0.4404 [0.3560, 0.5266] (n=87) |
| E2 | P2 | 20 | 0.4719 [0.3016, 0.6484] (n=20) | 0.4289 [0.3441, 0.5164] (n=80) |
| E3 | P3 | 8 | 0.6250 [0.3711, 0.8672] (n=8) | 0.3798 [0.3135, 0.4504] (n=92) |
| E4 | P4a | 0 | insufficient | 1.0000 [1.0000, 1.0000] (n=100) |
| E5 | P4a | 1 | insufficient | 1.0000 [1.0000, 1.0000] (n=99) |
| E5' | P4a | 10 | 1.0000 [1.0000, 1.0000] (n=10) | 1.0000 [1.0000, 1.0000] (n=90) |
| E6 | P4a | 0 | insufficient | 1.0000 [1.0000, 1.0000] (n=100) |

## 3. Visibility agreement (42 cells, never pooled)

| Stratum | Agreement [95% CI] | Cells | Agreement at smallest strength |
|---|---|---:|---:|
| invariant | 0.9130 [0.9130, 0.9565] | 23 | 22 / 23 |
| sensitive | 0.6316 [0.5789, 0.6842] | 19 | 9 / 19 |

| Cell | Stratum | Predicted | Power | Power-0.80 | Power-0.10 | False alarm | FA-0.10 | Observed | Agree | alpha_0.01 | alpha_0.10 | power_visible_0.50 | power_visible_0.90 | false_alarm_visible_0.05 | false_alarm_visible_0.15 | Smallest-strength label |
|---|---|---|---:|---:|---:|---:|---:|---|---|---|---|---|---|---|---|---|
| P1/E1 | sensitive | visible | 0.4000 | -0.4000 | +0.3000 | 0.0578 | -0.0422 | partial | NO | partial | partial | partial | partial | partial | partial | partial |
| P1/E2 | invariant | blind | 0.0381 | -0.7619 | -0.0619 | 0.0387 | -0.0613 | blind | yes | blind | blind | blind | blind | blind | blind | blind |
| P1/E3 | sensitive | partial | 0.6128 | -0.1872 | +0.5128 | 0.0612 | -0.0388 | partial | yes | partial | partial | visible | partial | partial | partial | blind |
| P1/E4 | invariant | blind | 0.0475 | -0.7525 | -0.0525 | 0.0453 | -0.0547 | blind | yes | blind | blind | blind | blind | blind | blind | blind |
| P1/E5 | invariant | blind | 0.0494 | -0.7506 | -0.0506 | 0.0547 | -0.0453 | blind | yes | blind | blind | blind | blind | blind | blind | blind |
| P1/E5' | invariant | blind | 0.0544 | -0.7456 | -0.0456 | 0.0519 | -0.0481 | blind | yes | blind | blind | blind | blind | blind | blind | blind |
| P1/E6 | sensitive | blind | 0.0559 | -0.7441 | -0.0441 | 0.0472 | -0.0528 | blind | yes | blind | blind | blind | blind | blind | blind | blind |
| P2/E1 | sensitive | partial | 0.1834 | -0.6166 | +0.0834 | 0.0531 | -0.0469 | partial | yes | partial | partial | partial | partial | partial | partial | partial |
| P2/E2 | sensitive | partial | 0.4163 | -0.3838 | +0.3163 | 0.0491 | -0.0509 | partial | yes | partial | partial | partial | partial | partial | partial | blind |
| P2/E3 | sensitive | partial | 0.2475 | -0.5525 | +0.1475 | 0.0494 | -0.0506 | partial | yes | partial | partial | partial | partial | partial | partial | blind |
| P2/E4 | sensitive | partial | 0.1697 | -0.6303 | +0.0697 | 0.0587 | -0.0413 | partial | yes | partial | partial | partial | partial | partial | partial | blind |
| P2/E5 | sensitive | partial | 0.0862 | -0.7138 | -0.0138 | 0.0925 | -0.0075 | blind | NO | partial | blind | blind | blind | blind | blind | blind |
| P2/E5' | invariant | blind | 0.1316 | -0.6684 | +0.0316 | 0.1331 | +0.0331 | partial | NO | partial | partial | partial | partial | partial | partial | partial |
| P2/E6 | sensitive | partial | 0.1131 | -0.6869 | +0.0131 | 0.1128 | +0.0128 | partial | yes | partial | blind | partial | partial | partial | partial | partial |
| P3/E1 | invariant | blind | 0.0456 | -0.7544 | -0.0544 | 0.0506 | -0.0494 | blind | yes | blind | blind | blind | blind | blind | blind | blind |
| P3/E2 | invariant | blind | 0.0369 | -0.7631 | -0.0631 | 0.0509 | -0.0491 | blind | yes | blind | blind | blind | blind | blind | blind | blind |
| P3/E3 | sensitive | visible | 0.3794 | -0.4206 | +0.2794 | 0.0522 | -0.0478 | partial | NO | partial | partial | partial | partial | partial | partial | blind |
| P3/E4 | invariant | blind | 0.0434 | -0.7566 | -0.0566 | 0.0488 | -0.0513 | blind | yes | blind | blind | blind | blind | blind | blind | blind |
| P3/E5 | invariant | blind | 0.0475 | -0.7525 | -0.0525 | 0.0406 | -0.0594 | blind | yes | blind | blind | blind | blind | blind | blind | blind |
| P3/E5' | invariant | blind | 0.0600 | -0.7400 | -0.0400 | 0.0534 | -0.0466 | blind | yes | blind | blind | blind | blind | blind | blind | blind |
| P3/E6 | sensitive | blind | 0.0384 | -0.7616 | -0.0616 | 0.0366 | -0.0634 | blind | yes | blind | blind | blind | blind | blind | blind | blind |
| P4a/E1 | invariant | blind | 0.0000 | -0.8000 | -0.1000 | 0.0000 | -0.1000 | blind | yes | blind | blind | blind | blind | blind | blind | blind |
| P4a/E2 | invariant | blind | 0.0000 | -0.8000 | -0.1000 | 0.0000 | -0.1000 | blind | yes | blind | blind | blind | blind | blind | blind | blind |
| P4a/E3 | invariant | blind | 0.0000 | -0.8000 | -0.1000 | 0.0000 | -0.1000 | blind | yes | blind | blind | blind | blind | blind | blind | blind |
| P4a/E4 | sensitive | visible | 1.0000 | +0.2000 | +0.9000 | 0.0000 | -0.1000 | visible | yes | visible | visible | visible | visible | visible | visible | visible |
| P4a/E5 | invariant | blind | 0.0494 | -0.7506 | -0.0506 | 0.0444 | -0.0556 | blind | yes | blind | blind | blind | blind | blind | blind | blind |
| P4a/E5' | invariant | blind | 0.0547 | -0.7453 | -0.0453 | 0.0419 | -0.0581 | blind | yes | blind | blind | blind | blind | blind | blind | blind |
| P4a/E6 | sensitive | partial | 0.7153 | -0.0847 | +0.6153 | 0.0472 | -0.0528 | partial | yes | partial | visible | visible | partial | partial | partial | blind |
| P4b/E1 | invariant | blind | 0.0000 | -0.8000 | -0.1000 | 0.0000 | -0.1000 | blind | yes | blind | blind | blind | blind | blind | blind | blind |
| P4b/E2 | invariant | blind | 0.0000 | -0.8000 | -0.1000 | 0.0000 | -0.1000 | blind | yes | blind | blind | blind | blind | blind | blind | blind |
| P4b/E3 | invariant | blind | 0.0000 | -0.8000 | -0.1000 | 0.0000 | -0.1000 | blind | yes | blind | blind | blind | blind | blind | blind | blind |
| P4b/E4 | sensitive | visible | 1.0000 | +0.2000 | +0.9000 | 0.0000 | -0.1000 | visible | yes | visible | visible | visible | visible | visible | visible | visible |
| P4b/E5 | sensitive | partial | 0.0100 | -0.7900 | -0.0900 | 0.0481 | -0.0519 | blind | NO | blind | blind | blind | blind | blind | blind | blind |
| P4b/E5' | invariant | blind | 0.0522 | -0.7478 | -0.0478 | 0.0366 | -0.0634 | blind | yes | blind | blind | blind | blind | blind | blind | blind |
| P4b/E6 | sensitive | partial | 0.1191 | -0.6809 | +0.0191 | 0.0387 | -0.0613 | partial | yes | blind | partial | partial | partial | partial | partial | blind |
| P5/E1 | invariant | blind | 0.1869 | -0.6131 | +0.0869 | 0.0528 | -0.0472 | partial | NO | partial | partial | partial | partial | partial | partial | blind |
| P5/E2 | invariant | blind | 0.0525 | -0.7475 | -0.0475 | 0.0641 | -0.0359 | blind | yes | blind | blind | blind | blind | blind | blind | blind |
| P5/E3 | sensitive | partial | 0.9822 | +0.1822 | +0.8822 | 0.0475 | -0.0525 | visible | NO | visible | visible | visible | visible | visible | visible | partial |
| P5/E4 | sensitive | partial | 1.0000 | +0.2000 | +0.9000 | 0.0475 | -0.0525 | visible | NO | visible | partial | visible | visible | visible | visible | partial |
| P5/E5 | invariant | blind | 0.0537 | -0.7463 | -0.0463 | 0.0578 | -0.0422 | blind | yes | blind | blind | blind | blind | blind | blind | blind |
| P5/E5' | invariant | blind | 0.0403 | -0.7597 | -0.0597 | 0.0403 | -0.0597 | blind | yes | blind | blind | blind | blind | blind | blind | blind |
| P5/E6 | sensitive | partial | 1.0000 | +0.2000 | +0.9000 | 0.0516 | -0.0484 | visible | NO | visible | partial | visible | visible | partial | visible | partial |

## 4. Readout certificate (v3 Section 11.2), compared with R0

| Cell | Rule | False certification [95% CI] | Unresolved [95% CI] |
|---|---|---|---|
| P4a/E4 | certificate | 0.0000 [0.0000, 0.0000] | 1.0000 [1.0000, 1.0000] |
| P4a/E4 | R0 | 0.0000 [0.0000, 0.0000] | 0.5094 [0.4272, 0.5928] |
| P4a/E4 | bound | finite fraction 0.981; median finite B 0.3100; mean retained channels 0.98 | |
| P4b/E4 | certificate | 0.0000 [0.0000, 0.0000] | 1.0000 [1.0000, 1.0000] |
| P4b/E4 | R0 | 0.0000 [0.0000, 0.0000] | 0.5094 [0.4272, 0.5928] |
| P4b/E4 | bound | finite fraction 0.996; median finite B 0.3100; mean retained channels 3.03 | |
| P4b/E5 | certificate | 0.0000 [0.0000, 0.0000] | 0.8666 [0.8103, 0.9200] |
| P4b/E5 | R0 | 0.0000 [0.0000, 0.0000] | 0.4222 [0.3422, 0.5041] |
| P4b/E5 | bound | finite fraction 0.998; median finite B 0.1200; mean retained channels 7.97 | |

E4 never flips a decision (Section 4.1), so for E4 the comparison is
coverage gained or lost, not error prevented.

## 5. Probe fraction f*

not evaluable under v4: no frozen thresholds at f = 0.05 or 0.25 (holdout plan Section 2); f* = 0 for P0 and P5 by zero probe cost.
