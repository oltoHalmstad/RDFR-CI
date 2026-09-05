
"""Threat-exposure calculations (Manuscript Section 3.3, Eq. 3)."""
from __future__ import annotations
import math

def tail_var_exposure(tail_var_95: float, risk_appetite: float) -> float:
    """Return E = min(1, TailVaR95 / RiskAppetite).

    Both inputs must be non-negative and risk appetite must be strictly positive.
    Saturation at 1 is intentional and should be reported because it removes
    discrimination among scenarios whose tail loss exceeds the appetite.
    """
    if risk_appetite <= 0 or not math.isfinite(risk_appetite):
        raise ValueError("risk_appetite must be finite and > 0")
    if tail_var_95 < 0 or not math.isfinite(tail_var_95):
        raise ValueError("tail_var_95 must be finite and >= 0")
    return min(1.0, float(tail_var_95) / float(risk_appetite))

def normalized_exposure(frequency: float, exploitability: float, adversary_capability: float,
                        external_exposure: float, control_effectiveness: float,
                        weights=(0.20, 0.20, 0.20, 0.20, 0.20)) -> float:
    """Scenario-based E for organizations without financial tail-risk modelling.

    The first four dimensions increase exposure; control effectiveness reduces it.
    This is a configurable normalized demonstration, not a universally validated formula.
    """
    xs = [frequency, exploitability, adversary_capability, external_exposure, control_effectiveness]
    if len(weights) != 5 or abs(sum(weights) - 1.0) > 1e-9:
        raise ValueError("weights must contain five values summing to 1")
    if any(not 0 <= float(x) <= 1 for x in xs):
        raise ValueError("all normalized exposure inputs must lie in [0, 1]")
    if any(float(w) < 0 for w in weights):
        raise ValueError("weights must be non-negative")
    vals = [frequency, exploitability, adversary_capability, external_exposure, 1.0-control_effectiveness]
    return float(sum(float(w) * float(v) for w, v in zip(weights, vals)))
