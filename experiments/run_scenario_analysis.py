#!/usr/bin/env python3
from pathlib import Path
import argparse,json,sys,pandas as pd
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(HERE))
from common import write_df
from rdfr_ci.scenario_loader import load_catalog
from rdfr_ci.risk import composite_risk
from rdfr_ci.authority import authority_from_score,label,boundary_margin
from rdfr_ci.gates import final_authority
from rdfr_ci.uncertainty import simulate_state_distribution
EXPECTED={'CDI-001':.1705,'MFG-001':.3055,'SUB-001':.3385,'RAIL-001':.3705,'HOSP-001':.4195,'WATER-001':.5000}
TABLE11={'CDI-001':{},'MFG-001':{'G_H':'unknown'},'SUB-001':{'G_S':'unknown','G_H':'unknown'},'RAIL-001':{},'HOSP-001':{},'WATER-001':{'G_A':'unknown'}}
EXPECTED_FINAL={'CDI-001':4,'MFG-001':2,'SUB-001':2,'RAIL-001':2,'HOSP-001':2,'WATER-001':1}

def main(n=10000,sigma=.05,seed=42):
    src=ROOT/'scenarios/scenario_catalog_v1.3.yaml';sc=load_catalog(src if src.exists() else ROOT/'scenarios/scenario_catalog.yaml');rows=[];urs=[]
    for i,s in enumerate(sc):
        score=composite_risk(s.E,s.D,s.A,s.F,s.C,s.weights);prov=authority_from_score(score);final,binding=final_authority(prov,s.gate_states,s.gate_caps);u=simulate_state_distribution(s.values(),s.weights,sigma=sigma,n=n,seed=seed+i)
        rows.append({'scenario_id':s.scenario_id,'sector':s.sector,'E':s.E,'D':s.D,'A':s.A,'F':s.F,'C':s.C,'R_CI':score,'provisional_authority':label(prov),'final_authority':label(final),'boundary_margin':boundary_margin(score),'P_point_state':u['p_point_state'],'P_state_change':u['p_state_change'],'binding_constraint':binding,'evidence_class':'ILLUSTRATIVE'});urs.append({'scenario_id':s.scenario_id,**u})
    df=pd.DataFrame(rows);udf=pd.DataFrame(urs);write_df(df,ROOT/'results/tables/table_S1_thirty_scenario_results.csv');write_df(udf,ROOT/'results/sensitivity/decision_uncertainty.csv')
    by={r['scenario_id']:r for r in rows}
    for sid,x in EXPECTED.items(): assert abs(by[sid]['R_CI']-x)<1e-9
    PASS={k:'pass' for k in ('G_S','G_V','G_FA','G_A','G_H')};vr=[]
    for sid,g in TABLE11.items():
        final,binding=final_authority(authority_from_score(by[sid]['R_CI']),{**PASS,**g});assert int(final)==EXPECTED_FINAL[sid];vr.append({'scenario_id':sid,'final_code':int(final),'binding':binding})
    write_df(pd.DataFrame(vr),ROOT/'results/tables/table_11_policy_verification.csv')
    summary={'scenarios':len(df),'sectors':int(df.sector.nunique()),'uncertainty_sigma':sigma,'simulations_per_scenario':n,'manuscript_showcase_scores_verified':True,'manuscript_table_11_policy_verified':True}
    (ROOT/'results/scenario_results').mkdir(parents=True,exist_ok=True);(ROOT/'results/scenario_results/summary_v1.3.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary,indent=2));return df,udf
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--n',type=int,default=10000);ap.add_argument('--sigma',type=float,default=.05);ap.add_argument('--seed',type=int,default=42);a=ap.parse_args();main(a.n,a.sigma,a.seed)
