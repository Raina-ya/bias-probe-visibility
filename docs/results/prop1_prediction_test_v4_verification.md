# Verification and breakdown of the Proposition-1 prediction test (Task 3-3)

Evidence type: recomputation of a noisy-simulation result (E1 depolarizing,
p = 0.04) from immutable raw counts. Secondary endpoint. Nothing here changes
the registered hit rate.

## 1. Order of operations

| Step | Commit / record | Time (UTC) |
|---|---|---|
| Plan, code, tests committed before split 30 | `bd3e29a` | 2026-11-17 |
| Pilot (split 30), predictions written | run log, pilot SHA-256 `57de9af6...` | 2026-11-17 |
| Predictions committed | `1e8396f` | 2026-11-17 |
| Predictions registered | OSF `abuct` | 2026-11-17 03:19:45 |
| Registration recorded | `0956527` | 2026-11-17 |
| Scoring (split 31), single-run marker | marker at `0956527` | 2026-11-17 03:35--03:44 |

The scorer refused to run without `docs/freeze/registration_prop1_v4.json`
and checked the predictions hash against it.

## 2. Recomputation

- **Predictions.** On Linux, the predictions were recomputed from the pilot raw
  counts. The prediction, diagnostic reason, and anchor match for all 100
  graphs. Risk percentiles differ by 1.1e-16 in 20 graphs. In 9 graphs both
  risks are 0 within rounding, and these are Raw ties under the rule. This was
  disclosed in the OSF registration.
- **Hits.** Separate code recomputed the hits from the scoring raw counts
  (`scoring_raw_v4.jsonl.gz`, SHA-256 `9010c299...`): 45 hits, 47 ties, and
  8 graphs where ZNE was better. These are identical to the scorer. No repeat
  violates the 16,384 + 16,384 shot budget. The result JSON matches the
  single-run marker (SHA-256 `70c7361b...`).

## 3. Breakdown (descriptive)

Every prediction was Raw. The 100 graphs split as follows:

| Diagnostic reason | Graphs | Hit (Raw strictly better) | Tie (miss) | ZNE strictly better (miss) |
|---|---:|---:|---:|---:|
| raw_separated | 22 | 5 | 17 | 0 |
| uncertified_raw_default | 46 | 19 | 27 | 0 |
| unresolved_anchor | 32 | 21 | 3 | 8 |
| **Total** | 100 | **45** | **47** | **8** |

- **Ties (47).** In 42 graphs both methods had zero top-1 errors in all 32
  repeats. In 1 graph both erred in every repeat. In 4 graphs the error rates
  were equal but nonzero. The registered rule counts every tie as a miss.
- **Directional errors (8).** All 8 come from `unresolved_anchor`, the graphs
  where the pilot could not identify the best candidate and the rule defaulted
  to Raw without certification. Where the pilot certified a Raw advantage
  (`raw_separated`) or found overlapping risks, ZNE was never strictly better.
- **Mean top-1 error over all graphs:** Raw 0.145, ZNE 0.188.
- **Among the 53 graphs without a tie,** Raw was strictly better in 45
  (0.849). This is a descriptive figure, not the registered endpoint.

## 4. Limits

- With no ZNE prediction, the test cannot evaluate the rule's ability to
  identify ZNE-favourable graphs. It tests only whether Raw is strictly better
  when Raw is predicted.
- The noise model was fixed after the holdout results were known, as
  disclosed.
- The recomputation was done within the project. No third-party blind check
  has been made.
