# Primary endpoint, protocol v4 holdout (Task 3-1)

Evidence type: noisy simulation, holdout split 20, read once. Rule:
protocol v4 Section 11.1, thresholds and operating points from the
confirmatory lock (OSF j597k). Recomputable from the raw rows with
`experiments/holdout/score_primary_v4.py`.

Graphs: 100; repeats: 32; ideal ties: 0; failed units: 0.

**Outcome: improvement.**

| Quantity | Value | Threshold | Value - threshold |
|---|---:|---:|---:|
| dFC (point) | +0.008036 | | |
| dFC 2.5th percentile | +0.002857 | 0 (improvement if >) | +0.002857 |
| dFC 97.5th percentile | +0.014152 | | |
| Pooled FC(R0) | 0.010313 | | |
| Pooled FC(R0) 97.5th percentile | 0.017946 | 0.01 (no problem if <) | +0.007946 |
| Pooled coverage loss C(R0)-C(R1) | +0.417679 | | |

No-problem bound sensitivity (Section 8; never replaces the main outcome): 0.005: improvement, 0.02: improvement.

## Per structure (main operating point)

| Structure | Probe | FC(R0) | FC(R1) | C(R0) | C(R1) | R0 false certs | R0 false-cert graphs | Interception (units) |
|---|---|---:|---:|---:|---:|---:|---:|---|
| E1 | P1 | 0.000000 | 0.000000 | 0.2978 | 0.0147 | 0 | 0 | insufficient (0) |
| E2 | P2 | 0.060937 | 0.015938 | 0.6025 | 0.3000 | 195 | 7 | 0.744 (195) |
| E3 | P3 | 0.011250 | 0.000000 | 0.5747 | 0.3109 | 36 | 2 | 1.000 (36) |
| E4 | P4a | 0.000000 | 0.000000 | 0.4906 | 0.0000 | 0 | 0 | insufficient (0) |
| E5 | P4a | 0.000000 | 0.000000 | 0.5778 | 0.0000 | 0 | 0 | insufficient (0) |
| E5' | P4a | 0.000000 | 0.000000 | 0.4409 | 0.0000 | 0 | 0 | insufficient (0) |
| E6 | P4a | 0.000000 | 0.000000 | 0.5650 | 0.0000 | 0 | 0 | insufficient (0) |

## Secondary: structure-agnostic variant (P2 for every structure)

Outcome improvement; dFC +0.006652 [+0.002054, +0.011786]; coverage loss +0.141830. Secondary endpoint.

Machine-readable result: `primary_endpoint_v4.json`.
