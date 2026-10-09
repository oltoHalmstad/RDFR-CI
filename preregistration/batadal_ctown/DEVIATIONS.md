# Deviations from PREREGISTRATION.md, and clarifications

Every item below was decided before the result it affects was inspected, unless stated otherwise. Items 7–11 correct defects
found by an independent code review; that review was carried out after the BATADAL detection results and the cached part of
the simulation had been seen.

1. **Station without a gate-passing action (clarification).** The protocol did not say which action is executed when no candidate action passes G_S and G_V for a station.
   - Gates-only: the lowest-C_meas action goes to a human, who executes it after d_h.
   - Full RDFR-CI: every candidate action is treated as prohibited for that station, so the AI recommends nothing (a0).

2. **Hydraulic solver.** EPANET 2.2 with pressure-dependent demand gave non-physical solutions when a tank pipe was closed (pressures down to −6×10^5 m; unserved demand larger than expected demand).
   - All runs use WNTR's pressure-dependent solver (WNTRSimulator) with otherwise unchanged settings, and the EPANET results were discarded.
   - The two solvers also differ by tens of m³ per week on runs that EPANET solved validly, so all comparisons use a baseline from the same solver.

3. **Non-converging runs.** A run that does not converge over 168 h is retried once with the Newton iteration limit raised from 3,000 to 10,000; backtracking is already on by default in WNTR 1.5. If it still fails, it is reported as "no convergence" and excluded, not imputed. Results are cached per run.

4. **Ties in C_meas (clarification).** Actions whose C_meas lies within 0.01 of the station minimum are treated as tied, and the tie goes to the protocol's listing order (a1, a2, a3). This rule was fixed after the false-alarm runs and before any attack-response or policy result existed. The slow zone-isolation runs were moved to the end of the queue; the set of runs is unchanged.

5. **Station shutdown during an attack (exact shortcut).** a1 forces the attacked elements to the status the attack already imposes, over part of the attack interval, so its hydraulics equal the no-action run. The no-action run is reused; the 10 a1 runs computed before this change were identical to it (within about 1e-13).

6. **Operator response when the AI path is withheld (clarification).** The protocol defined the human response only for level 2. At level 1, both the score-only and the full policy now assume the operator responds independently with the manual fallback (a2) after the detection delay plus d_h, and no AI recommendation reaches the operator.
   - The earlier draft of this item claimed the policies were already symmetric and that no number changed. Both statements were wrong: Score-only used a1 while Full used the gate-selected action.
   - The policy numbers reported now come from the corrected rule.

7. **Tank-envelope hours (correction).** For G_S and C_safety, added envelope hours are counted per tank and only increases count. In the first implementation, an increase in one tank could be cancelled by a decrease in another. The false-alarm runs and their baselines were rerun to record per-tank hours.

8. **Missed attacks in the policy comparison (correction).** Each policy's attack impact is now the detection-weighted mix (k/n) × response outcome + (1 − k/n) × no-action outcome. Previously every attack was treated as detected.

9. **Metric details not stated in the protocol (disclosure).**
   - **Junctions:** low-pressure junction-hours and minimum pressure are computed over junctions with non-zero demand.
   - **Metric windows:**
     - false-alarm consequences: the 24 h action window plus 24 h of recovery (48–96 h), scaled by the expected demand of the 24 h action window;
     - attack outcomes: 24–168 h.
   - **Clipping:** per-action false-alarm costs are clipped at zero in the policy comparison.
   - **Zone isolation (a3):** closes every link at the tank. Each C-Town tank has exactly one link, so this equals closing its outlet pipe.
   - **Negative pressures:** runs with negative minimum pressure at a demand junction are flagged in the output tables (`negative_pressure`).
   - **Assurance gate:** in the policy comparison, the gate uses exceedance in either later period, as in P2.

10. **Window-length sensitivity (correction).** The 12 h and 48 h sensitivity runs now use the protocol's 24 h blocks for the Wilson interval. They previously used blocks equal to the window length.

11. **Labels (correction, no numeric effect).**
    - `R_CI_lower` was renamed `R_CI_at_lower_recall`.
    - `final_level` is min(provisional level, 1) when the gate binds. Level 0 cannot occur here.
    - The cross-dataset summary now reports the pooled later periods for every dataset.

**Caveat on the detection definition (not a deviation).** For test attack 1 at the 5% and 10% budgets, the detector was already flagging in the hour before the attack began. Under the pre-specified definition (any flagged window ending inside the attack), this counts as a detection with delay 0.

12. **Compute budget for zone isolation during attacks (incomplete runs).** Zone isolation during an attack (a3 under attack) needed 10–30 min per run with WNTR on the two available cores. When the other runs finished, 5 of these 32 descriptive runs were complete, so the rest were stopped to keep the reruns for item 7 within the time available.
   - None of these runs enters the policy comparison: a3 is never the action selected by the gate rules.
   - The missing runs are listed as "not run". They can be completed with the archived script (`--cached-only` off), without changing any other result.
