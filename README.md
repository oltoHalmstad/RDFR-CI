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

with illustrative default weights `0.20, 0.20, 0.15, 0.20, 0.25`.

## Release / citation status

- Software version: **1.3.0**
- Manuscript alignment date: **9 September 2026**
- Article DOI: pending
- v1.3.0 Zenodo DOI: **10.5281/zenodo.22682447**
- Previous archived release v1.2.1: **10.5281/zenodo.22662284**
- GitHub: https://github.com/oltoHalmstad/RDFR-CI

Cite `10.5281/zenodo.22682447` for the v1.3.0 software/supplementary release. `10.5281/zenodo.22662284` identifies the previous v1.2.1 release.

## License

Code is MIT licensed. Dataset licenses/access terms remain with their original providers; the MIT License does not grant rights to restricted third-party data.
