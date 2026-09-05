
"""AI-specific risk and hard assurance triggers (Manuscript Section 3.5, Eq. 6)."""
from __future__ import annotations

DEFAULT_ALPHA = {"B": 0.25, "P": 0.25, "G": 0.25, "U": 0.25}
HARD_ASSURANCE_TRIGGERS = {"prompt_injection", "action_policy_bypass", "privilege_violation"}

def ai_specific_risk(B: float, P: float, G: float, U: float, alpha=None) -> float:
    """Return A = alpha1*B + alpha2*P + alpha3*G + alpha4*U."""
    alpha = DEFAULT_ALPHA if alpha is None else alpha
    for k in ("B", "P", "G", "U"):
        if k not in alpha:
            raise ValueError(f"missing alpha weight {k}")
    if abs(sum(float(alpha[k]) for k in ("B","P","G","U")) - 1.0) > 1e-9:
        raise ValueError("alpha weights must sum to 1")
    vals = {"B":B,"P":P,"G":G,"U":U}
    if any(not 0 <= float(v) <= 1 for v in vals.values()):
        raise ValueError("AI-risk inputs must lie in [0,1]")
    return float(sum(float(alpha[k]) * float(vals[k]) for k in vals))

def assurance_gate_trigger(events) -> bool:
    """Return True when any hard AI-assurance event must directly fail G_A."""
    return bool(HARD_ASSURANCE_TRIGGERS.intersection(set(events)))
