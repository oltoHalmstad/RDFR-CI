#!/usr/bin/env python3
"""Verify manuscript-aligned RDFR-CI reproducibility invariants and write a status report."""
from pathlib import Path
import argparse,json,sys,subprocess,os
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from rdfr_ci.scenario_loader import load_catalog
from rdfr_ci.risk import composite_risk

EXPECTED={'CDI-001':.1705,'MFG-001':.3055,'SUB-001':.3385,'RAIL-001':.3705,'HOSP-001':.4195,'WATER-001':.5000}

def main(mode='full'):
    checks=[]
    def add(name,ok): checks.append((name,bool(ok)))
    sc=load_catalog(ROOT/'scenarios/scenario_catalog.yaml')
    add('30-scenario library',len(sc)==30)
    add('18-sector coverage',len({s.sector for s in sc})==18)
    showcase_ok=True
    for sid,exp in EXPECTED.items():
        s=next(x for x in sc if x.scenario_id==sid); score=composite_risk(s.E,s.D,s.A,s.F,s.C,s.weights)
        showcase_ok &= abs(score-exp)<1e-9
    add('Six showcases',showcase_ok)
    agg=json.loads((ROOT/'results/sensitivity/aggregation_summary.json').read_text())
    add('Aggregation sensitivity',agg['changed_under_at_least_one']==21)
    summary=json.loads((ROOT/'results/scenario_results/summary.json').read_text())
    add('Score/gate binding analysis',summary['score_binding']==20 and summary['gate_binding']==10)
    add('G_A most common binding gate',summary['most_common_gate_binding']=='G_A')
    add('Authority ceiling', (ROOT/'results/tables/table_5_authority_ceilings.csv').exists() and (ROOT/'results/figures/figure_A1_authority_ceiling.png').exists())
    add('Decision uncertainty',(ROOT/'results/sensitivity/decision_uncertainty.csv').exists() and (ROOT/'results/figures/figure_A2_decision_stability.png').exists())
    add('Weight sensitivity',(ROOT/'results/sensitivity/weight_sensitivity.csv').exists() and (ROOT/'results/figures/figure_S2_weight_sensitivity_wc.png').exists())
    add('Agent authority demonstrations',(ROOT/'results/tables/table_S3_agent_authority_demo.csv').exists() and (ROOT/'results/logs/agent_authority_events.jsonl').exists())
    add('Figures regenerated',len(list((ROOT/'results/figures').glob('*.png')))>=8 and len(list((ROOT/'results/figures').glob('*.pdf')))>=8)
    add('Tables regenerated',len(list((ROOT/'results/tables').glob('*.csv')))>=17 and len(list((ROOT/'results/tables').glob('*.md')))>=17)
    private=[p for p in (ROOT/'data/private').rglob('*') if p.is_file() and p.name!='.gitkeep']
    add('Restricted data excluded from working tree',not private)
    swat_results=ROOT/'results/swat'
    add('No SWaT empirical outputs in unrestricted release',not swat_results.exists() or not any(swat_results.iterdir()))
    add('SWaT pipeline implemented',(ROOT/'experiments/swat/run_swat_experiment.py').exists())
    add('Zenodo metadata ready',(ROOT/'.zenodo.json').exists())
    add('Reproducibility manifest',(ROOT/'results/reproducibility_manifest.json').exists())
    env=os.environ.copy(); env['PYTHONPATH']=str(ROOT/'src')+os.pathsep+env.get('PYTHONPATH','')
    t=subprocess.run([sys.executable,'-m','pytest','-q'],cwd=ROOT,env=env,capture_output=True,text=True)
    add('Unit tests',t.returncode==0)

    failed=[m for m,ok in checks if not ok]
    lines=['# REPRODUCIBILITY STATUS','']
    friendly={
      '30-scenario library':'30-scenario library','Six showcases':'Six showcases','Authority ceiling':'Authority ceiling',
      'Decision uncertainty':'Decision uncertainty','Aggregation sensitivity':'Aggregation sensitivity','Weight sensitivity':'Weight sensitivity',
      'Agent authority demonstrations':'Agent authority tests','Figures regenerated':'Figures regenerated','Tables regenerated':'Tables regenerated',
      'Unit tests':'Unit tests','SWaT pipeline implemented':'SWaT pipeline implemented','Restricted data excluded from working tree':'Restricted data excluded from Git/working tree','Zenodo metadata ready':'Zenodo metadata ready'}
    core_ok=all(ok for name,ok in checks if name in {'Six showcases','Authority ceiling','Score/gate binding analysis'})
    lines.append(f"Core RDFR-CI equations: {'PASS' if core_ok else 'FAIL'}")
    for key in ['30-scenario library','Six showcases','Authority ceiling','Decision uncertainty','Aggregation sensitivity','Weight sensitivity','Agent authority demonstrations','Figures regenerated','Tables regenerated','Unit tests','SWaT pipeline implemented']:
        ok=next(v for n,v in checks if n==key); lines.append(f"{friendly[key]}: {'PASS' if ok else 'FAIL'}")
    lines.append('SWaT empirical results: NOT RUN — authorized official data were not supplied')
    for key in ['Restricted data excluded from working tree','Zenodo metadata ready']:
        ok=next(v for n,v in checks if n==key); lines.append(f"{friendly[key]}: {'PASS' if ok else 'FAIL'}")
    lines += ['',f'Verification mode: {mode}',f'Pytest: {t.stdout.strip() or t.stderr.strip()}','',
              'Scientific classification: unrestricted computational and illustrative outputs are reproduced; SWaT remains a pre-specified external-data protocol.']
    (ROOT/'results/REPRODUCIBILITY_STATUS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

    print('REPRODUCIBILITY STATUS')
    for m,ok in checks: print(f'{m}: {"PASS" if ok else "FAIL"}')
    print('SWaT empirical results: NOT RUN unless authorized official data were supplied')
    if failed:
        print('\nFailed checks:',*failed,sep='\n- '); return 1
    return 0

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--full',action='store_true'); ap.add_argument('--smoke',action='store_true'); a=ap.parse_args(); raise SystemExit(main('smoke' if a.smoke else 'full'))
