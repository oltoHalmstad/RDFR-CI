"""Action-specific non-transitive authority for manuscript Section 3.11 / Eq. (12)."""
from __future__ import annotations
from typing import Iterable, Mapping, Any
from .authority import AuthorityState
from .gates import final_authority

def capability_intersection(parent_delegable: Iterable[str], child_requested: Iterable[str], policy_allowed: Iterable[str]):
    """Return the explicit capability intersection required by Section 3.11."""
    return frozenset(parent_delegable) & frozenset(child_requested) & frozenset(policy_allowed)

def child_authority(
    parent_authority: AuthorityState | int,
    child_risk_authority: AuthorityState | int,
    child_scope_cap: AuthorityState | int,
    gate_states: Mapping[str, Any],
    gate_caps=None,
    *,
    priority_prohibition: bool = False,
    capability_scope_authorized: bool = True,
):
    """Apply the numerical cap in Equation (12)."""
    parent = AuthorityState(int(parent_authority))
    local = AuthorityState(int(child_risk_authority))
    scope = AuthorityState(int(child_scope_cap))
    starting = AuthorityState(min(int(parent), int(local), int(scope)))
    return final_authority(starting, gate_states, gate_caps,
        priority_prohibition=priority_prohibition,
        capability_scope_authorized=capability_scope_authorized)
