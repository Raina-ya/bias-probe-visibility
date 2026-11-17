# Third-party blind recomputation brief

Purpose: satisfy specification item 24 by having a person outside the project
independently recompute three headline quantities from the frozen protocol and
immutable raw rows. This is a recomputation, not a new simulation run.

## Package prepared by the project owner

Give the reviewer only the following files in a separate directory. Preserve
their repository-relative paths.

- `docs/freeze/frozen_protocol_v4.md`
- `docs/part3/prop1_plan_v4.md`
- `docs/freeze/confirmatory_lock_v4.json`
- `docs/freeze/registration_prop1_v4.json`
- `results/development_v4/thresholds_v4.csv`
- `results/holdout_v4/reference/holdout_reference_v4.csv`
- all four `results/holdout_v4/main/shard_*.jsonl.gz` files
- `results/prop1/predictions.csv`
- `results/prop1/scoring/scoring_raw_v4.jsonl.gz`
- this brief

The owner verifies the eight data-file hashes before transfer:

| File | SHA-256 |
|---|---|
| `main/shard_0000_of_0004.jsonl.gz` | `0d0c83b13a3196b9bb7bf52beddb0b7fd60d768869b2276b1c285d8909fd5e83` |
| `main/shard_0001_of_0004.jsonl.gz` | `9036593f7b8c908eb62ca289285592e50e28e55101661ca6d024b27514629411` |
| `main/shard_0002_of_0004.jsonl.gz` | `73228f854024a7174cbce348618e13a9eac7d2c6e8c995e9d126e16052820bc5` |
| `main/shard_0003_of_0004.jsonl.gz` | `6b99c311e98742489e69d238bc424f4ae730bf7ec8c2f9a588b504241078eb7c` |
| `holdout_reference_v4.csv` | `7af4eaadab1fc0041927ce3f08c9685311acfb13cea18e4bfac4fd0881fc021a` |
| `thresholds_v4.csv` | `567e522e80db508c30bec95a831670babae4701818da1b4dabd8668a3aeea0dd` |
| `predictions.csv` | `2a6007c7b08fe38fe1a3067eaee083dd040d508a46678250270586ce31e74a12` |
| `scoring_raw_v4.jsonl.gz` | `9010c29991ec886ab714a7c8a20bd91eaf607056e4fe4853fed756f58289b896` |

Do **not** include `README.md`, `.zenodo.json`, `paper/`, `docs/results/`,
`results/holdout_v4/primary_endpoint_v4.json`,
`results/prop1/prop1_scoring_v4.json`, or any project scoring script. They
contain the answer or the implementation being checked. Because the public
repository already contains answers, ask the reviewer not to open the GitHub,
Zenodo, or OSF result pages until the signed report is returned. This is a
procedural blind, not a technically sealed blind.

## Reviewer instructions

Use an independently written analysis. Do not run the simulator and do not use
the project's scorers. Implement the definitions in protocol v4 Sections 2,
8, and 11.1--11.2, and the Proposition-1 plan Sections 2.5--2.7.

Recompute exactly these three quantities:

1. `dFC`: the seven-structure pooled change
   `mean_s[FC_s(R0) - FC_s(R1)]` on the main holdout rows.
2. `coverage_loss_pooled`: the seven-structure pooled change
   `mean_s[C_s(R0) - C_s(R1)]` on those same rows.
3. `prop1_hits`: among the 100 registered predictions, the count for which the
   predicted method has a strictly lower empirical top-1 error rate across the
   32 scoring repeats. Exact error-rate ties are misses.

For Proposition 1, recompute Raw candidate scores from `raw_c*`; recompute ZNE
candidate scores from scales 1, 3, and 5 using the registered intercept weights
`(13/12, 1/3, -5/12)`; apply the registered tie and ideal-tie rules. Derive the
graph edges from the frozen manifest specification rather than consulting a
project result file. Record any numerical decision within `1e-10` of a tie.

Save the independent implementation as `reviewer_recompute.py`; a suggested
run contract is:

```text
python reviewer_recompute.py --package BLIND_PACKAGE --output blind_recompute_report.json
```

The output has fields `dFC`, `coverage_loss_pooled`, `prop1_hits`,
`input_sha256`, `environment`, `reviewer_code_sha256`, and `notes`. This brief
deliberately provides no expected values.

Return a signed, dated JSON or plain-text report containing the three values,
the reviewer's code hash, environment, input hashes, and any ambiguity. Do not
ask the project owner for the expected values until the report is frozen. The
owner then compares the report with the excluded answer files and records every
disagreement without changing tolerances or raw data.
