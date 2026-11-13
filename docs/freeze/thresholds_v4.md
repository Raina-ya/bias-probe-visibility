# Alarm thresholds, protocol v4 (Task 2-3)

Evidence type: noisy simulation, development split 10 only. Rule: protocol
v4 Section 6.3, main alpha 0.05 (sensitivity alphas 0.01 and 0.10 are in
`results/development_v4/thresholds_v4.csv`).
Each threshold is a per-stratum order statistic of n development null
scores; the alarm is strict, `T > tau`. Thresholds were computed once and
are not recalibrated on non-null settings or holdout data.

- Threshold rows (all alphas): 6300; main-alpha rows: 2100.
- Matched-null rows with a degenerate (identically 0) null: 200 of 1050.
- Clean-E0 rows with a degenerate null: 350 of 1050, of which 50 are `temporal_contrast` (not recorded under E0; tau = 0).

## Decision-endpoint thresholds (clean E0, alpha 0.05)

Designated probes (E1 P1, E2 P2, E3 P3, E4--E6 P4a) and the
structure-agnostic P2 variant. Range over the 25 width-depth strata.

| Structure | Probe | Component | n per stratum | min tau | max tau | degenerate strata |
|---|---|---|---:|---:|---:|---:|
| E1 | P1 | statistic | 448 | 0.00693377 | 0.0137017 | 0 |
| E1 | P2 | statistic | 448 | 0.0111111 | 0.0262515 | 0 |
| E2 | P2 | statistic | 448 | 0.0111111 | 0.0262515 | 0 |
| E3 | P2 | statistic | 448 | 0.0111111 | 0.0262515 | 0 |
| E3 | P3 | statistic | 448 | 0.0140952 | 0.0277272 | 0 |
| E4 | P2 | statistic | 448 | 0.0111111 | 0.0262515 | 0 |
| E4 | P4a | assignment | 448 | 0 | 0 | 25 |
| E5 | P2 | statistic | 448 | 0.0111111 | 0.0262515 | 0 |
| E5 | P4a | assignment | 448 | 0 | 0 | 25 |
| E5' | P2 | statistic | 448 | 0.0111111 | 0.0262515 | 0 |
| E5' | P4a | assignment | 448 | 0 | 0 | 25 |
| E6 | P2 | statistic | 448 | 0.0111111 | 0.0262515 | 0 |
| E6 | P4a | temporal_contrast | 448 | 0 | 0 | 25 |

## Matched-null thresholds (alpha 0.05)

Range over the 25 width-depth strata for each of the 42 cells.

