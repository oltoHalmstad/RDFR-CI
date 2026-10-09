# Pre-specified protocol: BATADAL second-system evaluation and C-Town action-consequence simulation

Frozen on 9 October 2026, before any detector was fitted to BATADAL data and before any defensive action was simulated.
The SHA-256 of this file is recorded in `PREREGISTRATION.sha256` and in every results file. Deviations are listed in
`DEVIATIONS.md`, and none is made silently. This is a time-stamped internal freeze, not a public registry entry.
For a public record, upload this file unchanged to OSF before citing it as a pre-registration.

## A. Data

| Data set | Period | Rows | Role |
|---|---|---|---|
| BATADAL training set 1 (`BATADAL_dataset03.csv`) | 6 Jan 2014 – 6 Jan 2015 | 8,761 hourly records | Normal operation: first 80% training, last 20% normal calibration |
| BATADAL training set 2 (`BATADAL_dataset04.csv`) | 4 Jul – 25 Dec 2016 | 4,177 records | F1-comparator selection; its attack-free hours are also *later period 1* for budget transfer |
| BATADAL test set (`BATADAL_test_dataset.csv`) | 4 Jan – 1 Apr 2017 | 2,089 records | Labeled held-out evaluation; attack-free hours are *later period 2* |

Ground truth comes from the published attack intervals (start inclusive, end exclusive), as tabulated in EPyT-Flow
`batadal_data.py`:
- 7 attacks in training set 2;
- 7 attacks in the test set.

The partial `ATT_FLAG` labels of training set 2 are not used.

Additional checks:
- identical rows and timestamps shared with training set 1;
- uniform hourly sampling.

## B. Detector protocol

This is the HAI protocol of Sections 3.13 and 3.15, adapted only for hourly sampling.

- **Variables:** all 43 sensor and status variables.
- **Windows:** trailing windows of L = 24 records (24 h), step 1 h.
  - Features: mean, standard deviation and end-to-end delta per variable.
  - Features constant on the training segment are dropped.
  - The scaler is fitted on the training segment only.
- **Primary detector:** Isolation Forest, 300 trees, contamination 'auto', seed 42.
- **Secondary detector** (Appendix B design):
  - a reconstruction autoencoder: an MLP with hidden layers (64, 16, 64), ReLU, Adam, max 500 iterations, early stopping, seed 42;
  - its score is the mean squared reconstruction error.
- **Score transform:** Equation (14) in the training-referenced form (primary). The segment-wise form is a sensitivity analysis.
- **Operating points:**
  - budgets φ = 1%, 5% and 10% selected on the calibration segment (same rule as HAI);
  - an F1 comparator selected on training set 2.
- **Window and episode definitions:**
  - A window is attack-free if it contains no attack hour.
  - An attack is detected if any window ending inside it is flagged.
  - Delay is in hours from attack start.
