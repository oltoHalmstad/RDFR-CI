
"""Non-transitive authority for agentic and multi-agent operation (Manuscript Section 3.11, Eq. 12)."""
from __future__ import annotations
from .authority import AuthorityState
from .gates import final_authority

def child_authority(parent_authority: AuthorityState | int,
                    child_scope_cap: AuthorityState | int,
                    gate_states, gate_caps=None):
    """Return the most restrictive of parent, child scope and applicable gate caps.

    Because AuthorityState is stored as a restriction rank (0 permissive, 4 restrictive),
    a child can only inherit the same or a more restrictive rank. Delegation therefore
    cannot create authority escalation.
    """
    parent = AuthorityState(int(parent_authority))
    scope = AuthorityState(int(child_scope_cap))
    starting = AuthorityState(max(int(parent), int(scope)))
    return final_authority(starting, gate_states, gate_caps)
