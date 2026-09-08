# RDFR-CI

**Risk-Driven Deployment and Forensic Readiness for Governing AI Authority in Critical Infrastructure Protection**

Reference implementation, scenario library, evaluation harness, and supplementary materials for the RDFR-CI paper by Olga Torstensson and Dmytro Prokopovych-Tkachenko.

> **Scientific status.** The cross-sector scenario values are illustrative demonstration inputs and must not be interpreted as measured risk levels for the corresponding sectors or organizations.
>
> **SWaT restriction.** This repository does not redistribute the Secure Water Treatment (SWaT) dataset. SWaT-derived results must be generated using an independently obtained authorized copy of the official iTrust/SUTD dataset.

## What this repository supports

RDFR-CI converts five measurable governance dimensions into a provisional AI-authority decision and then applies independent safety, availability, forensic-accountability, AI-assurance, and human-authority gates:

\[
R_{CI}=w_EE+w_DD+w_AA+w_FF+w_CC.
\]

The default illustrative weights are `E=0.20`, `D=0.20`, `A=0.15`, `F=0.20`, and `C=0.25`. These weights and all authority thresholds are configurable governance parameters, not universal constants.

The package contains:

- the core equations for exposure, detection gap, AI-specific risk, forensic readiness, consequence and cascading risk;
- independent deployment gates and half-open authority bands;
- the consequence-driven authority ceiling `R_min = w_C * C`;
- non-transitive authority for agentic and multi-agent workflows;
- a 30-scenario library spanning 18 critical-infrastructure sectors;
- the six manuscript showcases;
- 10,000-draw elicitation-uncertainty analysis;
- weight and aggregation sensitivity analyses;
- synthetic inter-rater and multi-agent demonstrations;
- reproducible publication figures and machine-readable tables;
- a pre-specified SWaT A1/A2 pipeline that refuses to run when authorized data are absent;
- an executed SWaT A11 normal-operation threshold-transfer experiment plus a clearly labeled synthetic perturbation challenge for D(phi) and authority propagation.

## Reproducibility classification

The repository separates four evidence classes and never merges them:

1. **Reproduced computational results** — deterministic results generated directly by repository code.
2. **Illustrative scenario results** — synthetic governance demonstrations, including the 30-scenario library and six showcases.
3. **External dataset protocol** — the SWaT validation workflow is implemented and ready to execute after authorized data access.
4. **Future empirical validation** — labeled attack validation, real practitioner elicitation, broader multi-testbed validation, and forensic-readiness field measurement remain future work.

An additional external-data class is reported for SWaT A11: empirical **normal-only** threshold transfer. Synthetic perturbation event metrics are kept separate and are not described as attack performance.

See `paper/claims_ledger.csv` for claim-level provenance.

## Quick start

```bash
git clone <repository>
cd RDFR-CI

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .

python experiments/run_all.py
```

Equivalent shell entry point:

```bash
bash scripts/reproduce_all.sh
```

For a fast CI-style run:

```bash
python experiments/run_all.py --smoke
```

## Main outputs

Generated unrestricted outputs are written to:

```text
results/tables/
results/figures/
results/scenario_results/
results/sensitivity/
results/logs/
```

Every major result table is emitted as CSV and Markdown. Figures are emitted as PNG and PDF. Scenario audits are JSON.

## Core authority bands

| Composite score | Provisional state |
|---|---|
| `R_CI < 0.20` | Bounded automation |
| `0.20 <= R_CI < 0.35` | Human-approved intervention |
| `0.35 <= R_CI < 0.50` | Assisted defense |
| `0.50 <= R_CI < 0.65` | Shadow / restricted |
| `R_CI >= 0.65` | Rollback / isolation |

The intervals are implemented as half-open bands exactly. Every scenario report includes the distance to the nearest authority boundary.

## Gate semantics and rank convention

The paper expresses final authority as the minimum of the provisional authority and all applicable gate caps on an authority/permissiveness scale. The software stores **restriction rank** as specified in the supplement design: `0 = Bounded automation` and `4 = Rollback / isolation`. Therefore the equivalent implementation takes the maximum restriction rank. A gate can maintain or reduce authority; it can never increase it.

