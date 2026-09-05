# SWaT External Validation Protocol

The Secure Water Treatment (SWaT) A1/A2 benchmark is used only to validate the measurable detector-to-authority link:

```text
process telemetry -> anomaly score -> D(phi) -> R_CI -> provisional authority
```

It does not provide organization-specific evidence for `E`, `F`, `G_FA` or `G_H`, and it does not validate the full RDFR-CI framework.

## Pre-specified design

- Train on the first 80% of the normal period chronologically.
- Use the remaining 20% of the normal period for FPR calibration.
- Evaluate attacks at the episode/scenario level; avoid leaking correlated windows from the same attack across calibration and test partitions.
- Primary temporal window: 60 s; sensitivity: 30 s and 120 s.
- Primary detector: Isolation Forest.
- Secondary detector: reconstruction autoencoder.
- FPR budgets: 0.01, 0.05, 0.10.
- Primary metrics: ROC-AUC, PR-AUC, precision, recall, F1, event detection rate, median time-to-detection and false alarms/hour.
- Primary reporting does not use point adjustment.
- Water showcase context is held at `E=0.55`, `A=0.30`, `F=0.25`, `C=0.90`; only `D` is replaced by a measured value.
- Therefore `R_CI(tau) = 0.430 + 0.20*D(tau)` under default weights.
- Bootstrap 10,000 attack episodes where feasible to estimate `P(authority state)`.

## Pre-specified hypotheses

- **H1:** the threshold maximizing global F1 differs from the threshold minimizing criticality-weighted `D` under an operational FPR budget.
- **H2:** a statistically modest threshold change may materially change the RDFR-CI boundary margin or provisional authority state.
- **H3:** attack-episode bootstrap reveals non-negligible uncertainty in `P(authority state)` when `R_CI` lies near a band boundary.

## Data boundary

Raw SWaT files are not included in the repository. See `data/README_SWAT.md`. The runner exits without generating empirical metrics if authorized data are absent.
