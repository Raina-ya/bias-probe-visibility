# Execution contract for Part 2 (Task 2-1)

Status: written 2026-11-12 after OSF registration `j67wy` of protocol v3
(commit `e8b5300`). Code and tests only: no development (split 10) or holdout
(split 20) row has been produced, and all tests use the software-test
namespace (split 99). The registered pre-development files are unchanged; the
development lock still passes.

The protocol is normative. This file lists every point where the code makes a
choice the protocol text does not fix. **The owner approves or changes each
item before Task 2-2.** These items implement the protocol and change none of
its rules. Approved items enter the confirmatory lock (Section 10.2).

## Modules

| File | Role |
|---|---|
| `src/circuits.py` | Qiskit compilation (Section 2.4), identity pairs, folding, Clifford twin, Pauli frames, preparations |
| `src/simulate.py` | Exact pre-readout probabilities; E1/E3 hooks after every hard CX |
| `src/channels.py` | Structure settings and readout channels (Section 3) |
| `src/probes.py` | Probe statistics from counts only (Section 6.2) |
| `src/execution.py` | Circuit lists, allocation, E6 schedule, seeded multinomial draws, raw rows |
| `src/reference.py` | Ideal and noisy population gaps for the strength map and scoring only |
| `src/runner.py` | CLI; split guard, clean-commit check, exclusive output files |
| `tests/test_execution.py` | Task 2-1 acceptance tests |

## Acceptance criteria and their tests

- **Total cost exactly 16,384 shots:**
  `BudgetTests.test_every_probe_structure_fraction_charges_exactly_16384` runs
  every primary probe plus P1b, every structure including E6, and all three
  probe fractions. It checks allocated shots, scheduled shots, and drawn
  counts.
- **No target ideal value reaches a probe:** `NoIdealValueTests` inspects the
  probe-function signatures, checks that `probes.py` and `execution.py` never
  import `reference.py`, and checks that a raw row contains no ideal value.
- **Same seed, same row:** `ReproducibilityTests`, including E6.
- **Locked splits refused:** `LockTests`. Holdout is refused. Development is
  refused without registration, at the wrong commit, and without
  `--previous-project-closed`. The split-99 runner refuses to overwrite.

## Interpretations requiring approval

1. **QAOA layer:** `H` on every qubit; each layer applies `RZZ(gamma)` on every
   edge in lexicographic order, a barrier, then `RX(2*beta)` on every qubit.
2. **E2** scales the logical `RZZ` angle before transpilation.
3. **E3** applies `RZZ(zeta)` on the hard gate's own pair after every CX (in
   E3.1 terms, \(h_{\ell r}=1\) on the active pair and 0 elsewhere). This
   includes identity-pair and folded CX gates.
4. **E1** applies two-qubit depolarizing noise after every CX, including
   identity pairs, folded gates, and framed circuits.
5. **P1 folding** replaces every non-barrier gate \(G\) by
   \(G G^\dagger G\). \(\sqrt{X}^\dagger\) is simulated directly; it is not a
   hardware basis gate.
6. **P2 twin** rounds every `rz` angle to the nearest multiple of \(\pi/2\),
   with exact half ties toward the smaller angle. The twin reference gap is
   the twin circuits' own noiseless value, not a target value.
7. **P3 frames** use Sylvester-Hadamard columns 1..w of the order-16 matrix.
   Each version applies a static X frame around every CX with the conjugated
   correction after it. Row 0 is the identity frame, so version 0 equals the
   plain circuit.
8. **P4a/P4b preparations** contain only X gates, so E1--E3 do not act on them
   and only readout does. In a P4b pair preparation the other qubits are in 0.
9. **P1b** uses the W_neg maximum over the two candidates.
10. **E6:** the P1/P2/P3 permutation key uses `artifact_code=4`,
    `structure_code=6`, and `candidate_index=0`. Statistics other than P5 use
    counts pooled over blocks; P5 adds half-scores as Section 6.2 specifies.
11. **Shot draws:** one `SeedSequence` per row (`artifact_code=6`,
    `candidate_index=0`), spawned into one child per schedule entry in
    canonical order. The row stores the key.
12. **`seed_transpiler`** is the first 32-bit word of the `SeedSequence` with
    `artifact_code=4`, `structure_code=0`, `probe_code=0`, and the candidate
    index.
13. **Reference E6 population gap** uses the rates at \(t=0.5\). By Section 4.1
    the E6 ratio does not depend on \(\delta\).
14. **GVS** is not implemented. Its \(L_{\mathcal C}\) and \(K\) must first be
    fixed from Scavino v1. It is exploratory and first in the scope-cut order.
15. **Dependencies:** Qiskit (tests run with 2.2.3), NumPy, and SciPy. The
    versions used are recorded in every development run log.

## Not yet done (Tasks 2-2 and 2-3)

- **Development runs:** no development batch driver or run log has been
  executed. Split 10 requires an owner-confirmed closure of the previous
  project (plan, Section 14).
- **Timing:** P3/E1 at width 8, depth 5 took about 19 s per row in this
  environment, mostly density-matrix solves. The 1% timing pilot (Task 2-3)
  decides whether the 14-day cap holds.
- **Second-lock artifacts:** `strength_map_v3.csv`, `thresholds_v3.md`,
  `dev_mismatch_v3.md`, the timing pilot, the implementation-error log, and
  `confirmatory_lock_v3.json` are not yet produced.
