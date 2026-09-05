import pytest
from rdfr_ci.ai_risk import ai_specific_risk,assurance_gate_trigger

def test_ai_risk(): assert ai_specific_risk(.2,.4,.1,.3)==pytest.approx(.25)
def test_hard_trigger():
    assert assurance_gate_trigger(['prompt_injection'])
    assert not assurance_gate_trigger(['model_drift'])
