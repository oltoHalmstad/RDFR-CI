#!/usr/bin/env python3
"""Verify the v1.3.0 manuscript-alignment invariants available in the public repository."""
from pathlib import Path
import argparse,csv,json,sys,subprocess,os
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from rdfr_ci.authority import AuthorityState,authority_from_score
from rdfr_ci.gates import final_authority
VERSION='1.3.0'
def main(mode='full'):
    checks=[]
    def add(n,v): checks.append((n,bool(v)))
    add('Canonical authority scale',[int(AuthorityState.ROLLBACK_ISOLATION),int(AuthorityState.SHADOW_RESTRICTED),int(AuthorityState.ASSISTED_DEFENSE),int(AuthorityState.HUMAN_APPROVED),int(AuthorityState.BOUNDED_AUTOMATION)]==[0,1,2,3,4])
    PASS={k:'pass' for k in ('G_S','G_V','G_FA','G_A','G_H')}
    add('UNKNOWN AI-assurance cap',final_authority(4,{**PASS,'G_A':'unknown'})[0]==AuthorityState.SHADOW_RESTRICTED);add('Priority stop',final_authority(4,PASS,priority_prohibition=True)[0]==AuthorityState.ROLLBACK_ISOLATION)
    add('Exact manuscript table set',all((ROOT/f'paper/manuscript_tables/table_{x}.csv').exists() for x in list(map(str,range(1,12)))+['B1','C1','C2']))
    t7=ROOT/'results/tables/table_7_generated.csv'
    if t7.exists():
        rows=list(csv.reader(t7.open(encoding='utf-8')));exp=[['Detection threshold','0.510','0.385'],['Global F₁','0.924','0.887'],['False-positive rate','0.000','0.037'],['Criticality-weighted recall','0.714','0.876'],['Detection capability gap D','0.286','0.124'],['Composite score RCI','0.381','0.349'],['Provisional state','Assisted defense','Human-approved intervention']];add('Generated Table 7 values',rows[1:8]==exp)
    s=ROOT/'results/scenario_results/summary_v1.3.json'
    if s.exists():
        j=json.loads(s.read_text());add('30 scenarios / 18 sectors',j.get('scenarios')==30 and j.get('sectors')==18);add('Table 11 policy verification',j.get('manuscript_table_11_policy_verified') is True)
    agg=ROOT/'results/sensitivity/aggregation_summary.json'
    if agg.exists(): add('Aggregation sensitivity 21/30',json.loads(agg.read_text()).get('changed_under_at_least_one')==21)
    env=os.environ.copy();env['PYTHONPATH']=str(ROOT/'src')+os.pathsep+env.get('PYTHONPATH','');t=subprocess.run([sys.executable,'-m','pytest','-q'],cwd=ROOT,env=env,capture_output=True,text=True);add('Unit tests',t.returncode==0)
    lines=['# REPRODUCIBILITY STATUS','',f'Release: v{VERSION}','Manuscript alignment: 9 September 2026','']+[f'{n}: {"PASS" if ok else "FAIL"}' for n,ok in checks]+['',f'Verification mode: {mode}',f'Pytest: {t.stdout.strip() or t.stderr.strip()}','', 'Scientific classification: v1.3.0 verifies the public policy implementation and manuscript-facing numeric tables. Exact publication figure binaries and the aligned DOCX are identified by hashes in the release/Zenodo package; raw SWaT data are excluded and labeled A1/A2 attack validation remains unexecuted.']
    (ROOT/'results/REPRODUCIBILITY_STATUS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8');print('\n'.join(lines));return 1 if any(not ok for _,ok in checks) else 0
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--full',action='store_true');ap.add_argument('--smoke',action='store_true');a=ap.parse_args();raise SystemExit(main('smoke' if a.smoke else 'full'))
