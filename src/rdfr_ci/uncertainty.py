
"""Uncertainty propagation and authority-state stability analysis (Manuscript Section 5.6)."""
from __future__ import annotations
import numpy as np
from .risk import DIMENSIONS, composite_risk, validate_weights
from .authority import AuthorityState, authority_from_score, boundary_margin, label

def simulate_state_distribution(values, weights, sigma=0.05, n=10_000, seed=42):
    """Propagate independent truncated-normal elicitation uncertainty through Eq. 1.

    The default sigma=0.05 corresponds to one step on a 20-point elicitation rubric.
    This is an illustrative methodological model, not a claim of universal uncertainty.
    """
    validate_weights(weights)
    if sigma < 0 or n <= 0:
        raise ValueError("sigma must be >=0 and n > 0")
    base = np.array([float(values[k]) for k in DIMENSIONS])
    if np.any((base < 0)|(base > 1)):
        raise ValueError("dimension values must lie in [0,1]")
    rng = np.random.default_rng(seed)
    draws = np.clip(rng.normal(base, sigma, size=(int(n), len(DIMENSIONS))), 0.0, 1.0)
    w = np.array([weights[k] for k in DIMENSIONS])
    scores = draws @ w
    # Vectorized exact half-open band mapping.
    states = np.select(
        [scores < .20, scores < .35, scores < .50, scores < .65],
        [0,1,2,3], default=4).astype(int)
    point_score = composite_risk(*(values[k] for k in DIMENSIONS), weights=weights)
    point_state = authority_from_score(point_score)
    counts = np.bincount(states, minlength=5)
    probs = counts / counts.sum()
    modal = AuthorityState(int(np.argmax(probs)))
    return {
        "point_score": point_score,
        "mean_R_CI": float(scores.mean()),
        "median_R_CI": float(np.median(scores)),
        "p05_R_CI": float(np.quantile(scores,.05)),
        "p95_R_CI": float(np.quantile(scores,.95)),
        "point_state": label(point_state),
        "modal_state": label(modal),
        "p_bounded": float(probs[0]),
        "p_human_approved": float(probs[1]),
        "p_assisted": float(probs[2]),
        "p_shadow": float(probs[3]),
        "p_rollback": float(probs[4]),
        "p_point_state": float(probs[int(point_state)]),
        "p_state_change": float(1.0-probs[int(point_state)]),
        "boundary_margin": boundary_margin(point_score),
        "n": int(n), "sigma": float(sigma), "seed": int(seed),
    }

def dirichlet_weight_sensitivity(values, base_weights, concentration=120.0, n=5000, seed=42):
    """Sample weight vectors on the simplex with a Dirichlet distribution."""
    validate_weights(base_weights)
    alpha = np.array([base_weights[k] for k in DIMENSIONS], dtype=float)*float(concentration)
    rng = np.random.default_rng(seed)
    W = rng.dirichlet(alpha, size=int(n))
    x = np.array([values[k] for k in DIMENSIONS], dtype=float)
    scores = W @ x
    states = np.select([scores<.20,scores<.35,scores<.50,scores<.65],[0,1,2,3],default=4).astype(int)
    return W, scores, states
