import pytest
from rdfr_ci.authority import AuthorityState,authority_from_score,boundary_margin,authority_ceiling

def test_exact_half_open_boundaries():
    assert authority_from_score(.199999)==AuthorityState.BOUNDED_AUTOMATION
    assert authority_from_score(.20)==AuthorityState.HUMAN_APPROVED
    assert authority_from_score(.35)==AuthorityState.ASSISTED_DEFENSE
    assert authority_from_score(.50)==AuthorityState.SHADOW_RESTRICTED
    assert authority_from_score(.65)==AuthorityState.ROLLBACK_ISOLATION

def test_boundary_margin(): assert boundary_margin(.50)==pytest.approx(0)
def test_authority_ceiling():
    r,s=authority_ceiling(.80,.25); assert r==pytest.approx(.20); assert s==AuthorityState.HUMAN_APPROVED