`not_evaluated` is conservative and imposes the configured failure cap. `not_applicable` imposes no cap.

## Agentic and multi-agent authority

Delegation does not imply privilege escalation. A child agent is restricted by parent authority, its own scope, action policy, and every applicable gate. Synthetic demonstrations are provided for:

- a high-capability agent with low authorization;
- individually compliant agents whose combined workflow fails a system-level safety gate;
- authority revocation after an AI-assurance failure.

All demonstrations produce an independent witness-style JSONL event log.

## SWaT external validation

The pre-specified SWaT workflow uses:

- first 80% of the normal period for training;
- remaining 20% of normal data for FPR calibration;
- attack-episode-aware evaluation;
- 60 s primary windows, with 30 s and 120 s sensitivity settings documented;
- Isolation Forest as the primary baseline;
- a reconstruction autoencoder as a secondary baseline;
- FPR budgets of 0.01, 0.05 and 0.10;
- pointwise and event-level metrics;
- 10,000 attack-episode bootstrap resamples where feasible.

To run it after obtaining authorized files:

```bash
python experiments/swat/run_swat_experiment.py \
  --data-dir data/private/swat
```

When official files are absent, the A1/A2 program terminates and explicitly states that no empirical attack metrics were generated. See `data/README_SWAT.md` and `docs/swat_protocol.md`.

For the February 2026 A11 normal-operation captures, see `docs/swat_a11_normal_challenge.md` and run `experiments/swat_a11/run_a11_normal_challenge.py`. This experiment reports empirical next-day normal threshold transfer and a separate synthetic perturbation challenge. The raw A11 files are not redistributed.

## Tests

```bash
pytest -q
```

Tests cover the equations, exact band boundaries, gate monotonicity, non-transitive child authority, forensic-risk complement, authority ceiling, conservative unevaluated gates, non-applicable gates, scenario validation, and deterministic uncertainty simulation.

## Regulatory mapping

`docs/regulatory_mapping.md` provides a conceptual mapping to NIST CSF 2.0, NIST SP 800-82 Rev. 3, NIST AI RMF, NIST Generative AI Profile, the NIST adversarial-ML taxonomy, NISTIR 8428, NIS2, the Critical Entities Resilience Directive, the EU AI Act, the Cyber Resilience Act, and IEC 62443 principles.

RDFR-CI **does not certify or guarantee legal or regulatory compliance**. It can support, map to, complement, or provide operational evidence for governance processes.

## Reproducibility-aligned release v1.2.1

This release is aligned with the corrected MDPI submission master updated 8 September 2026; the reproducibility corrections themselves were completed on 6 September 2026. It resolves manuscript/repository consistency issues identified during reproducibility review: Figures A1-A3 in the manuscript are now the exact repository-generated outputs; Table 7 is regenerated directly from the same detector sweep used for Figure A3; the decision-stability text now reports the shipped result of **9/30 scenarios** with P(state change) > 0.10; and unsupported numerical cross-sector exposure/slope claims were removed from the manuscript.

The underlying experimental data and algorithms are unchanged from v1.2.0; v1.2.1 is a reproducibility-consistency correction. Raw SWaT data remain excluded.

A detailed manuscript-to-artifact consistency record is available in `paper/manuscript_reproducibility_alignment.md`.

## Citation and release status

- Software version: **1.2.1**
- Manuscript version aligned: **8 September 2026 (reproducibility-aligned final submission master with SWaT A11 experiment and exact A1-A3/Table 7 regeneration)**
- Article DOI: **pending**
- Software/Zenodo DOI: **10.5281/zenodo.22662284** (https://doi.org/10.5281/zenodo.22662284)
- GitHub URL: **https://github.com/oltoHalmstad/RDFR-CI**

See `CITATION.cff`, `.zenodo.json`, and `docs/release_checklist.md`.

## License

Code is released under the MIT License. Dataset licenses and access terms remain with their original providers; the MIT License does not grant rights to restricted third-party datasets.
