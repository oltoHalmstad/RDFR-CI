#!/usr/bin/env python3
from pathlib import Path
import sys,numpy as np,pandas as pd
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(HERE))
from common import write_df
from rdfr_ci.scenario_loader import load_catalog
from rdfr_ci.uncertainty import dirichlet_weight_sensitivity
from rdfr_ci.authority import authority_from_score

def main(n=5000,seed=42):
    src=ROOT/'scenarios/scenario_catalog_v1.3.yaml';sc=load_catalog(src if src.exists() else ROOT/'scenarios/scenario_catalog.yaml');rows=[]
    for i,s in enumerate(sc):
        W,scores,states=dirichlet_weight_sensitivity(s.values(),s.weights,n=n,seed=seed+i)
        point=int(authority_from_score(sum(s.weights[k]*s.values()[k] for k in ('E','D','A','F','C'))))
        rows.append({'scenario_id':s.scenario_id,'draws':n,'point_state_code':point,'P_same_state':float((states==point).mean()),'P_more_restrictive':float((states<point).mean()),'P_more_permissive':float((states>point).mean()),'score_mean':float(scores.mean()),'score_p05':float(np.quantile(scores,.05)),'score_p95':float(np.quantile(scores,.95)),'corr_wC_score':float(np.corrcoef(W[:,4],scores)[0,1])})
    df=pd.DataFrame(rows);write_df(df,ROOT/'results/sensitivity/weight_sensitivity.csv');return df
if __name__=='__main__': main()
