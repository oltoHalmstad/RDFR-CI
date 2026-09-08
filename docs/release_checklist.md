# v1.2.1 Release Checklist

## Verified in this package

- [x] Public GitHub URL is `https://github.com/oltoHalmstad/RDFR-CI`.
- [x] Software authors and affiliations are aligned in `CITATION.cff` and `.zenodo.json`.
- [x] Manuscript-to-repository mapping includes Section 5.8 and SWaT A11 outputs.
- [x] Figure/table audit confirms all 12 tables and 7 figures are mentioned in the manuscript text before their captions.
- [x] SWaT A11 empirical normal-only results are kept separate from synthetic challenge results.
- [x] No labeled SWaT A1/A2 attack-detection results are claimed.
- [x] Restricted SWaT raw files are excluded from the repository/archive.
- [x] GitHub/Zenodo metadata are prepared for version 1.2.1.

## Complete immediately before GitHub release

- [ ] Upload/replace the v1.2.1 files in `https://github.com/oltoHalmstad/RDFR-CI`.
- [ ] Confirm the GitHub Actions workflow passes.
- [ ] Confirm `data/private/` contains only `.gitkeep` in the public repository.
- [ ] Create tag `v1.2.1`.
- [ ] Create GitHub release **RDFR-CI v1.2.1 — Submission-Aligned Supplementary and Reproducibility Package**.

## Complete for Zenodo

- [ ] Upload `RDFR-CI-v1.2.1-Zenodo.zip` or archive the GitHub `v1.2.1` release through Zenodo.
- [ ] Use the metadata in `.zenodo.json` / `docs/ZENODO_DEPOSIT_GUIDE.md`.
- [x] Reserve or obtain the Zenodo DOI: `10.5281/zenodo.22662284`.
- [x] Replace `SOFTWARE DOI: pending` in `README.md` and `CITATION.cff` after DOI reservation.
- [ ] Add the article DOI later when assigned; do not invent it before acceptance/publication.
- [x] Add the reserved Zenodo DOI to the manuscript Supplementary Materials/Data Availability statement before submission.
