# RDFR-CI v1.2.1 Zenodo Archive

This archive is the reproducibility-aligned supplementary/software release supporting the RDFR-CI manuscript.

## Reproducibility alignment

Version 1.2.1 corrects manuscript-to-repository drift found during final submission QA. In the final manuscript, Appendix Figures A1-A3 are the exact outputs shipped under `results/figures/`; manuscript Table 7 is regenerated from the same detector-threshold sweep as Figure A3; Section 5.6 reports the shipped decision-stability result (9 of 30 scenarios with P(state change) > 0.10); and two unsupported numerical claims from an earlier draft were removed. See `paper/manuscript_reproducibility_alignment.md` for the detailed record and SHA-256 hashes.

## Data restriction

SWaT raw files are not redistributed. Authorized researchers must obtain them from the official provider and place them under the ignored private-data paths described in `data/README_SWAT.md`. Derived A11 normal-threshold-transfer results and clearly labeled synthetic-challenge outputs are included. Labeled A1/A2 attack results are not claimed in this release.

## Integrity

Run `python scripts/verify_results.py --full` from a configured environment. The v1.2.1 release passes 30 unit tests and the repository verification checks.

Article DOI: pending.
Software DOI: 10.5281/zenodo.22662284 (https://doi.org/10.5281/zenodo.22662284); reserved for this v1.2.1 deposit and activated when the Zenodo record is published.
