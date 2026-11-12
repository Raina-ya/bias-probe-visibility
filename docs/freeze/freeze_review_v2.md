# Freeze review of protocol v2 (task 1d-3)

Status: pre-development review, 2026-11-12. No development or holdout seed was
instantiated. Evidence types are labelled per item. **Result: protocol v2 cannot
be locked as written.** Item 3 shows, before any data, that the primary endpoint
cannot reach its 0.80 success threshold. The project owner must choose a repair
(Section 3.4), after which a new protocol version is reviewed, committed, and
independently timestamped.

## 1. Line-ending hash mismatch (fixed)

Evidence type: software verification.

`artifact_registry_v1.yaml` held hashes of Windows CRLF working copies, while
`frozen_protocol_v2.sha256` and the matrix hash were LF hashes. Git stores LF,
so the provenance test failed on a clean Linux checkout (20 passed, 1 failed).

Fix:

- `.gitattributes` stores and checks out all text with LF on every platform;
- `src/hashing.py` hashes text artifacts after CRLF/CR-to-LF normalization and
  binary artifacts byte for byte; `provenance.py` and `protocol_contract.py` use
  it; and
- registry and `power_analysis_v4.md` hashes were recomputed.

Cross-platform finding: regenerating power v4 on Linux (Python 3.13.18,
NumPy 2.5.3) reproduced the Windows raw and summary files exactly after
line-ending normalization. No tolerance was changed and no check was removed.

## 2. Ceiling power result (wording fixed)

Evidence type: simulated design calculation.

All three power-v4 scenarios were 250/250. The Wilson bound 0.9849 describes
250/250, not the design. `power_analysis_v4.md` now names the informative
quantity, the minimum dataset-level bootstrap lower endpoint (0.8929 in
upper-boundary stress, margin +0.0929 over 0.80), and states that the scenarios
contain no near-failure operating point. Section 5 of the protocol repeats the
power value without this caveat and must be updated in the next version.

## 3. Unattainable readout operating points (blocking)

### 3.1 Analytic statement

Evidence type: analytic.

Every target state is QAOA-MaxCut: initial state \(|+\rangle^{\otimes w}\), cost
layers diagonal in the computational basis and invariant under the global flip
\(X^{\otimes w}\), and mixers \(\prod_q e^{-i\beta X_q}\) that commute with
\(X^{\otimes w}\). The candidate-1 `CX-CX` pairs are logical identities. Hence the
pre-readout distribution satisfies \(p(z)=p(\bar z)\) and
\(\langle Z_q\rangle=0\) for every qubit.

For a product readout channel with the same assignment rates
\(e_0=\Pr(1|0)\), \(e_1=\Pr(0|1)\) on every qubit, write
\(\tilde z_q=\lambda z_q+\delta\) in \(\pm1\) form with
\(\lambda=1-e_0-e_1\), \(\delta=e_1-e_0\). Then

\[
\langle\tilde Z_i\tilde Z_j\rangle
=\lambda^2\langle Z_iZ_j\rangle+\lambda\delta(\langle Z_i\rangle+\langle Z_j\rangle)+\delta^2
=\lambda^2\langle Z_iZ_j\rangle+\delta^2 .
\]

The normalized cut score is affine in the edge correlators, and the
\(\delta^2\) term is identical for both candidates, so the observed gap is
\(g_{\rm noisy}=\lambda^2 g\) and

\[
\beta/\Delta=-(1-\lambda^2)\in(-1,0] .
\]

A time-varying channel shared by all qubits (E6) is a mixture of such channels
and obeys the same bound. Therefore, for E4 and E6, the design ratios
\(q=-1.5\) and \(q=-1.0\) are unattainable on every graph, at every strength,
by construction. Uniform readout error of this kind can shrink a QAOA-MaxCut
decision gap but can never flip it.

### 3.2 Design check

