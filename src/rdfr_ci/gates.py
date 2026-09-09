"""Independent deployment gates for manuscript Section 3.8 / Equation (10).

The priority prohibition/scope check precedes the minimum.  All caps use the
canonical manuscript authority scale: 0 least permission, 4 most permission.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Any
from .authority import AuthorityState, label

class GateStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    UNKNOWN = "unknown"
    NOT_APPLICABLE = "not_applicable"

DEFAULT_UNKNOWN_CAPS = {
    "G_S": AuthorityState.ASSISTED_DEFENSE,
    "G_V": AuthorityState.ASSISTED_DEFENSE,
    "G_FA": AuthorityState.ASSISTED_DEFENSE,
    "G_A": AuthorityState.SHADOW_RESTRICTED,
    "G_H": AuthorityState.ASSISTED_DEFENSE,
}
DEFAULT_FAILURE_CAPS = {
    "G_S": AuthorityState.ROLLBACK_ISOLATION,
    "G_V": AuthorityState.ROLLBACK_ISOLATION,
    "G_FA": AuthorityState.ASSISTED_DEFENSE,
    "G_A": AuthorityState.SHADOW_RESTRICTED,
    "G_H": AuthorityState.ROLLBACK_ISOLATION,
}

@dataclass(frozen=True)
class GateDecision:
    name: str
    status: GateStatus | str
    cap: AuthorityState | int | None = None
    prohibited: bool = False
    rationale: str = ""
    evidence_reference: str = ""

def _status(value: Any) -> GateStatus:
    if isinstance(value, GateStatus):
        return value
    text = str(value).strip().lower()
    if text == "not_evaluated":
        text = "unknown"
    return GateStatus(text)

def _decision(name: str, value: Any, gate_caps: Mapping[str, int | AuthorityState] | None = None) -> GateDecision:
    if isinstance(value, GateDecision):
        if value.name != name:
            return GateDecision(name=name, status=value.status, cap=value.cap, prohibited=value.prohibited,
                                rationale=value.rationale, evidence_reference=value.evidence_reference)
        return value
    st = _status(value)
    cap = None
    if gate_caps and name in gate_caps:
        cap = AuthorityState(int(gate_caps[name]))
    return GateDecision(name=name, status=st, cap=cap)

def _cap_for(decision: GateDecision) -> AuthorityState:
    st = _status(decision.status)
    if st == GateStatus.PASS:
        return AuthorityState.BOUNDED_AUTOMATION if decision.cap is None else AuthorityState(int(decision.cap))
    if st == GateStatus.NOT_APPLICABLE:
        return AuthorityState.BOUNDED_AUTOMATION
    if st == GateStatus.UNKNOWN:
        return AuthorityState(int(decision.cap)) if decision.cap is not None else DEFAULT_UNKNOWN_CAPS[decision.name]
    return AuthorityState(int(decision.cap)) if decision.cap is not None else DEFAULT_FAILURE_CAPS[decision.name]

def final_authority(
    provisional: AuthorityState | int,
    gate_states: Mapping[str, Any],
    gate_caps: Mapping[str, int | AuthorityState] | None = None,
    *,
    priority_prohibition: bool = False,
    capability_scope_authorized: bool = True,
):
    """Apply Equation (10) and its preceding priority stop rule."""
    provisional = AuthorityState(int(provisional))
    if priority_prohibition:
        return AuthorityState.ROLLBACK_ISOLATION, "Priority prohibition"
    if not capability_scope_authorized:
        return AuthorityState.ROLLBACK_ISOLATION, "Capability scope"
    candidates: list[tuple[int, str]] = [(int(provisional), "Score")]
    for name in ("G_S", "G_V", "G_FA", "G_A", "G_H"):
        raw = gate_states.get(name, GateDecision(name, GateStatus.UNKNOWN))
        d = _decision(name, raw, gate_caps)
        if d.prohibited:
            return AuthorityState.ROLLBACK_ISOLATION, name
        cap = _cap_for(d)
        candidates.append((int(cap), name))
    min_level = min(v for v, _ in candidates)
    if int(provisional) == min_level:
        binding = "Score"
    else:
        binding = next(name for v, name in candidates if v == min_level and name != "Score")
    return AuthorityState(min_level), binding

def gate_audit(provisional, gate_states, gate_caps=None, **kwargs):
    final, binding = final_authority(provisional, gate_states, gate_caps, **kwargs)
    return {"provisional": label(provisional), "final": label(final), "binding_constraint": binding}
