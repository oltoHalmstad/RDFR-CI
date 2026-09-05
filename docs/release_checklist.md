# v1.0.0 Release Checklist

- [ ] Replace `https://github.com/TODO/RDFR-CI` in `README.md` and `CITATION.cff`.
- [ ] Replace `ARTICLE DOI: pending` if/when the manuscript DOI is assigned.
- [ ] Replace `SOFTWARE DOI: pending` only after Zenodo creates the archived software DOI.
- [ ] Confirm software authors and affiliations in `CITATION.cff` and `.zenodo.json`.
- [ ] Run `pytest -q`.
- [ ] Run `python experiments/run_all.py`.
- [ ] Run `python scripts/verify_results.py`.
- [ ] Confirm `git status` contains no restricted data.
- [ ] Confirm `git ls-files data/private` lists only `.gitkeep`.
- [ ] Inspect all PNG/PDF figures.
- [ ] Confirm the six showcase scores match the manuscript.
- [ ] Confirm aggregation sensitivity reports 21/30 scenarios changing provisional state under at least one alternative operator.
- [ ] Confirm the scenario library spans 18 sectors and contains 30 scenarios.
- [ ] Confirm all scenario values remain labeled illustrative.
- [ ] Confirm SWaT empirical results remain absent unless generated from an authorized official copy.
- [ ] Tag `v1.0.0` on GitHub.
- [ ] Create the GitHub release and enable Zenodo archiving.
- [ ] Regenerate `results/reproducibility_manifest.json` after the release commit/tag if an exact commit hash is required.
