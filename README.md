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

**No simulation results exist; nothing has been run on development or holdout data.**
Protocol v3 was registered on OSF (`j67wy`). A pre-data audit
([docs/freeze/pre_data_defect_audit_v3.md](docs/freeze/pre_data_defect_audit_v3.md)) then found
definition conflicts that made its primary endpoint uninterpretable. Protocol v4
([docs/freeze/frozen_protocol_v4.md](docs/freeze/frozen_protocol_v4.md)) repairs the design: a
decision-level primary endpoint, matched nulls, component-level P4 cells, and a 42-cell
stratified matrix. It is the current freeze candidate and must be committed and registered,
with its complete execution code, before any noisy simulation. v3 stays registered and
unchanged as the record.

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
