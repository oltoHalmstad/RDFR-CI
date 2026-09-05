
"""Independent deployment gates (Manuscript Section 3.8, Eq. 10)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Mapping
from .authority import AuthorityState, label

class GateStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    NOT_EVALUATED = "not_evaluated"
    NOT_APPLICABLE = "not_applicable"

DEFAULT_GATE_CAPS = {
    "G_S": AuthorityState.HUMAN_APPROVED,
    "G_V": AuthorityState.HUMAN_APPROVED,
    "G_FA": AuthorityState.ASSISTED_DEFENSE,
    "G_A": AuthorityState.SHADOW_RESTRICTED,
    "G_H": AuthorityState.ASSISTED_DEFENSE,
}

@dataclass(frozen=True)
class GateDecision:
    name: str
    status: GateStatus
    cap: AuthorityState
    rationale: str = ""
    evidence_reference: str = ""

def _status(value) -> GateStatus:
    return value if isinstance(value, GateStatus) else GateStatus(str(value))

def final_authority(provisional: AuthorityState | int, gate_states: Mapping[str, str | GateStatus],
                    gate_caps: Mapping[str, int | AuthorityState] | None = None):
    """Apply gate caps without allowing any gate to increase authority.

    The manuscript writes Authority_final = min(...) on an authority/permissiveness
    scale. This implementation stores states as *restriction ranks* where 0 is the most
    permissive and 4 the most restrictive, as specified in the supplement instructions.
    Therefore the mathematically equivalent operation is max(restriction ranks).

    PASS and NOT_APPLICABLE impose no cap. FAIL and NOT_EVALUATED impose the
    configured cap; unevaluated is conservative by design.
    """
    provisional = AuthorityState(int(provisional))
    caps = dict(DEFAULT_GATE_CAPS)
    if gate_caps:
        caps.update({k: AuthorityState(int(v)) for k,v in gate_caps.items()})
    candidates = [(int(provisional), "Score")]
    for name in ("G_S","G_V","G_FA","G_A","G_H"):
        st = _status(gate_states.get(name, GateStatus.NOT_EVALUATED))
        if st in (GateStatus.FAIL, GateStatus.NOT_EVALUATED):
            candidates.append((int(caps[name]), name))
    max_rank = max(v for v,_ in candidates)
    # Prefer Score when a gate only ties the provisional state; this keeps the
    # manuscript's binding-constraint convention for the water showcase.
    if int(provisional) == max_rank:
        binding = "Score"
    else:
        binding = next(name for v,name in candidates if v == max_rank and name != "Score")
    return AuthorityState(max_rank), binding

def gate_audit(provisional, gate_states, gate_caps=None):
    final, binding = final_authority(provisional, gate_states, gate_caps)
    return {"provisional": label(provisional), "final": label(final), "binding_constraint": binding}
