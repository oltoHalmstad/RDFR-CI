# RDFR-CI v1.3.0

**Risk-Driven Deployment and Forensic Readiness for Governing AI Authority in Critical Infrastructure Protection**

Reference implementation, scenario library, evaluation harness, and manuscript-aligned supplementary materials for the RDFR-CI article.

> **Scientific status.** The 30 cross-sector scenario values and the six showcased action contexts are illustrative governance inputs, not measured risk levels for sectors or organizations. The SWaT A11 materials distributed here are aggregate derived outputs plus a separately labeled constructed-event challenge; raw SWaT telemetry is not redistributed. Labeled SWaT A1/A2 attack validation remains unexecuted.

## What changed in v1.3.0

v1.3.0 is the manuscript-alignment release. It removes the remaining semantic drift between the Clean manuscript and the v1.2.1 implementation:

- the software now uses the **canonical manuscript authority scale**: `0=Rollback/isolation`, `1=Shadow/restricted`, `2=Assisted defense`, `3=Human-approved intervention`, `4=Bounded automation`;
- gate evidence distinguishes **PASS**, **UNKNOWN**, documented **NOT_APPLICABLE**, and established failure/prohibition;
- a **priority prohibition / capability-scope stop** precedes Equation (10);
- child authority in Equation (12) now includes the child's **own local provisional risk** and an explicit capability intersection;
- manuscript Tables **1-11, B1, C1, C2** and Figures **1-3, A1-A4** are tracked as publication artifacts and checked against the aligned manuscript;
- Table 7 uses the detector sweep values threshold `0.510/0.385`, D `0.286/0.124`, and R_CI `0.381/0.349`;
- the claims ledger and manuscript-to-repository mapping use the final Sections 1-8 / Appendices A-C structure.

## Core score

`R_CI = w_E E + w_D D + w_A A + w_F F + w_C C`

with illustrative default weights `0.20, 0.20, 0.15, 0.20, 0.25`. The score assigns a provisional level. Independent safety, availability, forensic-accountability, AI-assurance, and human-authority constraints can only maintain or reduce permission; explicit prohibitions and unauthorized capability scope select level 0 for the implicated AI action path.

## Canonical authority bands

| Composite score | Code | Provisional state |
|---|---:|---|
| `R_CI < 0.20` | 4 | Bounded automation |
| `0.20 <= R_CI < 0.35` | 3 | Human-approved intervention |
| `0.35 <= R_CI < 0.50` | 2 | Assisted defense |
| `0.50 <= R_CI < 0.65` | 1 | Shadow / restricted |
| `R_CI >= 0.65` | 0 | Rollback / isolation |

The intervals are half-open exactly. The numerical thresholds are illustrative governance parameters, not empirically established safety limits.

## Gate semantics

For actions that clear the priority stop and capability-scope check, Equation (10) is implemented as the minimum of the provisional code and applicable gate caps. Default UNKNOWN caps are `G_S=2`, `G_V=2`, `G_FA=2`, `G_A=1`, `G_H=2`. A valid required human approval caps the approved action at level 3; no per-action approval requirement may permit up to level 4 if all other conditions pass.

## Agentic / multi-agent authority

Delegation is non-transitive. Equation (12) caps a child by parent authority, the child's own local provisional risk, child scope, and child-local gates. Actual tools must also lie in `parent_delegable ∩ child_requested ∩ policy_allowed`.

## Evidence classes

1. **Reproduced computational results** — equations, score bands, detector calculations, scenario sensitivity and policy checks.
2. **Illustrative governance inputs** — 30 scenarios across 18 sector labels and six action contexts.
3. **External-data aggregate evidence** — reported A11 threshold transfer plus constructed-event/bootstrap summaries; raw SWaT data are excluded.
4. **Future empirical validation** — labeled A1/A2 attacks, practitioner reliability, controlled defensive actions, field forensic readiness and broader testbeds.

See `paper/claims_ledger.csv` for claim-level provenance and `paper/manuscript_to_repository_mapping.md` for the one-to-one map.

## Release / citation status

- Software version: **1.3.0**
- Manuscript alignment date: **9 September 2026**
- Article DOI: pending
- v1.3.0 Zenodo DOI: **pending reservation**
- Previous archived release v1.2.1: **10.5281/zenodo.22662284**
- GitHub: https://github.com/oltoHalmstad/RDFR-CI

Do not cite `10.5281/zenodo.22662284` as the v1.3.0 software DOI. Reserve a new version DOI in Zenodo, then replace the pending DOI field in the manuscript and release metadata before final publication.

## License

Code is MIT licensed. Dataset licenses/access terms remain with their original providers; the MIT License does not grant rights to restricted third-party data.