Evidence type: noiseless simulation (exact statevectors and channels, no shots)
on the 50-graph `software_test` namespace (split 99), never development or
holdout seeds. Script: `experiments/design_checks/readout_ratio_check.py`; log:
`readout_ratio_log.txt`.

| Structure (strongest setting) | min | median | max | fraction \(\le-1\) |
|---|---:|---:|---:|---:|
| E4 `(0.08,0.12)` | -0.3600 | -0.3600 | -0.3600 | 0.00 |
| E5 `tau=+/-0.01`, worse sign per graph | -0.2938 | -0.1600 | 0.6747 | 0.00 |
| E5-prime `tau=+/-0.015625`, worse sign | -1.9237 | -0.5104 | 2.3714 | 0.02 |
| E6 worst endpoint of `delta=0.03` | -0.1900 | -0.1900 | -0.1900 | 0.00 |

The maximum \(|\langle Z_q\rangle|\) was \(1.9\times10^{-16}\), which confirms
the symmetry. E4 equals \(-(1-0.8^2)=-0.36\) exactly. The E5 and E5-prime rows use
this review's reading of Section 3 (flip patterns act only on the named pair or
triple and other qubits are error-free); that reading needs owner confirmation.

### 3.3 Consequence for the primary endpoint

Section 4 declares a structure-target point unattainable when the development
median is more than 0.25 from \(q\), and Section 11.1 counts unattainable cells
as disagreements. At the main point \(q=-1.5\):

- E4 and E6 (14 cells) are unattainable by theorem, so agreement is at most
  42/56 = 0.75 < 0.80 before any data;
- if E5 and E5-prime are also unattainable, as the design check indicates, the
  ceiling is 28/56 = 0.50.

The primary endpoint is therefore guaranteed to fail as specified. This is a
design defect discovered before the lock, not a result.

### 3.4 Repair options (owner decision)

None of these has been applied.

- **R1. Structure-specific operating points.** Keep \(q=-1.5\) for gate
  structures; for readout structures use design ratios inside the provably
  attainable range, chosen now from the analytic bound rather than from data.
  State the uniform-readout result as an analytic finding.
- **R2. Qubit-dependent readout rates.** Replace the shared rates in E4/E6 with
  a frozen per-qubit rate pattern. Unequal \(\lambda_i\lambda_j\) weights edges
  differently and can flip a decision. This needs a new design check and a new
  matrix review for every readout cell.
- **R3. Change the denominator.** Remove analytically unattainable cells from
  the primary denominator. This weakens the endpoint and contradicts the
  current deliberate choice to count them as disagreements, so it is listed
  only for completeness.

Before any version is locked, the same noiseless design check should cover
E1--E3. Their attainability was not checked here, because gate noise needs
density-matrix evolution. If a repair changes the denominator or class counts,
power analysis must be rerun.

## 4. Implementation interpretations needing approval

Each item is a reading of text the protocol leaves implicit. It is implemented
as stated and must be approved, or changed, before the lock.

1. Graph, family, and candidate seed keys use `structure_code=0` and
   `probe_code=0` as "not applicable".
2. After a disconnected draw, attempt \(r\) uses `repeat_index=r` in the
   graph-draw key.
3. Family assignment is one seeded permutation of the label multiset over the
   width-depth-index ordered graph list.
4. Graph generators are NumPy implementations, not a third-party library, to
   avoid an undeclared dependency whose random stream may change between
   versions. Section 2.1 says "the library generator" for Barabasi-Albert;
   this is a wording change.
5. E5-prime uses the lexicographically smallest vertex triple with a connected
   induced subgraph.
6. Split code 99 (`software_test`) is added for tests and design checks. Its
   outputs are never reported as results. Section 9 must list it.
7. Wilson intervals use \(z=1.96\), matching power v4.
8. The Proposition-1 pilot (split 30) requires the confirmatory lock, because it
   reuses holdout graph identities.
