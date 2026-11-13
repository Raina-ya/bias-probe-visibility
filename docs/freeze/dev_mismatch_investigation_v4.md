# Investigation of the invariant-stratum disagreement P5/E1 (development)

Evidence type: noisy simulation, development split 10 only, plus a
parametric re-sampling diagnostic. This document changes no matrix label,
probe, threshold, or rule (protocol v4 Section 16.3).

## Implementation check: is the E1 population complement-symmetric?

Pooled over 32 repeats, 100 graph-candidate chi-square tests of
`p(z)=p(not z)` at the E1 main point gave
minimum p = 0.0110, fraction p < 0.05 = 0.050,
fraction p < 0.01 = 0.000.
Under exact symmetry these fractions are expected near 0.05 and 0.01.

## Finite-shot check: plug-in bias of P5 under a symmetric population

| Rows | Mean observed P5 | Mean P5 re-sampled from the symmetrized counts |
|---|---:|---:|
| matched null (`p=0`), n=1600 | 0.054090 | 0.051685 |
| E1 main (`p=0.04`), n=1600 | 0.059243 | 0.056640 |
| shift, E1 minus null | +0.005152 | +0.004955 |

The symmetric re-sampling reproduces 0.96 of the observed shift.

## Reading

If the symmetry tests are consistent with uniform p-values and the
symmetric re-sampling reproduces the observed shift, the disagreement is
not an implementation error. It is a derivation error in the scope of the
invariant stratum: the matrix established invariance of the population
statistic (P5 of the expected counts, the semantic-test quantity), but P5
is a nonlinear plug-in statistic whose finite-shot expectation depends on
the shape of a symmetric distribution, and depolarization changes that
shape. Under Section 16.3 the matrix label stays `blind`; on the holdout
this cell is scored against `blind` as registered.

## Inputs (SHA-256)

- `shard_0000_of_0004.jsonl.gz` (nulls): `10aab1d7c481b9062f0845940385729e7b7b16c05e7f9667e3b3eab2cddcbbb3`
- `shard_0001_of_0004.jsonl.gz` (nulls): `7ffd51fe93c7d388f6e935ddb5515678deb0dd8f65e9c64b218ac9bf9b7e9dc2`
- `shard_0002_of_0004.jsonl.gz` (nulls): `4e74c9bb47025d0a851e78b0bf8a1413d2935ca41682ede489ca8144ce8d5d55`
- `shard_0003_of_0004.jsonl.gz` (nulls): `6c924a6250cdd9c0de55855625bf8ba971c95c776850005be6753c97f4c9ae44`
- `shard_0000_of_0004.jsonl.gz` (main): `45a9f4b4c5814a45e66a15098e53f6408a5d906c8cab63cea85ec36e8bf48980`
- `shard_0001_of_0004.jsonl.gz` (main): `83f8ea2e4db416e75919763ded19a0a939515648e8d5d591068ecd1514793be8`
- `shard_0002_of_0004.jsonl.gz` (main): `7c14ff648d8acc4a98a3907b4e27b71487607b5e5f2113d552fd252924a48906`
- `shard_0003_of_0004.jsonl.gz` (main): `1be0add8e43f085a223f033eca9b12a66dd896c55e6c86ca91e3ee504807b75a`
