import pytest
from rdfr_ci.risk import composite_risk,validate_weights,DEFAULT_WEIGHTS

def test_default_weights_sum_to_one(): validate_weights(DEFAULT_WEIGHTS)

def test_composite_in_range():
    x=composite_risk(.3,.1,.08,.08,.25); assert 0<=x<=1; assert x==pytest.approx(.1705)

def test_bad_weights_rejected():
    with pytest.raises(ValueError): validate_weights({'E':.2,'D':.2,'A':.2,'F':.2,'C':.3})
