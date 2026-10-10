# Note on `experiments/run_revision_analyses.py`

## Provenance

The manuscript says that `experiments/run_revision_analyses.py` "regenerates Tables 10, 15, 17, and A1, the interval columns of Tables 11 and 12, and Figures 4–6 with fixed seeds from the archived scenario catalog and the reported A11 aggregates". That script was part of release v1.4.0. The v1.4.0 file was not available, so release v1.4.1 contains a **re-implementation** that was written from the manuscript's description of the method:

- Section 3.13 (end): Wilson and Clopper–Pearson interval bases.
- Section 3.14: robustness, policy-variant and 24-parameterization design.
- Section 3.16: the alternative decision methods.

The policy logic comes from `rdfr_ci`:

- Equation (1) score and Equation (2) weights.
- Table 5 UNKNOWN gate caps via `gates.final_authority`.
- Table 6 half-open bands.

The input is `scenarios/scenario_catalog.yaml`, which holds 30 scenarios. Thirteen of them have at least one unresolved gate.

The raw SWaT A11 data are restricted, so the A11 interval columns are recomputed from the aggregates reported in Tables 11 and 12. These aggregates are hard-coded in `REPORTED_A11_AGGREGATES`.

## How to run

```
PYTHONPATH=src python3 experiments/run_revision_analyses.py \
    [--out-dir results/revision_analyses] [--seed 42] [--n-mc 10000] [--no-figures]
PYTHONPATH=src python3 -m pytest -q tests/test_revision_analyses.py
```

The script runs in about 3 s. It writes the following CSV files to `--out-dir`:

- `table_10*`
- `table_15*`
- `table_17*`
- `table_A1`
- `table_11_intervals`
- `table_12_intervals`
- `scenario_points`

It also writes `summary.json` and Figures 4, 5 and 6 as PNG and PDF files.

## Conventions used

- A gate marked `fail` or `unknown` in the catalog gets the Table 5 UNKNOWN cap. All other gates are PASS. The final level is min(provisional level, gate cap).
- Bands are half-open, as in Table 6. Before scores are compared with boundaries, both are rounded to 1e-10. This prevents floating-point noise when a score lies exactly on a boundary or a shifted boundary, for example WATER-001 at RCI = 0.5000.
- **Joint Monte Carlo.** Each scenario `i` uses `numpy.random.default_rng(seed + i)`. In this order, the script draws:
  1. N(x, 0.05) noise on the inputs, clipped to [0, 1];
  2. Dirichlet weights with alpha = 120·w (Equation (2));
  3. a common boundary shift drawn from U(−0.025, 0.025).
- **Inputs-only retention.** This uses `rdfr_ci.uncertainty.simulate_state_distribution` with seed `seed + i`, as in `run_scenario_analysis.py`.
- **Fixed playbook.** Reversibility maps to levels as follows: high → 4, medium → 3, low → 2.
- **Gates-only policy.** Starts at level 4 and then applies the gate cap.
- **Restriction.** Defined as 4 minus the level. ρ is the Spearman correlation and κ is the quadratic-weighted κ (scikit-learn).
- **AI-SOC-style score.** Uses the E, D, A, F weights divided by 0.75. The original weights (0.30, 0.30, 0.20, 0.20) are a sensitivity row.
- **5 × 5 risk matrix.** Uses classes ⌊5x⌋, capped at 4. The class sum maps to levels as follows: 0–2 → 4, 3–4 → 3, 5 → 2, 6–7 → 1, 8 → 0.
- **Worst-dimension rule.** Assigns the Table 6 band of max(E, D, A, F, C).
- Gates are applied to every method. The water-context column of Table 17 is computed before gates are applied.
- **Table A1 weights.** For wC = 0.35, wC = 0.15, wD = 0.30 and wF = 0.10, the other weights are rescaled proportionally. C* = b1 / wC.
- **Wilson intervals.** These use the reported target flag rate as p̂, with n = 5821 for the nominal basis and n_eff = 485 for the block basis.

## Comparison with the manuscript (seed 42, n = 10,000)

**Exact matches.** All of the following deterministic quantities match the manuscript exactly:

