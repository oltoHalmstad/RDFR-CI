from rdfr_ci.authority import AuthorityState
from rdfr_ci.gates import final_authority

PASS={'G_S':'pass','G_V':'pass','G_FA':'pass','G_A':'pass','G_H':'pass'}

def test_failed_gate_cannot_increase_authority():
    final,_=final_authority(AuthorityState.ASSISTED_DEFENSE,{**PASS,'G_S':'fail'})
    assert int(final)>=int(AuthorityState.ASSISTED_DEFENSE)

def test_unevaluated_conservative():
    final,binding=final_authority(AuthorityState.BOUNDED_AUTOMATION,{**PASS,'G_A':'not_evaluated'})
    assert final==AuthorityState.SHADOW_RESTRICTED and binding=='G_A'

def test_not_applicable_does_not_cap():
    final,binding=final_authority(AuthorityState.BOUNDED_AUTOMATION,{**PASS,'G_A':'not_applicable'})
    assert final==AuthorityState.BOUNDED_AUTOMATION and binding=='Score'
