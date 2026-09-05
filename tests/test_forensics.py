import pytest
from rdfr_ci.forensic import forensic_quality,forensic_risk

def test_forensic_complement():
    q=forensic_quality(.9,.8,.7,.6,.5); f=forensic_risk(.9,.8,.7,.6,.5)
    assert f==pytest.approx(1-q)
    assert 0<=f<=1
