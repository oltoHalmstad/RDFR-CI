from rdfr_ci.authority import AuthorityState
from rdfr_ci.agent_authority import child_authority, capability_intersection
PASS={k:'pass' for k in ('G_S','G_V','G_FA','G_A','G_H')}

def test_child_is_capped_by_parent_local_risk_and_scope():
    assert child_authority(4,3,4,PASS)[0] == AuthorityState.HUMAN_APPROVED
    assert child_authority(4,4,2,PASS)[0] == AuthorityState.ASSISTED_DEFENSE
    assert child_authority(3,4,4,PASS)[0] == AuthorityState.HUMAN_APPROVED

def test_capability_intersection_is_explicit():
    assert capability_intersection({'search','simulate','block'},{'simulate','block','plc_write'},{'search','simulate'}) == frozenset({'simulate'})

def test_scope_failure_is_priority_stop():
    final,binding=child_authority(4,4,4,PASS,capability_scope_authorized=False); assert final==AuthorityState.ROLLBACK_ISOLATION and binding=='Capability scope'
