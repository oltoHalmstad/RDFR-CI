# SWaT Data Access and Local Placement

The RDFR-CI repository **does not contain or redistribute SWaT raw data**.

Researchers must independently obtain authorized access from the official iTrust / Singapore University of Technology and Design source and comply with the provider's terms of usage.

Place the authorized normal and attack CSV files locally under:

```text
data/private/swat/
```

The whole `data/private/` tree is ignored by Git except for `.gitkeep`.

Run:

```bash
python experiments/swat/run_swat_experiment.py --data-dir data/private/swat
```

If files are absent, the runner terminates with:

```text
Official SWaT data not found.

The RDFR-CI repository does not redistribute SWaT.

Please obtain authorized access from iTrust/SUTD and place the required files in:

data/private/swat/

No empirical SWaT metrics have been generated.
```

Do not commit authorized SWaT files, derived raw excerpts, or provider-restricted material to this repository.
