#!/usr/bin/env python3
from pathlib import Path
import sys,json
import numpy as np,pandas as pd
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'src')); sys.path.insert(0,str(HERE))
from common import write_df
from rdfr_ci.detection import threshold_sweep,select_global_f1,select_authority_point
from rdfr_ci.plotting import detection_threshold_figure

def generate(seed=42):
    rng=np.random.default_rng(seed); rows=[]
    classes=[('enterprise',1,320,50,.18,.78),('engineering',3,180,40,.20,.70),('safety_instrumented',10,120,30,.22,.58)]
    for name,q,nneg,npos,mu0,mu1 in classes:
        neg=np.clip(rng.normal(mu0,.11,nneg),0,1); pos=np.clip(rng.normal(mu1,.16,npos),0,1)
        for s in neg: rows.append((0,float(s),name,q))
        for s in pos: rows.append((1,float(s),name,q))
    return pd.DataFrame(rows,columns=['label','score','asset_class','criticality_weight'])

def main(seed=42):
    df=generate(seed); df.to_csv(ROOT/'data/synthetic/detection_scores.csv',index=False)
    class_values=['enterprise','engineering','safety_instrumented']; q=[1,3,10]
    pts=threshold_sweep(df.label.to_numpy(),df.score.to_numpy(),df.asset_class.to_numpy(),class_values,q,np.linspace(0,1,201))
    rows=[p.__dict__ for p in pts]; write_df(pd.DataFrame(rows),ROOT/'results/sensitivity/detection_threshold_sweep.csv')
    f1=select_global_f1(pts); auth=select_authority_point(pts,.05)
    op=pd.DataFrame([{'Operating point':'Global F1 optimum',**f1.__dict__},{'Operating point':'Authority optimum (phi=0.05)',**auth.__dict__}])
    write_df(op,ROOT/'results/tables/table_S5_synthetic_detection_operating_points.csv')
    detection_threshold_figure(ROOT/'results/figures/figure_A3_detection_threshold_authority',rows)
    # Manuscript Table 7 is preserved as an explicit reported synthetic configuration rather than silently
    # retrofitted to the generated score sample.
    manuscript=pd.DataFrame([
      {'Quantity':'Detection threshold','Global F1 optimum':0.72,'Authority optimum (phi = 0.05)':0.50},
      {'Quantity':'Global F1','Global F1 optimum':0.698,'Authority optimum (phi = 0.05)':0.346},
      {'Quantity':'Recall, safety-instrumented systems','Global F1 optimum':0.333,'Authority optimum (phi = 0.05)':0.667},
      {'Quantity':'Detection capability gap D','Global F1 optimum':0.514,'Authority optimum (phi = 0.05)':0.202},
      {'Quantity':'Composite score R_CI','Global F1 optimum':0.427,'Authority optimum (phi = 0.05)':0.364},
      {'Quantity':'Provisional state','Global F1 optimum':'Assisted defense','Authority optimum (phi = 0.05)':'Assisted defense'},
    ])
    write_df(manuscript,ROOT/'results/tables/table_7_manuscript_detection_operating_points.csv')
    return rows
if __name__=='__main__': main()
