#!/usr/bin/env python3
"""Generate static manuscript-aligned tables and conceptual figures."""
from pathlib import Path
import sys,pandas as pd
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'src')); sys.path.insert(0,str(HERE))
from common import write_df
from rdfr_ci.plotting import architecture_figure,evidence_workflow_figure,progressive_authority_figure,multi_agent_authority_figure

def main():
    tables={
      'table_1_research_streams.csv':pd.DataFrame([
        ['ML/DL detection','Improves anomaly and attack detection','Connects detection quality to consequence-sensitive authority'],
        ['Process-aware monitoring','Links cyber events to physical behavior','Extends detection context into response governance'],
        ['OT risk and resilience','Captures safety, reliability and service continuity','Makes these factors explicit deployment constraints'],
        ['AI governance','Provides lifecycle trustworthiness principles','Operationalizes them as measurable gates and stop conditions'],
        ['Autonomous defense','Reduces response latency','Limits action by reversibility, blast radius and process consequence'],
        ['OT DFIR','Supports evidence acquisition and reconstruction','Integrates forensic readiness into automation decisions'],
        ['Agent accountability','Supports provenance, replay and attribution','Requires independent witnessing of AI-influenced actions'],
      ],columns=['Research stream','Existing contribution','Gap addressed by RDFR-CI']),
      'table_2_ai_failure_modes.csv':pd.DataFrame([
        ['Model drift','Recall/calibration SLA breaches','Retrain, recalibrate or demote authority'],
        ['Evasion','Successful adversarial test cases','Harden features; restrict affected decision path'],
        ['Poisoning','Training or feedback integrity violation','Quarantine data; restore trusted training baseline'],
        ['Sensor manipulation','Cross-sensor or process-model inconsistency','Require corroboration before control action'],
        ['LLM hallucination','Unsupported factual claims','Evidence-only mode; analyst rewrite'],
        ['Prompt injection','Instruction hierarchy successfully altered','Disable tool use and isolate untrusted retrieval'],
        ['Agentic overreach','Unauthorized tool/action attempt','Revoke permissions; rollback authority level'],
        ['Environmental shift','Operation outside validated region','Shadow mode until revalidation'],
      ],columns=['Failure mode','Example indicator','Control response']),
      'table_3_independent_gates.csv':pd.DataFrame([
        ['G_S: Safety','Could the response violate a defined safety envelope?','Human-approved intervention (default; stricter action-specific cap permitted)','Block autonomous process-affecting action; require approval or stricter cap'],
        ['G_V: Availability','Could the response exceed maximum tolerable service disruption?','Human-approved intervention','Require operational approval or alternative action'],
        ['G_FA: Forensic accountability','Is evidence complete, independently witnessed, attributable and replayable?','Assisted defense','Preserve first or document emergency exception'],
        ['G_A: AI assurance','Is the model within its validated operating region and security policy?','Shadow / restricted','Demote authority; revalidate or retrain'],
        ['G_H: Human authority','Does policy, regulation or safety case require qualified human authorization?','Assisted defense','Recommendation only until approval'],
      ],columns=['Gate','Decision question','Authority cap on failure','Operational response']),
      'table_4_authority_bands.csv':pd.DataFrame([
        ['R_CI < 0.20','Bounded automation','Reversible, pre-authorized, low-blast-radius actions inside tested safety limits'],
        ['0.20 <= R_CI < 0.35','Human-approved intervention','AI proposes containment; qualified human authorizes execution'],
        ['0.35 <= R_CI < 0.50','Assisted defense','Detection, prioritization, evidence collection, simulation and recommendations'],
        ['0.50 <= R_CI < 0.65','Shadow / restricted','Outputs logged and evaluated; no direct process-affecting action'],
        ['R_CI >= 0.65','Rollback / isolation','AI removed from the live decision path until revalidation'],
      ],columns=['Composite score','State','Permitted AI activity']),
      'table_6_evidence_layers.csv':pd.DataFrame([
        ['Evidence','Packets, logs, sensor values, PLC logic, process state','Preserve original and integrity metadata'],
        ['Context','Asset criticality, topology, dependencies, CTI','Record source, version and retrieval time'],
        ['Interpretation','Anomaly scores, LLM explanation, reconstructed hypothesis','Label as AI-generated; cite supporting artifacts'],
        ['Recommendation','Proposed action, confidence, uncertainty, alternatives','Store rationale and policy basis'],
        ['Authorization','Human approval or pre-authorized policy decision','Record actor, time, scope and exceptions'],
        ['Action and verification','Firewall change, isolation, rollback, process validation','Record exact change, outcome and before/after evidence'],
      ],columns=['Layer','Examples','Forensic requirement']),
      'table_8_validation_metrics.csv':pd.DataFrame([
        ['Detection','Recall by asset class at declared FPR budget; precision; PR-AUC; latency; calibration','D'],
        ['Threat and loss','Frequency; ALE; VaR; Tail-VaR; adversary activity','E'],
        ['AI assurance','Drift; evasion success; prompt-injection success; policy violations','A / G_A'],
        ['Cyber-physical','Process deviation; safety event probability; outage duration; cascade','C / G_S / G_V'],
        ['Forensics','Evidence completeness; provenance; witness coverage; replay success','F / G_FA'],
        ['Automation','Action success; rollback success; blast radius; unauthorized attempts','Authority / stop conditions'],
        ['Human factors','Override rate; disagreement; review latency; uncertainty visibility','G_H'],
        ['Decision stability','Boundary margin; P(state); flip probability under declared uncertainty','Band assignment'],
        ['Elicitation reliability','Inter-rater ICC on values; agreement on resulting deployment state','All five dimensions'],
      ],columns=['Dimension','Example metrics','Primary framework element']),
      'table_9_swat_protocol.csv':pd.DataFrame([
        ['Dataset','SWaT A1/A2 Dec 2015 historian/process data','Official iTrust distribution; raw data not redistributed'],
        ['Training','First 80% of normal period, chronological','Fit model/preprocessing without attack leakage'],
        ['Normal calibration','Remaining 20% of normal period','Estimate FPR and false alarms per hour'],
        ['Attack split','Attack-scenario-wise calibration/test split','Prevent correlated windows from same attack on both sides'],
        ['Temporal window','60 s','Sensitivity at 30 s and 120 s'],
        ['Detectors','Isolation Forest; reconstruction autoencoder','Simple reproducible baseline plus reconstruction model'],
        ['FPR budgets phi','0.01, 0.05, 0.10','Strict, primary and relaxed operational budgets'],
        ['Primary metrics','PR-AUC, ROC-AUC, precision, recall, F1, event detection rate, median TTD, false alarms/hour','Separate statistical performance from operational burden'],
        ['RDFR-CI output','D(phi), R_CI, boundary margin, P(authority state)','Connect measured detection to deployment authority'],
        ['Uncertainty','10,000 attack-episode bootstrap resamples','Report authority as distribution rather than point state'],
      ],columns=['Element','Primary design','Purpose / sensitivity']),
      'table_11_deployment_phases.csv':pd.DataFrame([
        ['Phase 0','Offline','Dataset, model, policy and adversarial validation'],
        ['Phase 1','Shadow','Compare AI outputs with human and process-ground-truth decisions'],
        ['Phase 2','Advisory','Evidence-grounded prioritization, explanation and recommendations'],
        ['Phase 3','Controlled','Automated collection and reversible defensive actions'],
        ['Phase 4','Bounded autonomy','Pre-authorized automated response inside explicit safety and availability envelopes'],
      ],columns=['Phase','AI authority','Primary validation objective']),
      'table_12_stop_conditions.csv':pd.DataFrame([
        ['Recall below critical-asset SLA','Demote deployment state; investigate detector failure'],
        ['Significant feature/process drift','Freeze promotion; reassess operating region'],
        ['Successful adversarial manipulation','Disable affected model or action path'],
        ['Successful prompt injection or policy bypass','Disable tool-using mode until corrected'],
        ['Privilege violation','Revoke delegated privilege and isolate affected branch'],
        ['Forensic accountability below floor','Block destructive automation; preserve or record exception'],
        ['Repeated human overrides','Revalidate model, policy and escalation thresholds'],
        ['Failed rollback','Suspend relevant playbook and require manual recovery plan'],
        ['Safety-envelope violation','Immediate automation stop'],
        ['Unexpected process deviation after cyber action','Rollback where safe and escalate'],
        ['Operation outside validated model region','Return to shadow or advisory mode'],
        ['Score within one elicitation step of band edge','Freeze promotion; gather evidence'],
        ['Assessors disagree on deployment state','Reconcile elicitation before acting on score'],
        ['Excessive cross-agent propagation','Isolate delegated branch and re-evaluate agent trust boundaries'],
        ['Missing independent witness logs','Block privilege-bearing automation until witness coverage restored'],
      ],columns=['Condition','Required response']),
    }
    for name,df in tables.items(): write_df(df,ROOT/'results/tables'/name)
    architecture_figure(ROOT/'results/figures/figure_1_rdfr_ci_architecture')
    progressive_authority_figure(ROOT/'results/figures/figure_2_progressive_authority')
    evidence_workflow_figure(ROOT/'results/figures/figure_3_evidence_workflow')
    multi_agent_authority_figure(ROOT/'results/figures/figure_S1_multi_agent_authority')
    return tables
if __name__=='__main__': main()
