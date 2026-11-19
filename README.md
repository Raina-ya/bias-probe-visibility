# Bias Probe Visibility

[![Software DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24360452.svg)](https://doi.org/10.5281/zenodo.24360452)

Raw shot-level data: [10.5281/zenodo.24300969](https://doi.org/10.5281/zenodo.24300969)

When can a runtime bias probe tell that a quantum error-mitigated decision is wrong?

Confidence-interval certification controls sampling error only. A decision can be certified
with high confidence and still be wrong, because a differential bias between candidates
shifts the decisive gap, and more shots only make the wrong answer more certain. Detecting
such bias needs extra evidence that is paid for out of the same total budget. This project
maps which probes can see decision-flipping bias, under which error structures, at what cost,
and where a probe is blind in principle.

This is the follow-up to
[adaptive-qem-benchmark](https://github.com/Raina-ya/adaptive-qem-benchmark), which asked when
QEM is unreliable. This project asks whether that unreliability can be detected at runtime.

## Status

**Complete.** All four parts have been run under protocol v4, each confirmatory analysis once.
Evidence type for every decision-level result: noisy simulation. One exploratory readout test
was run on hardware after release v1.0 (below).

- Primary endpoint (holdout, 100 graphs, read once): the runtime probe rule reduced the
  CI-only false-certification rate, dFC = +0.0080 (95% graph-cluster bootstrap
  [+0.0029, +0.0142]), at a pooled coverage loss of 0.418.
  [docs/results/primary_endpoint_v4.md](docs/results/primary_endpoint_v4.md)
- Proposition-1 prediction test (predictions registered before scoring, OSF `abuct`):
  45/100 hits, 95% Wilson [0.356, 0.548].
  [docs/results/prop1_prediction_test_v4.md](docs/results/prop1_prediction_test_v4.md)
- Secondary endpoints, boundary synthesis and failure causes:
  [docs/results/](docs/results/)
- Hardware go/no-go review at the end of the study: NO-GO, no job submitted.
  [docs/hardware/review_v1.md](docs/hardware/review_v1.md)
- Hardware addendum (exploratory, registered after v1.0 at OSF `wh5rs` with its execution
  package): one run on `ibm_marrakesh` on 2026-11-19, 51 reported QPU seconds. The registered
  prediction held: no qubit pair's readout correlation came near the level at which tensored
  readout mitigation is worse than none (0 of 56 tests rejected).
  [docs/results/hardware_readout_v1.md](docs/results/hardware_readout_v1.md),
  [docs/hardware/amendment_readout_v1.md](docs/hardware/amendment_readout_v1.md)
- Paper: [paper/main_v4.pdf](paper/main_v4.pdf). Every result number in it is generated
  from the committed result files (`paper/numbers_v4.tex`).

Registrations on OSF (project `y7m29`): protocol v3 `j67wy` (superseded by a pre-data audit,
kept unchanged as the record), protocol v4 `r63vn`, confirmatory lock `j597k`, Proposition-1
predictions `abuct`. Disclosed deviations are listed in the paper and in
[docs/freeze/](docs/freeze/).

The immutable `abuct` registration was created without file attachments. Copies of
`predictions.csv` and `prop1_plan_v4.md` were later added to the OSF project `y7m29` Files;
their SHA-256 hashes match the values recorded in
[registration_prop1_v4.json](docs/freeze/registration_prop1_v4.json). They are project-file
copies, not retroactive attachments to the registration.

The large raw shot-level files (`*.jsonl.gz`) are not in git; their SHA-256 hashes are in the
committed result JSONs and run markers.

### Verification boundary

All verification to date is internal to the project; no third party has yet performed the
blind recomputation described in
[third_party_blind_recompute_v1.md](docs/reproducibility/third_party_blind_recompute_v1.md).
The primary endpoint was reproduced byte-identically with the frozen scorer on Windows and
Linux and was also recomputed through a separate code path. The secondary endpoints were
reproduced byte-identically on both platforms with the same scorer. Proposition-1 predictions
and hits were recomputed through separate project code. The boundary map is a deterministic
synthesis of committed results, not a separate confirmatory data run.

- Plan: [docs/project_plan_v0.md](docs/project_plan_v0.md) (in Chinese)
- Literature review and research anchors: [docs/literature_review.md](docs/literature_review.md)
  (in Chinese); library with verification status and notes:
  [docs/literature/library.csv](docs/literature/library.csv); verified bibliography (Zotero-importable):
  [paper/references.bib](paper/references.bib). Reading depth is recorded per entry in
  library.csv.
- Contributor rules: [AGENTS.md](AGENTS.md)

## Scope

The project has four parts, fixed in advance:

1. Theory and freeze: definitions, indistinguishability and symmetry criteria for probe
   blindness, a fixed-budget condition for when a probe pays off, and a frozen
   error-structure by probe prediction matrix. Analytic only.
2. Probe implementation and development set (noisy simulation, development data only).
3. Confirmatory holdout, read once.
4. Boundary synthesis, hardware go/no-go review, and paper.

Success means drawing the boundary between "the probe can see it" and "it cannot". If every
probe fails, explaining why it cannot see counts as a result.

## Evidence types

Analytic, noiseless simulation, noisy simulation, device-parameter simulation (Qiskit fake
backends), and hardware are always labeled separately. Fake-backend results are simulations,
not hardware evidence. No machine learning is used.

## License

Code and tests: MIT ([LICENSE](LICENSE)). Paper, documentation, figures, configurations and
results: CC BY 4.0 ([LICENSE-CC-BY-4.0.md](LICENSE-CC-BY-4.0.md)).
