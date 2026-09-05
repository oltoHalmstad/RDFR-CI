#!/usr/bin/env python3
"""Synthetic inter-rater demonstration near authority boundaries."""
from pathlib import Path
import sys,numpy as np,pandas as pd
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'src')); sys.path.insert(0,str(HERE))
from common import write_df
from rdfr_ci.authority import authority_from_score,label
from rdfr_ci.risk import DEFAULT_WEIGHTS

def icc2_1(matrix):
    """Two-way random-effects absolute-agreement ICC(2,1). Rows=targets, columns=raters."""
    X=np.asarray(matrix,float); n,k=X.shape
    gm=X.mean(); rowm=X.mean(1); colm=X.mean(0)
    ssr=k*((rowm-gm)**2).sum(); ssc=n*((colm-gm)**2).sum(); sse=((X-rowm[:,None]-colm[None,:]+gm)**2).sum()
    msr=ssr/(n-1); msc=ssc/(k-1); mse=sse/((n-1)*(k-1))
    return float((msr-mse)/(msr+(k-1)*mse+k*(msc-mse)/n))

def main(seed=42):
    rng=np.random.default_rng(seed); roles=['OT engineer','Cybersecurity analyst','Safety/process expert','DFIR expert']
    # Base scenarios intentionally straddle band boundaries while retaining small numeric deviations.
    base_scores=np.array([.198,.202,.347,.353,.497,.503,.647,.653])
    rows=[]; score_matrix=[]
    for j,base in enumerate(base_scores):
        # Convert target score into an equal-dimension base, then add role-specific small perturbations.
        vals=np.repeat(base,5); rater_scores=[]
        for i,role in enumerate(roles):
            delta=rng.normal(0,.006,5)+np.array([-.002,.002,0,.001,-.001])*((i-1.5)/1.5)
            x=np.clip(vals+delta,0,1)
            score=sum(DEFAULT_WEIGHTS[k]*x[m] for m,k in enumerate(('E','D','A','F','C')))
            rater_scores.append(score)
            rows.append({'case_id':f'BOUNDARY-{j+1:02d}','role':role,'E':x[0],'D':x[1],'A':x[2],'F':x[3],'C':x[4],'R_CI':score,'authority_state':label(authority_from_score(score)),'evidence_class':'SYNTHETIC METHODOLOGICAL DEMONSTRATION'})
        score_matrix.append(rater_scores)
    df=pd.DataFrame(rows); write_df(df,ROOT/'results/sensitivity/interrater_demo.csv')
    matrix=np.array(score_matrix); icc=icc2_1(matrix)
    unanimous=[]
    for case,g in df.groupby('case_id'): unanimous.append(g.authority_state.nunique()==1)
    summary=pd.DataFrame([{'ICC_2_1_on_R_CI':icc,'cases':len(unanimous),'unanimous_state_cases':sum(unanimous),'state_agreement_fraction':sum(unanimous)/len(unanimous),'interpretation':'Synthetic demonstration: high numeric agreement can coexist with discrete state disagreement near band boundaries.'}])
    write_df(summary,ROOT/'results/tables/table_S2_interrater_summary.csv')
    return df,summary
if __name__=='__main__': main()
