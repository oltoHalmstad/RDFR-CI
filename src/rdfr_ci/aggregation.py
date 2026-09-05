
"""Alternative compensatory/non-compensatory aggregation sensitivity."""
from __future__ import annotations
import numpy as np
from .risk import DIMENSIONS, validate_weights

def weighted_arithmetic(values, weights):
    validate_weights(weights)
    x = np.asarray([values[k] for k in DIMENSIONS], dtype=float)
    w = np.asarray([weights[k] for k in DIMENSIONS], dtype=float)
    return float(np.dot(w,x))

def weighted_power_mean(values, weights, rho: float):
    """Weighted power mean; rho=1 equals the arithmetic model."""
    if rho <= 0:
        raise ValueError("rho must be > 0 for this implementation")
    validate_weights(weights)
    x = np.asarray([values[k] for k in DIMENSIONS], dtype=float)
    w = np.asarray([weights[k] for k in DIMENSIONS], dtype=float)
    if np.any((x < 0) | (x > 1)):
        raise ValueError("dimension values must lie in [0,1]")
    return float(np.sum(w*np.power(x,rho))**(1.0/rho))

def worst_dimension_blend(values, weights, mean_share: float = 0.70):
    """Blend weighted arithmetic mean with max dimension (default 70/30)."""
    if not 0 <= mean_share <= 1:
        raise ValueError("mean_share must lie in [0,1]")
    mean = weighted_arithmetic(values, weights)
    worst = max(float(values[k]) for k in DIMENSIONS)
    return float(mean_share*mean + (1.0-mean_share)*worst)
