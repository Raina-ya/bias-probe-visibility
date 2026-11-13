# Execution contract for Part 2 under protocol v4

Status: 2026-11-12. Supersedes `execution_contract_v3.md` (kept for audit).
Unlike v3, this code is registered together with protocol v4, so every item
below is reviewed and frozen at registration. Tests use split 99 only. No
development or holdout row exists.

## Changes from the v3 execution contract

1. **E2** is applied at execution time to every tagged cost rotation (`rzc`)
   in target, folded, twin, and framed circuits (`circuits.py`, `simulate.py`).
   For targets this is identical to scaling the logical `RZZ` angle (tested).
2. **P4 components:** P4a records `assignment`; P4b records `t_marg` and
   `t_corr`; under E6 both also record `temporal_contrast` between blocks 0 and
   7. The cell-to-component mapping is in `cells_v4.py`.
3. **Matched nulls** are the zero-strength settings in
   `cells_v4.MATCHED_NULL`; clean E0 calibrates the decision endpoints.
4. **Population mode** (`run_row(..., population=True)`) replaces counts by
   expected values. It is used only by split-99 semantic tests.
5. **Locks:** the runner uses `split_guard_v4` and `manifest_v4`. Split 10
   needs `registration_v4.json`. The v3 lock files are unchanged.
6. **Analysis:** `analysis_v4.py` implements the primary decision estimand
   with its three-way outcome, interception, and stratified visibility
   agreement.

## Interpretations retained from v3 (frozen at v4 registration)

- **QAOA layer:** `H`, then per layer `RZZ(gamma)` on every edge in
  lexicographic order, a barrier, and `RX(2*beta)` on every qubit.
- **E3:** `RZZ(zeta)` on the pair of every hard CX, immediately after it.
- **E1:** two-qubit depolarizing noise after every CX.
- **P1 folding:** every non-barrier gate `G` becomes `G G^dag G`.
- **P2 twin:** each `rz`/`rzc` angle is rounded to the nearest multiple of
  pi/2, with exact half ties toward the smaller angle. The twin reference is
  the twin's own noiseless gap.
- **P3 frames:** static X frames around every CX, from Sylvester-Hadamard
  columns 1..w; row 0 is the identity frame. Frames do not twirl the
  non-Clifford cost rotations (this is why P3/E2 is invariant).
- **P4 preparations** contain only X gates.
- **P1b** uses the maximum over candidates.
- **E6 permutation key and shot spawning** are as in v3.
- **GVS** is not implemented; it is exploratory.
- **Dependencies:** Qiskit (tested with 2.2.3), NumPy, and SciPy.
