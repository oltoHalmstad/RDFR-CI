# Changelog

## v1.4.1 — 2026-10-10

Release for the fourth revision of the article. Zenodo DOI: `10.5281/zenodo.23277893`.


- Corrected HAI 21.03 evaluation (`experiments/hai_evaluation.py`):
  - excludes the first 12 h of test3, which duplicate the calibration segment;
  - applies the training-referenced form of Equation (14);
  - adds test4 and test5;
  - records input hashes and library versions.
- Same-testbed replication on HAI 22.04 and 23.05 (`experiments/hai_replication.py`).
- Second-system evaluation on BATADAL (C-Town) under a protocol frozen before analysis (`preregistration/batadal_ctown/`):
  - Isolation Forest and reconstruction autoencoder;
  - predictions P1–P3;
  - 20 seeds and window-length sensitivity;
  - code: `experiments/batadal_evaluation.py`.
- C-Town action-consequence simulation with WNTR and policy-outcome comparison (`experiments/ctown_consequence.py`). Per-run results are cached in `results/ctown/cache/`.
- Cross-dataset summary (`experiments/summarize.py`).
- The reference segment of Equation (14) is an explicit argument of `anomaly_scores()` (`experiments/swat/train_isolation_forest.py`).
- New dependency: `wntr>=1.5`.
- `experiments/swat/run_swat_experiment.py` now passes the reference segment explicitly (`--score-reference training|segment`, default `training`).
- Release metadata (README, CITATION.cff, .zenodo.json, ZENODO_*, pyproject, `__version__`, `scripts/verify_results.py`) set to 1.4.1.
- These analyses were prepared with the assistance of Claude (Anthropic).

## v1.3.0 — 2026-09-09

- Aligned the software authority codes to manuscript Table 4: `0=Rollback/isolation` through `4=Bounded automation`.
- Replaced the v1.2.1 inverse restriction-rank convention in the core authority and uncertainty code.
- Implemented PASS / UNKNOWN / documented N/A / established-failure semantics and the priority prohibition/capability-scope stop rule from manuscript Section 3.8 and Table 3.
- Updated delegated authority to include `Authority_R,child` plus explicit capability intersection, matching Equation (12).
- Corrected manuscript Table 7 alignment to the synthetic detector sweep values `.510/.385`, `.286/.124` and `.381/.349`.
- Added manuscript artifact hashes, claim-level provenance, and a Sections 1-8 / Appendices A-C mapping.
- Synchronized release metadata to version 1.3.0. The new version DOI remains pending reservation; v1.2.1 DOI `10.5281/zenodo.22662284` is retained only as the previous-version identifier.

## v1.2.1 — 2026-09-06

Previous reproducibility-consistency correction. Software DOI: `10.5281/zenodo.22662284`.
