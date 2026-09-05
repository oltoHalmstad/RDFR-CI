from rdfr_ci.uncertainty import simulate_state_distribution
from rdfr_ci.risk import DEFAULT_WEIGHTS

def test_identical_seed_reproduces():
    v={'E':.55,'D':.35,'A':.30,'F':.25,'C':.90}
    a=simulate_state_distribution(v,DEFAULT_WEIGHTS,n=1000,seed=42)
    b=simulate_state_distribution(v,DEFAULT_WEIGHTS,n=1000,seed=42)
    assert a==b

def test_probabilities_sum_to_one():
    v={'E':.3,'D':.1,'A':.08,'F':.08,'C':.25}; r=simulate_state_distribution(v,DEFAULT_WEIGHTS,n=500,seed=1)
    p=sum(r[k] for k in ['p_bounded','p_human_approved','p_assisted','p_shadow','p_rollback'])
    assert abs(p-1)<1e-12
