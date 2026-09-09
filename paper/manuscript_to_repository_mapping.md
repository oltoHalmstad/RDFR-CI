# RDFR-CI v1.3.0 manuscript-to-repository mapping

The aligned manuscript `RDFR-CI_Information_v1.3.0_aligned.docx` is distributed with the release/Zenodo package and identified in `paper/manuscript_reference.md` by SHA-256.

## Framework and equations

| Manuscript element | Canonical implementation / artifact |
|---|---|
| Section 3.2 / Equations (1)-(2) | `src/rdfr_ci/risk.py`, `configs/default_weights.yaml`, `paper/equations.csv` |
| Section 3.3 / Equation (3) | `src/rdfr_ci/exposure.py`, `paper/equations.csv` |
| Section 3.4 / Equations (4)-(5) | `src/rdfr_ci/detection.py`, `paper/equations.csv` |
| Section 3.5 / Equation (6) | `src/rdfr_ci/ai_risk.py`, `paper/equations.csv` |
| Section 3.6 / Equations (7)-(8) | `src/rdfr_ci/forensic.py`, `paper/equations.csv` |
| Section 3.7 / Equation (9) | `src/rdfr_ci/consequence.py`, `paper/equations.csv` |
| Section 3.8 / Equation (10) | `src/rdfr_ci/gates.py`, `configs/default_gates.yaml`, manuscript Table 3 |
| Section 3.9 authority states | `src/rdfr_ci/authority.py`, manuscript Table 4 |
| Section 3.10 / Equation (11) | `src/rdfr_ci/authority.py`, manuscript Table 5 |
| Section 3.11 / Equation (12) | `src/rdfr_ci/agent_authority.py`, `paper/equations.csv` |
| Section 4.3 / Equation (13) | `paper/equations.csv`, reported A11/constructed-event evidence |

## Manuscript results

- Table 7 is tied to the synthetic detector sweep values threshold `0.510/0.385`, FPR `0.000/0.037`, weighted recall `0.714/0.876`, D `0.286/0.124`, and RCI `0.381/0.349`.
- The six Table 10 action-context scores are `0.1705, 0.3055, 0.3385, 0.3705, 0.4195, 0.5000`.
- Table 11 uses the explicit v1.3 policy assumptions and final codes `4,2,2,2,2,1`.
- Scenario sensitivity retains the reported `21/30` alternative-aggregation changes and `9/30` point-band change probabilities above 0.10 under sigma=0.05, with WATER-001 at `0.5067`.

## Evidence and QA

- Claim-level provenance: `paper/claims_ledger.csv`.
- Exact manuscript SHA: `paper/manuscript_reference.md`.
- Equations: `paper/equations.csv`.
- Raw SWaT files remain excluded; labeled A1/A2 attack validation remains unexecuted.
