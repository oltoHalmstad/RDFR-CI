
"""Cyber-physical consequence and cascading risk (Manuscript Section 3.7, Eq. 9)."""
from __future__ import annotations
DEFAULT_BETA = {"H":0.30, "V":0.25, "K":0.20, "T":0.10, "R_c":0.15}

def consequence_risk(H: float, V: float, K: float, T: float, R_c: float, beta=None) -> float:
    """Calculate C = beta1*H + beta2*V + beta3*K + beta4*T + beta5*R_c.

    C is the consequence if the *defensive action is wrong*, not simply the
    consequence of a successful attack. The beta vector must be recorded with results.
    """
    beta = DEFAULT_BETA if beta is None else beta
    names = ("H","V","K","T","R_c")
    if any(k not in beta for k in names) or abs(sum(float(beta[k]) for k in names)-1.0) > 1e-9:
        raise ValueError("beta must define H, V, K, T and R_c weights summing to 1")
    vals = dict(zip(names,(H,V,K,T,R_c)))
    if any(not 0 <= float(v) <= 1 for v in vals.values()):
        raise ValueError("consequence inputs must lie in [0,1]")
    return float(sum(float(beta[k])*float(vals[k]) for k in names))
