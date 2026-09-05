import pytest,numpy as np
from rdfr_ci.detection import detection_gap,threshold_sweep,select_global_f1,select_authority_point

def test_detection_gap():
    assert detection_gap([.9,.6],[1,3])==pytest.approx(1-(.9+1.8)/4)

def test_threshold_selection_runs():
    y=np.array([0,0,0,1,1,1]); s=np.array([.1,.2,.8,.4,.7,.9]); c=np.array(['a','a','a','b','b','b'])
    pts=threshold_sweep(y,s,c,['a','b'],[1,10],thresholds=np.linspace(0,1,11))
    assert 0<=select_global_f1(pts).f1<=1
    assert select_authority_point(pts,.5).fpr<=.5+1e-12
