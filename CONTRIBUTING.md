# Contributing

Contributions are welcome when they improve reproducibility, validation, documentation, or scientific transparency.

## Scientific integrity

Do not submit fabricated datasets, fabricated citations, unverified empirical claims, or restricted SWaT files. New scenario values must be labeled as illustrative unless they are backed by documented empirical evidence. Regulatory mappings must use language such as *supports*, *maps to*, *can complement*, or *can inform*; do not claim compliance certification.

## Code changes

1. Create a focused branch.
2. Add or update tests.
3. Run `pytest -q`.
4. Run `python experiments/run_all.py --smoke`.
5. Explain whether outputs are reproduced, illustrative, externally data-dependent, or future work.
