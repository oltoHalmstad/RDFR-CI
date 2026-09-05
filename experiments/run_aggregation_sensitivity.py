#!/usr/bin/env python3
from pathlib import Path
import json,sys,pandas as pd
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'src')); sys.path.insert(0,str(HERE))
from common import write_df
from rdfr_ci.scenario_loader import load_catalog
from rdfr_ci.aggregation import weighted_arithmetic,weighted_power_mean,worst_dimension_blend
from rdfr_ci.authority import authority_from_score,label

def main():
    rows=[]
    for s in load_catalog(ROOT/'scenarios/scenario_catalog.yaml'):
        v=s.values(); w=s.weights
        scores={'arithmetic':weighted_arithmetic(v,w),'power_mean_rho_2':weighted_power_mean(v,w,2),'power_mean_rho_3':weighted_power_mean(v,w,3),'worst_30pct_blend':worst_dimension_blend(v,w,.70)}
        states={k:label(authority_from_score(x)) for k,x in scores.items()}
        changed=any(states[k]!=states['arithmetic'] for k in states if k!='arithmetic')
        rows.append({'scenario_id':s.scenario_id,**{f'{k}_score':v for k,v in scores.items()},**{f'{k}_state':v for k,v in states.items()},'changed_under_any_alternative':changed})
    df=pd.DataFrame(rows); write_df(df,ROOT/'results/sensitivity/aggregation_sensitivity.csv')
    counts={k:int((df[f'{k}_state']!=df['arithmetic_state']).sum()) for k in ['power_mean_rho_2','power_mean_rho_3','worst_30pct_blend']}
    summary={'changed_under_at_least_one':int(df.changed_under_any_alternative.sum()),'total':len(df),'operator_change_counts':counts,'interpretation':'Sensitivity analysis only; no operator is claimed to be universally correct.'}
    (ROOT/'results/sensitivity/aggregation_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2)); return df
if __name__=='__main__': main()
