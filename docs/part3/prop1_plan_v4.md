# Proposition-1 prediction test plan, protocol v4 (Task 3-3)

Status: written and committed **before** split 30 (pilot) or split 31
(scoring) is instantiated, and after the holdout run of Task 3-1. It implements
protocol v4 Section 13 (identical to v3 Section 13). It is a secondary
endpoint and changes nothing in the primary or other secondary endpoints.

## 1. A registration gap, closed here

Section 13 fixes the budgets, the ZNE estimator, the pilot estimators, and the
binary rule. It does **not** state the noise model under which Raw and ZNE are
compared. The comparison is meaningless without one: with no gate noise Raw is
always better, and under E2 local folding leaves the circuit unchanged
(`G G^dagger G = G`), so ZNE has nothing to extrapolate.

The project owner chose the following on 2026-11-17, after the holdout primary
and secondary results were known:

- **Noise:** E1, two-qubit depolarizing after every hard CX, at the locked main
  operating point `p = 0.04`, in all target and folded circuits; no readout
  error.

The holdout results do not involve ZNE or this estimator, but the choice was
made after they were seen and is disclosed as such. The predictions, this plan,
and the code are committed and registered on OSF together, before split 31 is
instantiated.

## 2. Interpretations of the registered text

1. **Graphs and candidates.** The 100 holdout graph identities (edges) are
   reused. K = 4 independent QAOA candidates per graph are drawn in the split-30
   namespace with the v4 candidate distributions (`gamma ~ U[0, 2 pi)`,
   `beta ~ U[0, pi)`) and no identity pairs. The same compiled candidate circuits
   are scored in split 31; split 31 changes only the shot seeds.
2. **Shot seeds.** For each graph, one generator per pilot block or scoring
   repeat:
   `SeedSequence([ROOT_SEED, split, 6, 1, 0, w, d, g, 0, repeat, 0])`. Within a
   block, Raw circuits are drawn first and ZNE circuits second, in candidate
   order and then scale order. Shot remainders go to earlier circuits.
3. **Anchor and attenuation.**
   - The anchor is the candidate with the largest mean ZNE intercept.
   - Gaps are anchor minus each other candidate (maximization), in candidate
     order.
   - The intervals that decide "unstable attenuation" are the Bonferroni
     intervals (0.05/6, two-sided) of the anchor-versus-candidate intercept
     gaps. They exclude zero exactly when the anchor is resolved.
4. **Bootstrap.** One set of 10,000 paired block resamples per graph, seed
   `SeedSequence([ROOT_SEED, 30, 7, 1, 0, w, d, g, 0, 0, 0])`, serves both the
   anchor intervals and the risk percentiles. Percentiles use `inverted_cdf`, as
   in Section 11.1.
5. **Orthant probabilities.**
   - Method: condition on one standardized gap, then integrate the exact
     bivariate normal CDF (Owen's T function) with Gauss-Legendre quadrature of
     orders 128 and 256 (384 integration points, within the 100,000 limit).
   - Convergence: the two orders agree within `max(1e-8, 1e-8 P)`.
   - Accuracy: on split-99 checks the orders agree to about 1e-14, and the
     bivariate CDF matches SciPy to 2e-16.
6. **Order of the diagnostic rules.** unresolved anchor → unstable attenuation
   → zero Raw variance (`uncertified_raw_default`) → non-convergence
   (`numerical_failure`) → `U_ZNE < L_Raw` (`zne_separated`, the only ZNE
   prediction) → `U_Raw < L_ZNE` (`raw_separated`) → otherwise
   `uncertified_raw_default`.
7. **Hit.** A method's error rate is the fraction of the 32 scoring repeats in
   which its selected candidate is not the ideal best. A non-unique sampled
   maximum is an error. If the ideal best is not unique (gap `<= 1e-12`), every
   selection is an error. A hit is a strictly lower error rate for the
   predicted method; an exact tie is a miss. The hit rate gets a 95% Wilson
   interval (z = 1.96) over the 100 graphs.

## 3. Order

1. Commit this plan and the code.
2. `pilot` (split 30) writes raw block counts.
3. `predict` writes `results/prop1/predictions.csv` and stops.
4. The owner commits the predictions and registers them on OSF. The record
   goes in `docs/freeze/registration_prop1_v4.json` (URL, timestamp, commit,
   predictions hash).
5. Only then `score` (split 31). It refuses without that record or if the
   predictions changed, and it writes a single-run marker.

## 4. Resources

Each graph is charged 1,310,720 shots: 32 x (4,096 + 4,096) in the pilot and
32 x (16,384 + 16,384) in scoring, which is 131,072,000 shots for 100 graphs.
On split 99 the largest graph (w8, p5) took about 11 s for the pilot and 3 s
for the prediction. The full pilot and prediction steps are expected to take
well under an hour in one process.
