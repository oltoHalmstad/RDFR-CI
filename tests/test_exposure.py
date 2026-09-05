import pytest
from rdfr_ci.exposure import tail_var_exposure,normalized_exposure

def test_tail_var_exposure_and_saturation():
    assert tail_var_exposure(4,8)==pytest.approx(.5)
    assert tail_var_exposure(12,8)==1.0

def test_normalized_exposure_range():
    x=normalized_exposure(.4,.5,.6,.7,.8); assert 0<=x<=1
