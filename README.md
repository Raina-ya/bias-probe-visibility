# Bias Probe Visibility

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

**Planning stage. There are no results in this repository.** The research plan is a draft and
has not been frozen. Nothing here has an independent timestamp yet; when the analytic
predictions and the protocol are frozen, they will be committed here and registered on OSF or
AsPredicted before any noisy simulation is run.

- Plan: [docs/project_plan_v0.md](docs/project_plan_v0.md) (in Chinese)
- Literature review and research anchors: [docs/literature_review.md](docs/literature_review.md)
  (in Chinese); library with verification status and notes:
  [docs/literature/library.csv](docs/literature/library.csv); verified bibliography (Zotero-importable):
  [paper/references.bib](paper/references.bib). Full texts have not been read yet; notes are based on
  abstracts or are marked as unconfirmed.
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
