# SWaT A11 rerun (release v1.4.1)

`experiments/swat/a11_rerun.py` reruns the A11 analysis of Section 4.3 with the **training-referenced** form of Equation (14), as Reviewer comment CC1 required. The segment-wise form of release v1.3.0 is computed for comparison only.

## Data

The two A11 captures (19 and 20 February 2026; 29,160 one-second records each) are restricted by iTrust and are **not** included. Place them in `data/private/swat_a11/`. SHA-256 of the files used:

- `SWaT.A10_OTDataset_19-Feb-2026_0930_1735.csv`: `a435ceda8885756738b9a8b5489653e635e7b73cbae55a08a4bec5c6c9a80ce4`
- `SWaT.A10_OTDataset_20-Feb-2026_0905_1710.csv`: `beff59ba83c407280e493657e8dcd252d581fc0135988f3f538c276991126dac`

## Run

```
PYTHONPATH=src python experiments/swat/a11_rerun.py --data-dir data/private/swat_a11 --out-dir results/swat_a11
```

Runtime about 70 s. Environment of the reported run: Python 3.13.16, NumPy 2.5.3, pandas 3.0.5, scikit-learn 1.9.1.

## Pipeline (Section 3.13)

- 82 historian variables (alarm fields Active=1/Inactive=0; four fields that contain only "Bad Input" removed; other bad inputs interpolated).
- Rolling mean, standard deviation and end-to-end delta over 60 s windows ending every 5 s; 173 features after removing those constant on the training segment.
- Isolation Forest, 300 trees, seed 42, trained on the first 80% of the 19 February capture (4654 windows); thresholds selected on the remaining 1167 windows; target 5821 windows; block basis n_eff = 485.

The variable count, feature count and calibration flag rates (0.94%, 4.97%, 9.94%) reproduce the manuscript exactly.

## Threshold transfer (Table 11, Figure 5)

| Budget | Calibration | Target, training-referenced | Block-basis 95% CI | Target, segment-wise |
|---|---|---|---|---|
| 1% | 0.94% | 1.96% | 1.05–3.62% | 0.33% |
| 5% | 4.97% | 10.55% | 8.12–13.60% | 2.15% |
| 10% | 9.94% | 17.92% | 14.76–21.58% | 11.32% |

Across 20 further detector seeds (1–20):

- training-referenced: 1.25–1.89%, 6.94–11.24%, 15.72–17.94%; block-basis exceedance distinguishable in 1, 20 and 20 of 20 seeds;
- segment-wise: 0.19–0.79%, 1.75–3.68%, 9.95–12.23%; distinguishable in 0 of 20 seeds at every budget.

**Relation to the previously published values.** The earlier manuscript reported 1.68%, 10.19% and 16.29% and attributed them to the segment-wise form. This rerun does not reproduce them exactly. They lie inside the training-referenced range across detector seeds and well outside the segment-wise range, so the earlier conclusion (budgets exceeded on the later capture) holds under the corrected normalization.

## Constructed-event challenge (Table 12)

The event definitions of the earlier analysis were not archived. The 24 events were therefore specified anew in `a11_constructed_events.json` (SHA-256 in `a11_constructed_events.sha256`) before any perturbed copy was scored: offset (+2 sd), ramp (0 to +4 sd), freeze and zero-value perturbations of 600 s on single variables; 12 calibration and 12 held-out events; weights q = 1, 2, 3 for analyzer, flow/pressure and level/state variables.

| Threshold | Held-out events | Weighted recall | D | R_CI | Provisional level | Target flag rate |
|---|---|---|---|---|---|---|
| F1 comparator | 9/12 | 0.83 | 0.17 | 0.463 | Assisted defense | 12.42% |
| Nominal 1% | 4/12 | 0.42 | 0.58 | 0.547 | Shadow/restricted | 1.96% |
| Nominal 5% | 6/12 | 0.58 | 0.42 | 0.513 | Shadow/restricted | 10.55% |
| Nominal 10% | 11/12 | 0.92 | 0.08 | 0.447 | Assisted defense | 17.92% |

Seed sensitivity of the held-out detections is in `results/swat_a11/a11_seed_sensitivity.csv`.

## Outputs (`results/swat_a11/`)

`a11_results.json` (all values, input hashes, versions), `table_11.csv`, `table_12.csv`, `a11_seed_sensitivity.csv`, `figure_5_a11_flag_rates.png/.pdf`.
