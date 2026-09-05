
"""Core RDFR-CI composite risk calculation (Manuscript Section 3.2, Eq. 1)."""
from __future__ import annotations
from typing import Mapping, Sequence
import math

DIMENSIONS = ("E", "D", "A", "F", "C")
DEFAULT_WEIGHTS = {"E": 0.20, "D": 0.20, "A": 0.15, "F": 0.20, "C": 0.25}

def validate_weights(weights: Mapping[str, float], atol: float = 1e-9) -> None:
    """Validate a five-element non-negative weight vector that sums to one."""
    missing = [k for k in DIMENSIONS if k not in weights]
    if missing:
        raise ValueError(f"Missing weights: {missing}")
    vals = [float(weights[k]) for k in DIMENSIONS]
    if any((not math.isfinite(v) or v < 0 or v > 1) for v in vals):
        raise ValueError("Weights must be finite and lie in [0, 1].")
    if abs(sum(vals) - 1.0) > atol:
        raise ValueError(f"Weights must sum to 1; got {sum(vals):.12f}")

def _validate_unit_interval(values: Sequence[float], names: Sequence[str]) -> None:
    for name, value in zip(names, values):
        value = float(value)
        if not math.isfinite(value) or not 0.0 <= value <= 1.0:
            raise ValueError(f"{name} must lie in [0, 1]; got {value}")

def composite_risk(E: float, D: float, A: float, F: float, C: float,
                   weights: Mapping[str, float] | None = None) -> float:
    """Calculate RDFR-CI composite deployment risk.

    R_CI = w_E E + w_D D + w_A A + w_F F + w_C C.
    Inputs and the returned score lie in [0, 1]. The default weights are
    illustrative governance parameters, not universal constants.
    """
    weights = DEFAULT_WEIGHTS if weights is None else weights
    validate_weights(weights)
    vals = (E, D, A, F, C)
    _validate_unit_interval(vals, DIMENSIONS)
    return float(sum(weights[k] * float(v) for k, v in zip(DIMENSIONS, vals)))
