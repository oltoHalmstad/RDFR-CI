import pytest
from rdfr_ci.consequence import consequence_risk,DEFAULT_BETA

def test_consequence_equal_components_reproduce_value():
    assert consequence_risk(.75,.75,.75,.75,.75,DEFAULT_BETA)==pytest.approx(.75)
