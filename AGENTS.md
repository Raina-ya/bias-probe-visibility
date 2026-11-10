# Repository Contract

## Research question

Under a fixed total resource budget, can runtime bias probes detect a differential bias that
flips a decision, including when confidence-interval certification looks certain? For which
error structures is a probe effective and worth its cost, and for which is it blind in principle?

## Absolute limits

- Do not commit, push, force-push, or `reset --hard`. Give the commands; the user runs them.
- No machine learning. No hardware runs unless the user explicitly authorizes that specific run.
- Never invent citations, numbers, or results. Verify every citation (authors, venue, volume,
  DOI) online; anything unverified is marked "unverified" and stays out of the bibliography.
- Never change selection rules or thresholds after seeing holdout results.
- Never loosen tolerances or delete checks to make CI pass.
- Never delete raw data or failed runs.
- Never request, print, or write an IBM Quantum API key.

## Project rules

- Every cost is charged to one total budget: probes, calibration, folding, pilots, repeats.
  Classical post-processing time is reported separately.
- Rules, thresholds, data splits, and analytic predictions are frozen and committed before any
  noisy simulation. Use "preregistered" only with an independent OSF/AsPredicted timestamp;
  otherwise write "frozen and committed in this repository".
- Analytic predictions are frozen before simulation; simulation results never revise the theory.
  Mismatches are reported as failed predictions.
- A probe may not read ideal values of the target circuit. Every probe states its runtime cost
  in circuits and shots.
- Every claim that a probe works also reports the error structures where it fails.
- The holdout is read once. Failed, unresolved, and disqualified rows are all kept.
- Analytic, noiseless simulated, noisy simulated, device-parameter simulated (fake backend), and
  hardware evidence are labeled separately. Fake backends are not hardware evidence.
- Every manual threshold has a sensitivity analysis written into the frozen plan.

## Reproducibility

- Derive all stochastic seeds from one `ROOT_SEED`.
- Raw repeat-level rows are never overwritten; every summary is recomputable from raw rows.
- Keep an artifact registry with content hashes, and check automatically that each registered
  output is actually written by its registered generator.
- Run `provenance --write` as the last step after all generation, and ship the files whose hashes
  were written. Compare figures at pixel level; do not assume equal images have equal bytes.
- Run logs record numpy version and BLAS configuration (`np.show_config()`). Iterative solvers
  use fixed iteration counts and tolerances and record convergence. Every value-versus-threshold
  decision reports its distance from the threshold.
- Cross-platform differences are recorded as findings, never hidden by loosening tolerances.
- Format only new files with ruff; do not reformat the whole repository.

## Reporting

After each unit of work, report only: files created or changed; the experiment grid actually
run; test and verification results; supported main findings; negative or inconclusive findings;
remaining scientific concerns; whether the next unit can start; the commit hash if the user has
committed.

## Work log

After each task, add one entry at the top of `docs/WORKLOG.md` in the format given there. Keep only
the 20 most recent entries; move older ones, unchanged, to `docs/WORKLOG_archive.md`. Never delete
or edit anyone else's entries; moving to the archive is the only allowed change.
