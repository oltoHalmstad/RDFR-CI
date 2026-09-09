from rdfr_ci.authority import AuthorityState
from rdfr_ci.gates import GateDecision, GateStatus, final_authority
PASS={k:'pass' for k in ('G_S','G_V','G_FA','G_A','G_H')}

def test_unknown_caps_match_table_3():
    final,binding=final_authority(4,{**PASS,'G_A':'unknown'}); assert final==AuthorityState.SHADOW_RESTRICTED and binding=='G_A'
    final,binding=final_authority(4,{**PASS,'G_S':'unknown'}); assert final==AuthorityState.ASSISTED_DEFENSE and binding=='G_S'

def test_not_applicable_does_not_cap():
    final,binding=final_authority(4,{**PASS,'G_A':'not_applicable'}); assert final==AuthorityState.BOUNDED_AUTOMATION and binding=='Score'

def test_priority_prohibition_precedes_minimum():
    final,binding=final_authority(4,PASS,priority_prohibition=True); assert final==AuthorityState.ROLLBACK_ISOLATION and binding=='Priority prohibition'
    final,binding=final_authority(4,PASS,capability_scope_authorized=False); assert final==AuthorityState.ROLLBACK_ISOLATION and binding=='Capability scope'

def test_compromised_ai_enforcement_can_be_explicit_stop():
    gates={**PASS,'G_A':GateDecision('G_A',GateStatus.FAIL,prohibited=True)}
    final,binding=final_authority(4,gates); assert final==AuthorityState.ROLLBACK_ISOLATION and binding=='G_A'

def test_valid_action_bound_human_approval_caps_at_three():
    gates={**PASS,'G_H':GateDecision('G_H',GateStatus.PASS,cap=AuthorityState.HUMAN_APPROVED)}
    final,binding=final_authority(4,gates); assert final==AuthorityState.HUMAN_APPROVED and binding=='G_H'
