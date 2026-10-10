# RDFR-CI v1.4.1 Zenodo archive

This package is the software and supplementary release supporting the fourth revision of the RDFR-CI article (DOI 10.5281/zenodo.23277893).

v1.4.1 adds the labeled-attack and consequence analyses of the revised article:

- `experiments/hai_evaluation.py`: corrected HAI 21.03 evaluation (Sections 3.15 and 4.6; Tables 16, D1, D2; Figure 7);
- `experiments/hai_replication.py`: replication on HAI 22.04 and 23.05 (Table D3);
- `experiments/batadal_evaluation.py`: BATADAL second-system evaluation under the protocol in `preregistration/batadal_ctown/` (Section 4.8; Table D4);
- `experiments/ctown_consequence.py`: C-Town action-consequence simulation and policy outcomes (Section 4.9; Tables D5, D6), with cached runs in `results/ctown/cache/`;
- `experiments/run_revision_analyses.py`: robustness, policy-variant, alternative-method and parameterization analyses (Tables 10, 15, 17, A1; interval columns of Tables 11 and 12; Figures 4–6), re-implemented from the manuscript description and verified to reproduce the published values (`experiments/REVISION_ANALYSES_NOTE.md`);
- `experiments/summarize.py` and `experiments/make_figures.py`.

The policy implementation (authority scale, gates, delegation) is unchanged from v1.3.0. See `README.md` for commands and the environment of the reported runs, and `CHANGELOG.md` for details.

No dataset is redistributed. Raw SWaT files are subject to iTrust access conditions; HAI (CC BY-SA 4.0) and BATADAL must be downloaded from their providers. Labeled SWaT A1/A2 attack validation remains unexecuted. Aggregate A11 values reported in the manuscript must remain clearly separated from real-attack performance claims.

Earlier releases: v1.3.0 `10.5281/zenodo.22682447`; v1.2.1 `10.5281/zenodo.22662284`.
