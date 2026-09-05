from rdfr_ci.authority import AuthorityState
from rdfr_ci.agent_authority import child_authority

PASS={'G_S':'pass','G_V':'pass','G_FA':'pass','G_A':'pass','G_H':'pass'}

def test_child_never_exceeds_parent_or_scope():
    final,_=child_authority(AuthorityState.HUMAN_APPROVED,AuthorityState.BOUNDED_AUTOMATION,PASS)
    assert int(final)>=int(AuthorityState.HUMAN_APPROVED)
    final,_=child_authority(AuthorityState.BOUNDED_AUTOMATION,AuthorityState.ASSISTED_DEFENSE,PASS)
    assert final==AuthorityState.ASSISTED_DEFENSE

def test_ai_gate_revokes_authority():
    final,_=child_authority(0,0,{**PASS,'G_A':'fail'})
    assert final==AuthorityState.SHADOW_RESTRICTED
