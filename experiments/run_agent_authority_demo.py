#!/usr/bin/env python3
from pathlib import Path
import json,sys,pandas as pd
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'src')); sys.path.insert(0,str(HERE))
from common import write_df
from rdfr_ci.agent_authority import child_authority
from rdfr_ci.authority import AuthorityState,label

PASS={'G_S':'pass','G_V':'pass','G_FA':'pass','G_A':'pass','G_H':'pass'}
DEMOS=[
 {'demo':'High-capability child, low authorization','parent':0,'scope':2,'gates':PASS,'explanation':'Capability does not create execution authority; child scope caps action at Assisted defense.'},
 {'demo':'Individually compliant agents, unsafe combined workflow','parent':0,'scope':0,'gates':{**PASS,'G_S':'fail'},'explanation':'System-level safety failure caps the combined workflow even when local agents pass their own checks.'},
 {'demo':'Authority revoked after AI-assurance failure','parent':1,'scope':0,'gates':{**PASS,'G_A':'fail'},'explanation':'A hard assurance failure demotes the delegated branch to Shadow / restricted.'},
]

def main():
    rows=[]; log=[]
    for i,d in enumerate(DEMOS,1):
        final,binding=child_authority(d['parent'],d['scope'],d['gates'])
        rows.append({'demo_id':i,'demonstration':d['demo'],'parent_authority':label(d['parent']),'child_scope_cap':label(d['scope']),'final_child_authority':label(final),'binding_constraint':binding,'explanation':d['explanation'],'evidence_class':'SYNTHETIC'})
        steps=['delegation','context_transfer','tool_scope_check','gate_evaluation','authority_decision','independent_witness']
        for n,step in enumerate(steps): log.append({'demo_id':i,'sequence':n+1,'event':step,'parent':label(d['parent']),'child_scope':label(d['scope']),'gate_states':d['gates'],'decision':label(final) if step=='authority_decision' else None,'binding_constraint':binding if step=='authority_decision' else None})
    write_df(pd.DataFrame(rows),ROOT/'results/tables/table_S3_agent_authority_demo.csv')
    p=ROOT/'results/logs/agent_authority_events.jsonl'; p.write_text('\n'.join(json.dumps(x,ensure_ascii=False) for x in log)+'\n',encoding='utf-8')
    return rows
if __name__=='__main__': main()
