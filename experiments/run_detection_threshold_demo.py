#!/usr/bin/env python3
from pathlib import Path
import sys
import numpy as np,pandas as pd
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(HERE))
from common import write_df
from rdfr_ci.detection import threshold_sweep,select_global_f1,select_authority_point
from rdfr_ci.authority import authority_from_score,label
from rdfr_ci.plotting import detection_threshold_figure

def generate(seed=42):
    rng=np.random.default_rng(seed);rows=[]
    classes=[('enterprise',1,320,50,.18,.78),('engineering',3,180,40,.20,.70),('safety_instrumented',10,120,30,.22,.58)]
    for name,q,nneg,npos,mu0,mu1 in classes:
        neg=np.clip(rng.normal(mu0,.11,nneg),0,1);pos=np.clip(rng.normal(mu1,.16,npos),0,1)
        rows += [(0,float(s),name,q) for s in neg] + [(1,float(s),name,q) for s in pos]
    return pd.DataFrame(rows,columns=['label','score','asset_class','criticality_weight'])

def main(seed=42):
    df=generate(seed);(ROOT/'data/synthetic').mkdir(parents=True,exist_ok=True);df.to_csv(ROOT/'data/synthetic/detection_scores.csv',index=False)
    vals=['enterprise','engineering','safety_instrumented'];q=[1,3,10]
    pts=threshold_sweep(df.label.to_numpy(),df.score.to_numpy(),df.asset_class.to_numpy(),vals,q,np.linspace(0,1,201))
    rows=[p.__dict__ for p in pts];write_df(pd.DataFrame(rows),ROOT/'results/sensitivity/detection_threshold_sweep.csv')
    f1=select_global_f1(pts);auth=select_authority_point(pts,.05)
    write_df(pd.DataFrame([{'Operating point':'Global F1 optimum',**f1.__dict__},{'Operating point':'Gap-minimizing point (phi=0.05)',**auth.__dict__}]),ROOT/'results/tables/table_S5_synthetic_detection_operating_points.csv')
    def rci(p): return .324+.20*p.detection_gap
    table=pd.DataFrame([
      ['Detection threshold',f'{f1.threshold:.3f}',f'{auth.threshold:.3f}'],['Global F₁',f'{f1.f1:.3f}',f'{auth.f1:.3f}'],['False-positive rate',f'{f1.fpr:.3f}',f'{auth.fpr:.3f}'],['Criticality-weighted recall',f'{f1.criticality_weighted_recall:.3f}',f'{auth.criticality_weighted_recall:.3f}'],['Detection capability gap D',f'{f1.detection_gap:.3f}',f'{auth.detection_gap:.3f}'],['Composite score RCI',f'{rci(f1):.3f}',f'{rci(auth):.3f}'],['Provisional state',label(authority_from_score(rci(f1))),label(authority_from_score(rci(auth)))]],columns=['Quantity','Global F₁ optimum','Gap-minimizing point (φ = 0.05)'])
    write_df(table,ROOT/'results/tables/table_7_generated.csv')
    out=ROOT/'results/generated_figures/figure_A3_detection_threshold_authority';out.parent.mkdir(parents=True,exist_ok=True);detection_threshold_figure(out,rows)
    return rows
if __name__=='__main__': main()
