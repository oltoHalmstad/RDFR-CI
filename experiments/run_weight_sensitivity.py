#!/usr/bin/env python3
from pathlib import Path
import json,sys
import numpy as np,pandas as pd
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'src')); sys.path.insert(0,str(HERE))
from common import write_df
from rdfr_ci.scenario_loader import load_catalog
from rdfr_ci.uncertainty import dirichlet_weight_sensitivity
from rdfr_ci.authority import authority_from_score

def main(n=5000,seed=42):
    rows=[]; sc=load_catalog(ROOT/'scenarios/scenario_catalog.yaml')
    water=None
    for i,s in enumerate(sc):
        W,scores,states=dirichlet_weight_sensitivity(s.values(),s.weights,n=n,seed=seed+i)
        point=int(authority_from_score(sum(s.weights[k]*s.values()[k] for k in ('E','D','A','F','C'))))
        rows.append({'scenario_id':s.scenario_id,'draws':n,'point_state_rank':point,'P_same_state':float((states==point).mean()),'P_more_restrictive':float((states>point).mean()),'P_more_permissive':float((states<point).mean()),'score_mean':float(scores.mean()),'score_p05':float(np.quantile(scores,.05)),'score_p95':float(np.quantile(scores,.95)),'corr_wC_score':float(np.corrcoef(W[:,4],scores)[0,1])})
        if s.scenario_id=='WATER-001': water=(W,scores)
    df=pd.DataFrame(rows); write_df(df,ROOT/'results/sensitivity/weight_sensitivity.csv')
    if water:
        W,scores=water; fig,ax=plt.subplots(figsize=(7,5)); ax.scatter(W[:,4],scores,s=5,alpha=.25); ax.set(xlabel='Sampled w_C',ylabel='R_CI',title='Weight sensitivity: water-treatment showcase'); ax.grid(alpha=.2); fig.savefig(ROOT/'results/figures/figure_S2_weight_sensitivity_wc.png',dpi=300,bbox_inches='tight'); fig.savefig(ROOT/'results/figures/figure_S2_weight_sensitivity_wc.pdf',bbox_inches='tight'); plt.close(fig)
    return df
if __name__=='__main__': main()
