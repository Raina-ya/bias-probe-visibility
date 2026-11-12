# Power analysis v4: repaired shared-graph endpoint

Status: task 1d-2R design revalidation completed on 2026-11-12 after the
repaired matrix was committed as `c839b95`. This is a simulated design
calculation. It is not noisy-circuit, device-parameter, or hardware evidence and
does not show that any physical probe works.

## Preconditions

- Matrix: `docs/theory/06_matrix.csv`
- Matrix SHA-256:
  `7a8e3a56e6f48d8a29c3643c1c2e24f46bce6a54c674d6b1937dbdcd041d8995`
- Primary labels: 35 blind, 15 partial, 6 visible
- Design under revalidation: 100 graph clusters, 32 repeats per graph
- Width-depth strata: 25, with four graphs in every stratum
- Root seed: `20261111`
- Dataset simulations per scenario: 250
- Stratified shared-graph bootstrap resamples per dataset: 1,000

Unlike v1--v3, every bootstrap replicate reuses one set of resampled graph
indices across all 56 cells. This preserves the dependence created by using the
same graph manifest across probes and structures. The design model also adds a
shared graph-difficulty component with scale 0.20 and a cell-specific graph
component with scale 0.30. These are prespecified stress assumptions, not
estimates from quantum data.

## Results

| Scenario | Design successes / 250 | Estimated design power | 95% Wilson interval | Target | Lower-bound margin |
|---|---:|---:|---:|---:|---:|
| Baseline | 250 | 1.0000 | [0.9849, 1.0000] | 0.90 | +0.0849 |
| Lower-boundary stress | 250 | 1.0000 | [0.9849, 1.0000] | 0.80 | +0.1849 |
| Upper-boundary stress | 250 | 1.0000 | [0.9849, 1.0000] | 0.80 | +0.1849 |

Across the 250 simulated datasets, the minimum dataset-level primary bootstrap
lower endpoint was 1.0000 in baseline, 0.9464 in lower-boundary stress, and
0.8929 in upper-boundary stress. All remained above the frozen 0.80 endpoint.

The retained design is therefore 100 graph clusters and 32 repeats per graph.
This conclusion means only that the endpoint can be estimated stably under the
declared operating scenarios. The assumed class means already encode whether a
cell is near a classification boundary; the result cannot validate those means
or the physical visibility predictions.

**How to read the 1.0000 power.** Every scenario reached the ceiling (250/250),
so the design-power column cannot show how close the design is to failing; a
Wilson lower bound of 0.9849 is a property of 250/250, not of the design. The
informative quantity is the minimum dataset-level bootstrap lower endpoint:
0.8929 in upper-boundary stress, a margin of +0.0929 above the frozen 0.80
endpoint. A ceiling result also means the scenarios did not include an
operating point near failure; this analysis therefore provides no evidence
about designs that are less favourable than the three declared scenarios,
including unattainable operating points (see `freeze_review_v2.md`). Any text
that cites this analysis must report the minimum lower endpoint and this
ceiling caveat, not the power value alone.

## Artifacts

| Artifact | SHA-256 (LF-normalized, `src/hashing.py`) |
|---|---|
| `experiments/power/power_analysis_raw_v4.csv` | `457c095bd811d492647b846b4bda95842e16d77f5a2961c249bba0fd1da2f8f9` |
| `experiments/power/power_analysis_summary_v4.csv` | `dcf47ddfd2e6b0847e74a2d74b28f474192538387c771b4661b9820c711fd715` |
| `experiments/power/run_log_v4.txt` | `096bee823243be6a6707050c782a9b856e34c529c63faecc0429140354c0d6df` |

The hashes originally listed here were computed on Windows CRLF working copies
(`b61b86c9...`, `df957093...`, `74901ee6...`), while Git stores LF text, so a
clean Linux checkout failed the provenance check. Hashes are now computed on
LF-normalized text. Regenerating power v4 on Linux (Python 3.13, NumPy 2.5.3)
reproduced the raw and summary files exactly after line-ending normalization,
so the original mismatch was a line-ending convention only.

The raw file has 750 rows: 250 datasets for each of three scenarios. The
summary is independently recomputed by
`experiments/power/summarize_power_v4.py`. Historical v1--v3 outputs remain
unchanged as local audit data but are excluded from Git because the three
superseded raw files total about 153 MB. Only the current v4 outputs are in the
artifact registry.

## Remaining boundary

Power v4 closes the sample-design inconsistency but does not authorize noisy
development. The repair has been merged into `frozen_protocol_v2.md`, which is
still a freeze candidate awaiting owner review, commit, and an independent
timestamp. No development or holdout seed has been instantiated.
