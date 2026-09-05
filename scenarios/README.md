# Scenario Library

`scenario_catalog.yaml` is the authoritative 30-scenario catalog. JSON and CSV forms are provided for interoperability.

**All scenario values are illustrative demonstration inputs — not measured sector risk levels.**

The library spans exactly 18 sector labels and includes the six manuscript showcases in `scenarios/showcases/`.

Each scenario stores:

- descriptive attack and defensive-action context;
- `E`, `D`, `A`, `F`, `C`;
- the weight vector;
- an explicit beta vector and neutral consequence-component reproduction;
- gate states and failure caps;
- provisional/final authority and binding constraint;
- boundary margin;
- assumptions and evidence classification.

The generator is deterministic: `scripts/generate_scenarios.py`. The catalog is intentionally versioned so the manuscript's aggregation-sensitivity statement (21/30 scenarios change provisional state under at least one tested alternative operator) remains reproducible.
