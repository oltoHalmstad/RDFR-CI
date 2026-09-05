
"""Forensic readiness and accountability risk (Manuscript Section 3.6, Eqs. 7-8)."""
from __future__ import annotations
DEFAULT_ETA = {"EC":0.20, "PC":0.20, "TI":0.20, "CC":0.20, "RW":0.20}

def forensic_quality(ec: float, pc: float, ti: float, cc: float, rw: float, eta=None) -> float:
    """Calculate Q_F = eta1*EC + eta2*PC + eta3*TI + eta4*CC + eta5*RW."""
    eta = DEFAULT_ETA if eta is None else eta
    names = ("EC","PC","TI","CC","RW")
    if any(k not in eta for k in names) or abs(sum(float(eta[k]) for k in names)-1.0) > 1e-9:
        raise ValueError("eta must define EC, PC, TI, CC and RW weights summing to 1")
    vals = dict(zip(names,(ec,pc,ti,cc,rw)))
    if any(not 0 <= float(v) <= 1 for v in vals.values()):
        raise ValueError("forensic quality inputs must lie in [0,1]")
    return float(sum(float(eta[k])*float(vals[k]) for k in names))

def forensic_risk(ec: float, pc: float, ti: float, cc: float, rw: float, eta=None) -> float:
    """Calculate F = 1 - Q_F."""
    return 1.0 - forensic_quality(ec, pc, ti, cc, rw, eta)