- **Table 10, deterministic rows.** 13/8, 5/2, 3/1 and 7/2. The largest single-boundary shift gives 3/1 at ±0.025 and 6/3 at ±0.05.
- **Table 15, every entry:**
  - Gate-unresolved eligibility: 12, 6, 0 and 0.
  - Level above provisional: 24, 0, 16 and 0.
  - Level-4 assignments with C ≥ 0.5: 6, 0, 12 and 0.
  - Spearman ρ: −0.01, 0.94, −0.25 and 0.71.
  - Level distributions: as reported.
  - Score-only eligible IDs: MFG-001, SUB-001, WW-001, HEALTH-001, MFG-002 and OIL-002.
- **Table 17, every entry:**
  - Agreement and κ: 30 (1.00), 28 (0.95), 17 (0.63) and 3 (0.30).
  - Higher/lower: 2/0, 13/0 and 0/27.
  - Eligible with C ≥ 0.65: 0, 1, 1 and 0.
  - Level 0: 0, 0, 0 and 19.
  - ρ with C: 0.25, 0.18, 0.19 and 0.63.
  - ρ with RCI: 0.71, 0.69, 0.29 and 0.73.
  - Level distributions: as reported.
  - Water context: (2, 2), (3, 3), (2, 2) and (0, 0).
  - Original AI-SOC weights: 27 (0.93), with RAIL-002 at level 0.
- **Table A1, all 24 rows.** The number of changed levels and the up/down split, C*, and the showcase codes all match. No parameterization makes an action execution-eligible while a gate is unresolved. Only 1 of the 312 gated scenario–parameterization pairs changes: HOSP-001, with wC = 0.35 and stricter boundaries.
- **Table 11, interval columns.**
  - Window basis: 1.38–2.04%, 9.44–10.99% and 15.36–17.26%.
  - Block basis: 0.86–3.26%, 7.80–13.20% and 13.27–19.84%.
  - Exceedance distinguishable: No, Yes, Yes.
- **Table 12, interval column.** 0.43–0.95, 0.00–0.38, 0.02–0.48 and 0.15–0.72. RCI is 0.478, 0.606, 0.582 and 0.534.

The Table 11 intervals depend on how the flag rate is entered. With the reported rate as p̂, they match exactly. With implied integer counts instead (98, 593 and 948 of 5821), three upper limits move by 0.01 percentage points: 2.05, 3.27 and 19.83 in place of 2.04, 3.26 and 19.84. The original evidently used the unrounded v1.3.0 rates, so the reported rates are used here.

**Monte Carlo quantities.**

| Quantity | Manuscript | Script (seed 42) |
|---|---|---|
| Inputs-only retention ≥ 0.90 | 21 of 30 | 21 of 30 (WATER-001 lowest, 0.4933) |
| Joint MC provisional retention ≥ 0.90 | 18 of 30 | 18 of 30 |
| Joint MC final retention ≥ 0.90 | 25 of 30 | 25 of 30 |
| Lowest provisional retention | 0.49 (WATER-001) | 0.4937 (WATER-001) |
| Lowest final retention | 0.52 (HEALTH-002, margin 0.0010) | 0.5188 (HEALTH-002, margin 0.00095) |
| Final retention < 0.90 | CDI-001, WW-002, ROAD-002, HEALTH-002, HOSP-002 | same five; margins 0.00095–0.0368 |
| Minimum final retention, gated scenarios | ≥ 0.99 | 0.9907 |

The joint Monte Carlo counts depend on the seed. FOOD-001 (0.9003) and BUILD-001 (0.9004) lie at the 0.90 cut-off, and other scenarios are close to it. With seeds 1, 7, 123, 2024 and 99999:

- Provisional retention ≥ 0.90 in 16–18 of 30 scenarios.
- Final retention ≥ 0.90 in 23–25 of 30 scenarios.
- The lowest provisional retention is 0.493–0.498.
- The lowest final retention is 0.498–0.509.

## Figures

The script creates the figures from the same data:

- **Figure 4.** (a) Changed provisional and final levels for the 4 all-boundary shifts and the 16 single-boundary shifts. (b) Joint Monte Carlo retention against boundary margin, with open markers for provisional levels and filled markers for final levels.
- **Figure 5.** Calibration and target flag rates, with block-basis Wilson intervals and dashed budget lines.
- **Figure 6.** A grid of 30 scenarios × 4 variants, with the gate-unresolved eligible counts in the right-hand column.

The layout and styling are a re-implementation and are not byte-identical to the published renderings.
