
"""Machine-readable scenario audit output."""
from __future__ import annotations
from datetime import datetime, timezone
from . import __version__

def build_audit(scenario, score, provisional, final, binding, uncertainty):
    return {
        "scenario_id": scenario.scenario_id,
        "risk_dimensions": scenario.values(),
        "weights": scenario.weights,
        "beta_vector": scenario.beta_vector,
        "composite_score": float(score),
        "provisional_authority": provisional,
        "gate_results": scenario.gate_states,
        "gate_caps": scenario.gate_caps,
        "final_authority": final,
        "binding_constraint": binding,
        "boundary_margin": float(uncertainty['boundary_margin']),
        "uncertainty": {k:v for k,v in uncertainty.items() if k.startswith('p_')},
        "assumptions": scenario.assumptions,
        "evidence_status": scenario.evidence_status,
        "illustrative_or_empirical": scenario.illustrative_or_empirical,
        "evidence_references": [],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "software_version": __version__,
    }
