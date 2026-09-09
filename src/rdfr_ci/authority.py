"""RDFR-CI canonical authority scale, score bands, margins, and score floor.

Version 1.3.0 uses the same ordered scale as manuscript Table 4:
0 = Rollback/isolation (least permission), 4 = Bounded automation (most permission).
"""
from __future__ import annotations
from enum import IntEnum
import math

class AuthorityState(IntEnum):
    ROLLBACK_ISOLATION = 0
    SHADOW_RESTRICTED = 1
    ASSISTED_DEFENSE = 2
    HUMAN_APPROVED = 3
    BOUNDED_AUTOMATION = 4

STATE_LABELS = {
    AuthorityState.ROLLBACK_ISOLATION: "Rollback / isolation",
    AuthorityState.SHADOW_RESTRICTED: "Shadow / restricted",
    AuthorityState.ASSISTED_DEFENSE: "Assisted defense",
    AuthorityState.HUMAN_APPROVED: "Human-approved intervention",
    AuthorityState.BOUNDED_AUTOMATION: "Bounded automation",
}
BOUNDARIES = (0.20, 0.35, 0.50, 0.65)

def authority_from_score(score: float) -> AuthorityState:
    """Map R_CI to the manuscript's half-open provisional bands exactly."""
    x = float(score)
    if not math.isfinite(x) or not 0 <= x <= 1:
        raise ValueError("score must lie in [0,1]")
    if x < 0.20:
        return AuthorityState.BOUNDED_AUTOMATION
    if x < 0.35:
        return AuthorityState.HUMAN_APPROVED
    if x < 0.50:
        return AuthorityState.ASSISTED_DEFENSE
    if x < 0.65:
        return AuthorityState.SHADOW_RESTRICTED
    return AuthorityState.ROLLBACK_ISOLATION

def boundary_margin(score: float) -> float:
    x = float(score)
    if not 0 <= x <= 1:
        raise ValueError("score must lie in [0,1]")
    return float(min(abs(x - b) for b in BOUNDARIES))

def authority_ceiling(C: float, w_C: float = 0.25):
    """Return the conditional score floor R_min=w_C*C and best provisional state (Eq. 11)."""
    if not 0 <= float(C) <= 1 or not 0 <= float(w_C) <= 1:
        raise ValueError("C and w_C must lie in [0,1]")
    r_min = float(C) * float(w_C)
    return r_min, authority_from_score(r_min)

def label(state: AuthorityState | int) -> str:
    return STATE_LABELS[AuthorityState(int(state))]
