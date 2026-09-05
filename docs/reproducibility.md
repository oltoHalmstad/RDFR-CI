# Reproducibility Guide

## Full unrestricted reproduction

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
python experiments/run_all.py
```

The run regenerates the scenario catalog calculations, uncertainty analysis, authority ceiling, aggregation sensitivity, weight sensitivity, inter-rater demonstration, agent-authority demonstration, synthetic detector-threshold analysis, conceptual figures, static manuscript-aligned tables and the reproducibility manifest.

## Smoke test

```bash
python experiments/run_all.py --smoke
```

The smoke mode lowers Monte Carlo counts for CI while preserving deterministic logic.

## Determinism

Randomized demonstrations use configurable seeds; the default seed is 42. Scenario generation uses its own fixed seed to preserve the versioned 30-scenario library.

## Traceability

The expected trace is:

```text
input/configuration -> code -> machine-readable output -> manuscript claim
```

Use `paper/claims_ledger.csv` and `paper/manuscript_to_repository_mapping.md` to follow this path.

## Restricted external data

The unrestricted reproduction path never requires SWaT. SWaT must be run explicitly with an authorized local copy. The private-data directory is ignored by Git.
