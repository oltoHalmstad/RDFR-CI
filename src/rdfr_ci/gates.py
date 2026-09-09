"""Independent deployment gates for manuscript Section 3.8 / Equation (10)."""
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

DEFAULT_UNKNOWN_CAPS = {"G_S":2,"G_V":2,"G_FA":2,"G_A":1,"G_H":2}
DEFAULT_FAILURE_CAPS = {"G_S":0,"G_V":0,"G_FA":2,"G_A":1,"G_H":0}

@dataclass(frozen=True)
class GateDecision:
    name: str
    status: GateStatus | str
    cap: AuthorityState | int | None = None
    prohibited: bool = False
    rationale: str = ""
    evidence_reference: str = ""

def _status(value: Any) -> GateStatus:
    if isinstance(value,GateStatus): return value
    text=str(value).strip().lower()
    if text=="not_evaluated": text="unknown"
    return GateStatus(text)

def _decision(name: str, value: Any, legacy_caps=None) -> GateDecision:
    if isinstance(value,GateDecision):
        return value if value.name==name else GateDecision(name,value.status,value.cap,value.prohibited,value.rationale,value.evidence_reference)
    st=_status(value); cap=None
    # Legacy callers pass a gate_caps dictionary. In v1.3 those values are used
    # only for unresolved/failed gates; PASS must not silently become a cap.
    if legacy_caps and name in legacy_caps and st in (GateStatus.UNKNOWN,GateStatus.FAIL):
        cap=AuthorityState(int(legacy_caps[name]))
    return GateDecision(name,st,cap)

def _cap_for(d: GateDecision) -> AuthorityState:
    st=_status(d.status)
    if st==GateStatus.PASS:
        return AuthorityState.BOUNDED_AUTOMATION if d.cap is None else AuthorityState(int(d.cap))
    if st==GateStatus.NOT_APPLICABLE:
        return AuthorityState.BOUNDED_AUTOMATION
    if st==GateStatus.UNKNOWN:
        return AuthorityState(int(d.cap)) if d.cap is not None else AuthorityState(DEFAULT_UNKNOWN_CAPS[d.name])
    return AuthorityState(int(d.cap)) if d.cap is not None else AuthorityState(DEFAULT_FAILURE_CAPS[d.name])

def final_authority(provisional, gate_states: Mapping[str,Any], gate_caps=None, *, priority_prohibition=False, capability_scope_authorized=True):
    """Apply the priority stop and then the minimum in Equation (10)."""
    provisional=AuthorityState(int(provisional))
    if priority_prohibition: return AuthorityState.ROLLBACK_ISOLATION,"Priority prohibition"
    if not capability_scope_authorized: return AuthorityState.ROLLBACK_ISOLATION,"Capability scope"
    candidates=[(int(provisional),"Score")]
    for name in ("G_S","G_V","G_FA","G_A","G_H"):
        d=_decision(name,gate_states.get(name,GateDecision(name,GateStatus.UNKNOWN)),gate_caps)
        if d.prohibited: return AuthorityState.ROLLBACK_ISOLATION,name
        candidates.append((int(_cap_for(d)),name))
    min_level=min(v for v,_ in candidates)
    binding="Score" if int(provisional)==min_level else next(n for v,n in candidates if v==min_level and n!="Score")
    return AuthorityState(min_level),binding

def gate_audit(provisional,gate_states,gate_caps=None,**kwargs):
    final,binding=final_authority(provisional,gate_states,gate_caps,**kwargs)
    return {"provisional":label(provisional),"final":label(final),"binding_constraint":binding}
