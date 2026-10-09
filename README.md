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

## Revision-4 analyses (HAI replication, BATADAL second system, C-Town simulation)

These analyses support the fourth revision of the article (manuscript information-4588318). They are intended for release v1.4.1.

### What v1.4.1 adds

| Manuscript | Script | Outputs |
|---|---|---|
| Sections 3.15 and 4.6, Tables 16, D1 and D2, Figure 7: corrected HAI 21.03 evaluation | `experiments/hai_evaluation.py` | `results/hai/hai21.03/` |
| Section 4.6 and Table D3: replication on HAI 22.04 and 23.05 | `experiments/hai_replication.py` | `results/hai/hai22.04/`, `results/hai/hai23.05/` |
| Sections 3.17 and 4.8, Table D4: BATADAL second system, with pre-specified predictions | `experiments/batadal_evaluation.py` | `results/batadal/` |
| Section 4.9, Tables D5 and D6: C-Town action-consequence simulation and policy outcomes | `experiments/ctown_consequence.py` | `results/ctown/` |
| Table D4: cross-dataset summary | `experiments/summarize.py` | `results/summary/` |
| Figure 7 and Figure A2 | `experiments/make_figures.py` | `results/figures/revision4/` |
| Section 3.13 and Equation (14): explicit reference segment | `experiments/swat/train_isolation_forest.py` (patched) | Rerun of SWaT A11, if the restricted data are available |

The protocol and predictions for the BATADAL and C-Town analyses were fixed before analysis. They are in `preregistration/batadal_ctown/PREREGISTRATION.md`, with its SHA-256 and freeze time in `PREREGISTRATION.sha256`; every deviation is in `DEVIATIONS.md`. The hash of the protocol is also stored in each results file.

### Data

No dataset is redistributed. Input-file SHA-256 values are stored in the results JSON files (`meta`).

- **HAI 21.03, 22.04, 23.05.** https://github.com/icsdataset/hai (CC BY-SA 4.0). Releases 22.04 and 23.05 are Git LFS files: run `git lfs pull` after cloning. The 23.05 label file `label-test2.csv` stores timestamps only to the minute, so labels are matched to data by row.
- **BATADAL and C-Town.** https://www.batadal.net: `BATADAL_dataset03.csv`, `BATADAL_dataset04.csv`, `BATADAL_test_dataset.zip` and `CTOWN.INP`. Place them in `data/batadal/raw/` and unzip the test set there (`unzip BATADAL_test_dataset.zip`), so that `BATADAL_test_dataset.csv` is present.
  - `data/batadal/batadal_attacks.csv` holds the published attack intervals of Taormina et al. (2018), as tabulated in EPyT-Flow (`epyt_flow/data/benchmarks/batadal_data.py`).

### Reproduce (from the repository root)

```bash
pip install -r requirements.txt "wntr>=1.5"

# HAI 21.03 (corrected evaluation), HAI 22.04 / 23.05 (replication)
python experiments/hai_evaluation.py --data-dir DATA/hai-21.03 --out-dir results/hai/hai21.03 --seed-sensitivity 20
python experiments/hai_replication.py --version 22.04 --data-dir DATA/hai-22.04 --out-dir results/hai/hai22.04 --seeds 20
python experiments/hai_replication.py --version 23.05 --data-dir DATA/hai-23.05 --out-dir results/hai/hai23.05 --seeds 20

# BATADAL (pre-specified protocol) and C-Town simulation
python experiments/batadal_evaluation.py --data-dir data/batadal/raw --attacks data/batadal/batadal_attacks.csv --out-dir results/batadal --seeds 20
python experiments/ctown_consequence.py --inp data/batadal/raw/CTOWN.INP --batadal-dir data/batadal/raw \
    --attacks data/batadal/batadal_attacks.csv --out-dir results/ctown --no-new-a3
python experiments/summarize.py .
```

`ctown_consequence.py` stores each hydraulic run in `results/ctown/cache/` (or the directory named by `RDFR_CTOWN_CACHE`) and reuses it.
- `--cached-only` rebuilds Tables D5 and D6 from the archived runs in seconds.
- Without `--no-new-a3`, the script also runs the 27 zone-isolation-under-attack runs that were not completed for the article (DEVIATIONS.md, item 12). Each takes 10–30 minutes; none of them enters Table D6.

Running the scripts above reproduced `results/batadal/batadal_results.json` (primary results and predictions) and the Table D5 and D6 files exactly.

### Environment of the reported runs

Python 3.13.16, NumPy 2.5.3, pandas 3.0.5, SciPy 1.18.1, scikit-learn 1.9.1, WNTR 1.5.0. The Python, NumPy, pandas and scikit-learn versions are also stored in the HAI and BATADAL results JSON files, and the WNTR version in `results/ctown/ctown_results.json`.

### Notes for the release

- The HAI scripts were re-implemented from the manuscript description, because the v1.4.0 `hai_evaluation.py` was not public. On the uncorrected 21.03 split they give 2.27%, 7.83% and 14.63%, where the earlier manuscript version reported 2.44%, 8.20% and 15.03%. Rerun them in the release environment and confirm all values before publication.
- The analyses in this overlay were prepared with the assistance of Claude (Anthropic) and must be checked by the authors.
