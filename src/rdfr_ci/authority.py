
"""RDFR-CI authority bands, margins and consequence-driven authority ceiling."""
from __future__ import annotations
from enum import IntEnum
import math

class AuthorityState(IntEnum):
    """Restriction rank: 0 is most permissive; 4 is most restrictive."""
    BOUNDED_AUTOMATION = 0
    HUMAN_APPROVED = 1
    ASSISTED_DEFENSE = 2
    SHADOW_RESTRICTED = 3
    ROLLBACK_ISOLATION = 4

STATE_LABELS = {
    AuthorityState.BOUNDED_AUTOMATION: "Bounded automation",
    AuthorityState.HUMAN_APPROVED: "Human-approved intervention",
    AuthorityState.ASSISTED_DEFENSE: "Assisted defense",
    AuthorityState.SHADOW_RESTRICTED: "Shadow / restricted",
    AuthorityState.ROLLBACK_ISOLATION: "Rollback / isolation",
}
BOUNDARIES = (0.20, 0.35, 0.50, 0.65)

def authority_from_score(score: float) -> AuthorityState:
    """Map R_CI to the manuscript's half-open authority bands exactly."""
    x = float(score)
    if not math.isfinite(x) or not 0 <= x <= 1:
        raise ValueError("score must lie in [0,1]")
    if x < 0.20: return AuthorityState.BOUNDED_AUTOMATION
    if x < 0.35: return AuthorityState.HUMAN_APPROVED
    if x < 0.50: return AuthorityState.ASSISTED_DEFENSE
    if x < 0.65: return AuthorityState.SHADOW_RESTRICTED
    return AuthorityState.ROLLBACK_ISOLATION

def boundary_margin(score: float) -> float:
    """Distance from the score to the nearest authority-band boundary."""
    x = float(score)
    if not 0 <= x <= 1:
        raise ValueError("score must lie in [0,1]")
    return float(min(abs(x-b) for b in BOUNDARIES))

def authority_ceiling(C: float, w_C: float = 0.25):
    """Return R_min=w_C*C and the best reachable authority state (Eq. 11)."""
    if not 0 <= float(C) <= 1 or not 0 <= float(w_C) <= 1:
        raise ValueError("C and w_C must lie in [0,1]")
    r_min = float(C)*float(w_C)
    return r_min, authority_from_score(r_min)

def label(state: AuthorityState | int) -> str:
    return STATE_LABELS[AuthorityState(int(state))]
