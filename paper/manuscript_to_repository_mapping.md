# Manuscript-to-Repository Mapping

| Manuscript element | Repository implementation / evidence |
|---|---|
| Section 2 Related Work and Research Gap | `docs/framework.md`, `docs/regulatory_mapping.md` |
| Section 3.2 Five Risk Dimensions | `src/rdfr_ci/risk.py`, `configs/default_weights.yaml`, `tests/test_risk.py` |
| Section 3.3 Threat Exposure | `src/rdfr_ci/exposure.py`, `tests/test_exposure.py` |
| Section 3.4 Detection Capability Gap | `src/rdfr_ci/detection.py`, `experiments/run_detection_threshold_demo.py`, `tests/test_detection.py` |
| Section 3.5 AI-Specific Risk | `src/rdfr_ci/ai_risk.py`, `results/tables/table_2_ai_failure_modes.*` |
| Section 3.6 Forensic Readiness | `src/rdfr_ci/forensic.py`, `docs/forensic_readiness.md`, `tests/test_forensics.py` |
| Section 3.7 Cyber-Physical Consequence | `src/rdfr_ci/consequence.py`, `tests/test_consequence.py` |
| Section 3.8 Independent Deployment Gates | `src/rdfr_ci/gates.py`, `configs/default_gates.yaml`, `tests/test_gates.py` |
| Section 3.9 Authority States | `src/rdfr_ci/authority.py`, `configs/default_thresholds.yaml`, `tests/test_authority.py` |
| Section 3.10 Authority Ceiling | `src/rdfr_ci/authority.py`, `experiments/run_authority_ceiling.py`, `results/figures/figure_A1_authority_ceiling.*` |
| Section 3.11 Agentic/Multi-Agent Authority | `src/rdfr_ci/agent_authority.py`, `experiments/run_agent_authority_demo.py`, `results/figures/figure_S1_multi_agent_authority.*` |
| Section 4 Evidence-Preserving Workflow | `docs/forensic_readiness.md`, `results/figures/figure_3_evidence_workflow.*` |
| Section 5.1 Cyber-Physical Monte Carlo Model | `src/rdfr_ci/monte_carlo.py`, `experiments/run_loss_model_demo.py`, `results/tables/table_S4_loss_channel_demo.*` |
| Section 5.2 Detector Evaluation | `experiments/run_detection_threshold_demo.py`, `results/sensitivity/detection_threshold_sweep.*`, `results/tables/table_7_manuscript_detection_operating_points.*` |
| Section 5.3 Adversarial/Agent Testing | `src/rdfr_ci/ai_risk.py`, `experiments/run_agent_authority_demo.py` |
| Section 5.4 Forensic Readiness Evaluation | `src/rdfr_ci/forensic.py`, `results/scenario_results/*.json` |
| Section 5.5 Action-Safety Evaluation | `results/tables/table_12_stop_conditions.*`, `docs/deployment_gates.md` |
| Section 5.6 Decision Stability | `src/rdfr_ci/uncertainty.py`, `experiments/run_scenario_analysis.py`, `results/figures/figure_A2_decision_stability.*` |
| Section 5.7 SWaT Validation | `experiments/swat/`, `configs/swat.yaml`, `data/README_SWAT.md`, `docs/swat_protocol.md` |
| Section 6 Cross-Sector Showcases | `scenarios/showcases/`, `results/tables/table_10_six_sector_showcases.*` |
| Section 7 Cross-Showcase Interpretation | `results/tables/table_S1_thirty_scenario_results.*`, `results/sensitivity/aggregation_sensitivity.*` |
| Section 8 Forensic Readiness as Enabler | `src/rdfr_ci/forensic.py`, `docs/forensic_readiness.md` |
| Section 9 Governance / CRA Alignment | `docs/regulatory_mapping.md` |
| Section 10 Deployment / Stop Conditions | `results/tables/table_11_deployment_phases.*`, `results/tables/table_12_stop_conditions.*` |
| Section 12 Threats to Validity | `README.md` reproducibility classes; `paper/claims_ledger.csv` |
| Section 13 Future Validation | `docs/swat_protocol.md`, `data/README_SWAT.md` |
| Appendix authority ceiling | `results/figures/figure_A1_authority_ceiling.*` |
| Appendix decision stability | `results/figures/figure_A2_decision_stability.*` |
| Appendix detection threshold | `results/figures/figure_A3_detection_threshold_authority.*` |
