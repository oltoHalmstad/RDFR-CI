#!/usr/bin/env python3
from pathlib import Path
import json,sys,pandas as pd
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(HERE))
from common import write_df
from rdfr_ci.agent_authority import child_authority,capability_intersection
from rdfr_ci.authority import label
PASS={k:'pass' for k in ('G_S','G_V','G_FA','G_A','G_H')}
DEMOS=[('Permissive parent, stricter child-local risk',4,3,4,PASS),('Permissive parent, restricted child scope',4,4,2,PASS),('Unknown AI assurance on delegated action',4,4,4,{**PASS,'G_A':'unknown'})]

def main():
    rows=[];events=[]
    for i,(name,parent,local,scope,gates) in enumerate(DEMOS,1):
        final,binding=child_authority(parent,local,scope,gates)
        rows.append({'demo_id':i,'demonstration':name,'parent_authority':label(parent),'child_local_risk_authority':label(local),'child_scope_cap':label(scope),'final_child_authority':label(final),'binding_constraint':binding,'evidence_class':'SYNTHETIC'})
        events.append({'demo_id':i,'event':'authority_decision','parent':label(parent),'child_local_risk':label(local),'child_scope':label(scope),'gate_states':gates,'decision':label(final),'binding_constraint':binding})
    write_df(pd.DataFrame(rows),ROOT/'results/tables/table_S3_agent_authority_demo.csv')
    p=ROOT/'results/logs/agent_authority_events.jsonl';p.parent.mkdir(parents=True,exist_ok=True);p.write_text('\n'.join(json.dumps(x) for x in events)+'\n',encoding='utf-8')
    assert capability_intersection({'search','simulate','block'},{'simulate','block','plc_write'},{'search','simulate'})==frozenset({'simulate'})
    return rows
if __name__=='__main__': main()
