#!/usr/bin/env python3
"""Create the v1.3-normalized view of the existing 30-scenario catalog.

The E/D/A/F/C values are unchanged. Legacy illustrative gate metadata is
normalized by scenario_loader from fail/not_evaluated to UNKNOWN so it is not
misrepresented as a demonstrated prohibition.
"""
from pathlib import Path
import csv,json,sys,yaml
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from rdfr_ci.scenario_loader import load_catalog
from rdfr_ci.risk import composite_risk
from rdfr_ci.authority import authority_from_score,label,boundary_margin
from rdfr_ci.gates import final_authority
SRC=ROOT/'scenarios/scenario_catalog.yaml'

def main():
    scenarios=load_catalog(SRC); records=[]
    for s in scenarios:
        score=composite_risk(s.E,s.D,s.A,s.F,s.C,s.weights); prov=authority_from_score(score)
        final,binding=final_authority(prov,s.gate_states,s.gate_caps)
        x=s.model_dump(); x.update(provisional_authority=label(prov),final_authority=label(final),binding_constraint=binding,boundary_margin=round(boundary_margin(score),6))
        records.append(x)
    assert len(records)==30 and len({r['sector'] for r in records})==18
    payload={'schema_version':'1.3.0','notice':'Illustrative demonstration inputs — not measured sector risk levels. Gate metadata normalized to RDFR-CI v1.3 semantics; E/D/A/F/C unchanged.','scenarios':records}
    (ROOT/'scenarios/scenario_catalog_v1.3.yaml').write_text(yaml.safe_dump(payload,sort_keys=False,allow_unicode=True),encoding='utf-8')
    (ROOT/'scenarios/scenario_catalog_v1.3.json').write_text(json.dumps(payload,indent=2,ensure_ascii=False),encoding='utf-8')
    flat=[]
    for r in records:
        row={k:r[k] for k in ['scenario_id','title','sector','asset_type','attack_description','defensive_action','reversibility','blast_radius','physical_process_effect','E','D','A','F','C','provisional_authority','final_authority','binding_constraint','boundary_margin','evidence_status','illustrative_or_empirical']}
        for k in ('weights','beta_vector','gate_states','gate_caps'): row[k]=json.dumps(r[k],sort_keys=True)
        row['assumptions']=' | '.join(r.get('assumptions',[])); flat.append(row)
    with (ROOT/'scenarios/scenario_catalog_v1.3.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(flat[0]));w.writeheader();w.writerows(flat)
    print(f'Normalized {len(records)} scenarios across {len(set(r["sector"] for r in records))} sectors to v1.3 semantics.')
if __name__=='__main__': main()