| Probe | Structure | Component | Matched null | n per stratum | min tau | max tau | degenerate strata |
|---|---|---|---|---:|---:|---:|---:|
| P1 | E1 | statistic | `0.0` | 64 | 0.00596031 | 0.0182515 | 0 |
| P1 | E2 | statistic | `0.0` | 64 | 0.00793519 | 0.0163186 | 0 |
| P1 | E3 | statistic | `0.0` | 64 | 0.00626847 | 0.0173507 | 0 |
| P1 | E4 | statistic | `(0.0,0.0)` | 64 | 0.00573946 | 0.0150887 | 0 |
| P1 | E5 | statistic | `0.0` | 64 | 0.00546296 | 0.0176443 | 0 |
| P1 | E5' | statistic | `0.0` | 64 | 0.00660536 | 0.0148418 | 0 |
| P1 | E6 | statistic | `0.0` | 64 | 0.00607339 | 0.0159329 | 0 |
| P2 | E1 | statistic | `0.0` | 64 | 0.0113553 | 0.0296093 | 0 |
| P2 | E2 | statistic | `0.0` | 64 | 0.0120879 | 0.0323565 | 0 |
| P2 | E3 | statistic | `0.0` | 64 | 0.00989011 | 0.0286935 | 0 |
| P2 | E4 | statistic | `(0.0,0.0)` | 64 | 0.0113553 | 0.0323565 | 0 |
| P2 | E5 | statistic | `0.0` | 64 | 0.011803 | 0.0934066 | 0 |
| P2 | E5' | statistic | `0.0` | 64 | 0.011803 | 0.28022 | 0 |
| P2 | E6 | statistic | `0.0` | 64 | 0.0116867 | 0.111477 | 0 |
| P3 | E1 | statistic | `0.0` | 64 | 0.0139577 | 0.0310038 | 0 |
| P3 | E2 | statistic | `0.0` | 64 | 0.0147406 | 0.0344293 | 0 |
| P3 | E3 | statistic | `0.0` | 64 | 0.0121173 | 0.036965 | 0 |
| P3 | E4 | statistic | `(0.0,0.0)` | 64 | 0.0125597 | 0.0335912 | 0 |
| P3 | E5 | statistic | `0.0` | 64 | 0.0127282 | 0.0286427 | 0 |
| P3 | E5' | statistic | `0.0` | 64 | 0.0135562 | 0.0289849 | 0 |
| P3 | E6 | statistic | `0.0` | 64 | 0.0146364 | 0.0324907 | 0 |
| P4a | E1 | assignment | `0.0` | 64 | 0 | 0 | 25 |
| P4a | E2 | assignment | `0.0` | 64 | 0 | 0 | 25 |
| P4a | E3 | assignment | `0.0` | 64 | 0 | 0 | 25 |
| P4a | E4 | assignment | `(0.0,0.0)` | 64 | 0 | 0 | 25 |
| P4a | E5 | assignment | `0.0` | 64 | 0.120879 | 0.130647 | 0 |
| P4a | E5' | assignment | `0.0` | 64 | 0.282051 | 0.291819 | 0 |
| P4a | E6 | temporal_contrast | `0.0` | 64 | 0.0391794 | 0.0514402 | 0 |
| P4b | E1 | t_marg | `0.0` | 64 | 0 | 0 | 25 |
| P4b | E2 | t_marg | `0.0` | 64 | 0 | 0 | 25 |
| P4b | E3 | t_marg | `0.0` | 64 | 0 | 0 | 25 |
| P4b | E4 | t_marg | `(0.0,0.0)` | 64 | 0 | 0 | 25 |
| P4b | E5 | t_corr | `0.0` | 64 | 0.0567108 | 0.195556 | 0 |
| P4b | E5' | t_corr | `0.0` | 64 | 0.123702 | 0.293333 | 0 |
| P4b | E6 | temporal_contrast | `0.0` | 64 | 0.176471 | 0.571429 | 0 |
| P5 | E1 | statistic | `0.0` | 64 | 0.0361328 | 0.107178 | 0 |
| P5 | E2 | statistic | `0.0` | 64 | 0.0327148 | 0.103271 | 0 |
| P5 | E3 | statistic | `0.0` | 64 | 0.0344238 | 0.104492 | 0 |
| P5 | E4 | statistic | `(0.0,0.0)` | 64 | 0.0332031 | 0.106689 | 0 |
| P5 | E5 | statistic | `0.0` | 64 | 0.0373535 | 0.108643 | 0 |
| P5 | E5' | statistic | `0.0` | 64 | 0.0368652 | 0.11377 | 0 |
| P5 | E6 | statistic | `0.0` | 64 | 0.0722656 | 0.166016 | 0 |

## Inputs (SHA-256)

- `results/development_v4/main/shard_0000_of_0004.jsonl.gz`: `45a9f4b4c5814a45e66a15098e53f6408a5d906c8cab63cea85ec36e8bf48980`
- `results/development_v4/main/shard_0001_of_0004.jsonl.gz`: `83f8ea2e4db416e75919763ded19a0a939515648e8d5d591068ecd1514793be8`
- `results/development_v4/main/shard_0002_of_0004.jsonl.gz`: `7c14ff648d8acc4a98a3907b4e27b71487607b5e5f2113d552fd252924a48906`
- `results/development_v4/main/shard_0003_of_0004.jsonl.gz`: `1be0add8e43f085a223f033eca9b12a66dd896c55e6c86ca91e3ee504807b75a`
- `results/development_v4/nulls/shard_0000_of_0004.jsonl.gz`: `10aab1d7c481b9062f0845940385729e7b7b16c05e7f9667e3b3eab2cddcbbb3`
- `results/development_v4/nulls/shard_0001_of_0004.jsonl.gz`: `7ffd51fe93c7d388f6e935ddb5515678deb0dd8f65e9c64b218ac9bf9b7e9dc2`
- `results/development_v4/nulls/shard_0002_of_0004.jsonl.gz`: `4e74c9bb47025d0a851e78b0bf8a1413d2935ca41682ede489ca8144ce8d5d55`
- `results/development_v4/nulls/shard_0003_of_0004.jsonl.gz`: `6c924a6250cdd9c0de55855625bf8ba971c95c776850005be6753c97f4c9ae44`
- `thresholds_v4.csv`: `567e522e80db508c30bec95a831670babae4701818da1b4dabd8668a3aeea0dd`