9. The E6 schedule in Section 7 does not fully determine target placement in
   blocks 1--6 or the meaning of "cycle identities ... followed by its
   reverse". The dry-run ledger therefore checks only non-temporal budget
   conservation. The schedule must be made explicit before the lock.
10. The certificate's "retained probe event probabilities" (Section 11.2) are
    not enumerated. `analysis.py` accepts any event list, and the list must be
    named before the lock.

## 5. Editorial corrections for the next protocol version

- Status paragraph: the file is committed (`7772591`) but not timestamped.
- Section 5: add the ceiling caveat from item 2.
- Section 7: `e_1(t)=0.06-\delta t,qquad` is missing a backslash.
- Section 9: add split 99.
- Section 10.1: name the files now provided (below).
- Section 17: hashes are LF-normalized; `Get-FileHash` matches only on an LF
  checkout, which `.gitattributes` now guarantees.

## 6. Pre-development code delivered

| File | Content |
|---|---|
| `src/hashing.py` | Line-ending-independent hashes |
| `src/split_guard.py` | Lock checks for splits 10/20/30/31; single-run markers |
| `src/manifest.py` | Graph and candidate manifests; refuses locked splits |
| `src/strength_map.py` | Section 4 strength map |
| `src/alarm_calibration.py` | Section 6.1 E0 thresholds, exact-rational rank |
| `src/analysis.py` | Section 8 labels; Section 11.1 endpoint with shared stratified bootstrap; Wilson; Section 11.2 certificate pieces |
| `experiments/dry_run/run_dry_run_v2.py` | Outcome-free budget ledger and Section 12 resource check |
| `experiments/design_checks/readout_ratio_check.py` | Item 3.2 |
| `tests/test_freeze_v2.py` | Tests for all of the above |

Probe implementations, channel constructors, and the noisy runner are Part 2
work and are not included.

## 7. Registration record

After the owner registers a locked version, the owner writes
`docs/freeze/registration_v2.json` (or the matching name for the new version):

```json
{
  "registry": "OSF",
  "url": "<registration URL>",
  "timestamp_utc": "<timestamp shown by the registry>",
  "commit": "<registered commit hash>",
  "files": {"<path>": "<LF-normalized SHA-256>", "...": "..."}
}
```

`split_guard.require_development_lock` refuses split 10 unless every file in
`PRE_DEVELOPMENT_FILES` is listed and unchanged.

## 8. Resolution adopted in protocol v3

Evidence type for the new rows: noiseless simulation (exact density matrices)
on the `software_test` namespace only. Script:
`experiments/design_checks/gate_ratio_check.py`; log: `gate_ratio_log.txt`.
`tests/test_design_checks.py` checks the simulator against the statevector
code and the analytic \(\lambda^2\) scaling.

The gate structures also miss the v2 target. At the strongest settings, the
development-style medians of \(\beta/\Delta\) were -0.7358 (E1, `p=0.04`),
-0.0912 (E2, `epsilon=-0.04`), and -0.0781 (E3, `zeta=-0.04`). The largest
fraction of graphs with \(\beta/\Delta\le-1\) was 0.12 (E2, `epsilon=-0.04`).
Repair R1 alone would therefore leave a primary-endpoint ceiling of 7/56.

Protocol v3 adopts **R1-prime**: every non-null structure is evaluated at its
largest frozen strength (main) and smallest frozen strength (sensitivity), with
the sign or orientation chosen by development medians and a deterministic tie
rule. Decision flips become a prespecified descriptive subset (v3 Section
11.4). Matrix labels, grids, budget, sample size, and the 56-cell denominator
are unchanged, so power v4 is not rerun. Items 4.1--4.10 and 5 are written into
v3 explicitly (v3 Section 18). The scientific consequence is stated plainly:
under the frozen grids, decision-flipping bias is rare, so the primary
visibility endpoint measures detection of differential bias, and detection of
actual flips can be described only on small subsets.
