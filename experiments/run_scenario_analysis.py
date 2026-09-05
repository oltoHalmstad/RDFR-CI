#!/usr/bin/env python3
"""Reproduce the 30-scenario library, six manuscript showcases and uncertainty results."""
from pathlib import Path
import argparse,json,sys
import pandas as pd

HERE=Path(__file__).resolve().parent; ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'src')); sys.path.insert(0,str(HERE))
from common import write_df
from rdfr_ci.scenario_loader import load_catalog
from rdfr_ci.risk import composite_risk
from rdfr_ci.authority import authority_from_score,label,authority_ceiling,boundary_margin
from rdfr_ci.gates import final_authority
from rdfr_ci.uncertainty import simulate_state_distribution
from rdfr_ci.audit import build_audit
from rdfr_ci.plotting import decision_stability_figure

SHOWCASE_ORDER=['CDI-001','MFG-001','SUB-001','RAIL-001','HOSP-001','WATER-001']
SHOWCASE_LABELS={'CDI-001':'Critical digital infrastructure','MFG-001':'Smart manufacturing','SUB-001':'Electric-grid substation','RAIL-001':'Rail / traffic control','HOSP-001':'Hospital infrastructure','WATER-001':'Water treatment'}

def main(n=10000,sigma=.05,seed=42):
    scenarios=load_catalog(ROOT/'scenarios/scenario_catalog.yaml')
    rows=[]; uncertainties=[]
    audit_dir=ROOT/'results/scenario_results'; audit_dir.mkdir(parents=True,exist_ok=True)
    for i,s in enumerate(scenarios):
        vals=s.values(); score=composite_risk(s.E,s.D,s.A,s.F,s.C,s.weights)
        prov=authority_from_score(score); final,binding=final_authority(prov,s.gate_states,s.gate_caps)
        u=simulate_state_distribution(vals,s.weights,sigma=sigma,n=n,seed=seed+i)
        rmin,best=authority_ceiling(s.C,s.weights['C'])
        row={'scenario_id':s.scenario_id,'title':s.title,'sector':s.sector,**vals,
             'R_CI':score,'provisional_authority':label(prov),'final_authority':label(final),
             'w_C_times_C':rmin,'best_reachable_state':label(best),'boundary_margin':boundary_margin(score),
             'P_point_state':u['p_point_state'],'P_state_change':u['p_state_change'],'binding_constraint':binding,
             'evidence_class':'ILLUSTRATIVE'}
        rows.append(row)
        uncertainties.append({'scenario_id':s.scenario_id,**u})
        audit=build_audit(s,score,label(prov),label(final),binding,u)
        (audit_dir/f'{s.scenario_id}.json').write_text(json.dumps(audit,indent=2,ensure_ascii=False),encoding='utf-8')
    df=pd.DataFrame(rows)
    write_df(df,ROOT/'results/tables/table_S1_thirty_scenario_results.csv')
    udf=pd.DataFrame(uncertainties)
    write_df(udf,ROOT/'results/sensitivity/decision_uncertainty.csv')
    decision_stability_figure(ROOT/'results/figures/figure_A2_decision_stability',uncertainties)
    six=df.set_index('scenario_id').loc[SHOWCASE_ORDER].reset_index().copy()
    six.insert(1,'Showcase',[SHOWCASE_LABELS[x] for x in SHOWCASE_ORDER])
    cols=['Showcase','E','D','A','F','C','R_CI','w_C_times_C','boundary_margin','P_point_state','binding_constraint','final_authority']
    write_df(six[cols],ROOT/'results/tables/table_10_six_sector_showcases.csv')
    summary={'scenarios':len(df),'sectors':int(df.sector.nunique()),'score_binding':int((df.binding_constraint=='Score').sum()),
             'gate_binding':int((df.binding_constraint!='Score').sum()),'most_common_gate_binding':df.loc[df.binding_constraint!='Score','binding_constraint'].value_counts().index[0],
             'uncertainty_sigma':sigma,'simulations_per_scenario':n}
    (ROOT/'results/scenario_results/summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))
    return df,udf

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--n',type=int,default=10000); ap.add_argument('--sigma',type=float,default=.05); ap.add_argument('--seed',type=int,default=42)
    a=ap.parse_args(); main(a.n,a.sigma,a.seed)