- **Uncertainty:**
  - false-positive rate: Wilson interval on non-overlapping 24 h blocks (n_eff = attack-free windows // 24), and a moving-block bootstrap with 120 h blocks;
  - recall: Clopper–Pearson;
  - provisional level: episode bootstrap with 10,000 resamples.
- **Mapping to the score:** Equation (15) (water context, R_CI = 0.430 + 0.20·D, equal attack weights), with the bands of Table 6.
- **Robustness:**
  - seeds 1–20 for both detectors;
  - window lengths 12 h and 48 h for the primary detector at seed 42.

## C. Pre-specified predictions

All three are evaluated for the primary detector at seed 42 and summarized over seeds 1–20.

- **Exceedance (definition used in P1 and P2).** For a budget-selected operating point, the flag rate on attack-free windows of a later period exceeds the budget, and the lower block-basis Wilson limit also exceeds it.

- **P1 (budget transfer).** At each budget, the operating point shows exceedance on later period 1, on later period 2, or on both.
  - Outcome: confirmed, or not confirmed, separately per budget.

- **P2 (complementary restriction).** For every budget-selected operating point, the final level for automated execution under Equation (15) and the assurance-gate rule of Table C2 is at most 1 (Shadow/restricted). This holds if either:
  - (a) the provisional level from the measured detection gap is at most 1, that is R_CI ≥ 0.50, equivalently held-out attack recall ≤ 0.65; or
  - (b) exceedance occurs on a later period.

  Each operating point is labeled with the mechanism or mechanisms that apply.

- **P3 (normalization).** At the 5% and 10% budgets, the segment-wise form gives a lower flag rate on the pooled later attack-free periods than the training-referenced form.

A prediction counts as not confirmed for an operating point if its criterion fails. Results are reported regardless of outcome.

## D. Action-consequence simulation (C-Town, `CTOWN.INP`)

**Simulation settings**
- EPANET 2.2 through WNTR, pressure-dependent demand: required pressure 15 m, minimum 0 m.
- 168 h horizon, 15 min hydraulic step, original control rules unchanged.

**Attack classes** (BATADAL type: control or sensor deception that forces actuators). Each is active from 24 h to 96 h and implemented as a rule with priority above the original controls.

| Attack | Effect |
|---|---|
| A1 | PU1 and PU2 forced off (supply to T1) |
| A2 | PU10 and PU11 forced off (supply to T7) |
| A3 | PU6 and PU7 forced off (supply to T4) |
| A4 | V2 forced closed (supply to T2) |

**Candidate defensive actions**, each applied from its start time t_a until 96 h (attack) or for 24 h (false alarm):

| Action | Description |
|---|---|
| a0 | No automated action |
| a1 | Station shutdown: all pumps or the valve of the affected station forced off (containment) |
| a2 | Manual fallback: affected pumps or valve forced on, overriding the attack |
| a3 | Zone isolation: the tank's outlet links closed |

**Metrics**, relative to the attack-free baseline:
- unserved demand volume (m³);
- junction-hours with pressure below 15 m;
- tank-envelope hours, meaning a tank level ≤ 0.2 m or ≥ (maximum − 0.05 m).

**Measured consequence of an incorrect action.** Each action is executed on a false alarm (no attack, t_a = 48 h, 24 h duration), for every station.
- C_service = min(1, unserved volume / (0.05 × expected demand volume in the 24 h action window))
- C_safety = min(1, added tank-envelope hours / 24)
- C_meas = max(C_service, C_safety)

**Gates evaluated from the simulation**, per action and station:
- G_S fails if the action adds tank-envelope hours relative to baseline;
- G_V fails if C_service > 0.20.

**Response-timing comparison** for detected attacks. Actions a1–a3 start at:
- t_a = attack start + measured median detection delay of the operating point (rounded up to whole hours), for autonomous execution;
- the same plus a human-approval delay d_h ∈ {1 h, 4 h}, for human-approved execution.

Outcome per (attack, action, timing): the same metrics over 24–168 h.

**Policy outcome comparison.** Detection results on the BATADAL test set at each budget are combined with the simulation, with explicit assumptions:

| Policy | Rule |
|---|---|
| Playbook | Every alarm episode triggers autonomous a1 |
| Gates-only | Autonomous execution of the action with the lowest C_meas that passes G_S and G_V; otherwise human-approved |
| Score-only | Provisional level from R_CI; at level 2 the AI recommends and a human executes after d_h |
| Full RDFR-CI | min(score level, gates, G_A); at level 1 the AI path is withheld and the human response is independent, with delay d_h |

Human reviewers are assumed to reject a fraction r ∈ {1.0, 0.9, 0.5} of false recommendations (sensitivity).

Reported per policy over the test period:
- autonomous actions on false alarms, with their summed consequence (unserved m³, envelope hours);
- attack response timing and simulated attack impact;
- unsafe autonomous actions, meaning autonomous actions that fail G_S or G_V.

This is a model-based outcome comparison, not field evidence. Attack classes are generic, not reconstructions of specific BATADAL attacks.

## E. Reporting

- All results are reported, including predictions that are not confirmed.
- Scripts, results, file hashes and environment are archived.
- Values must be rerun by the authors in their own environment before publication.
