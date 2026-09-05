#!/usr/bin/env python3
"""Regenerate all unrestricted RDFR-CI supplementary results."""
from __future__ import annotations
from pathlib import Path
import argparse,subprocess,sys,os,json,hashlib,platform,importlib.metadata as im
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]

def run(script,*args):
    env=os.environ.copy(); env['PYTHONPATH']=str(ROOT/'src')+os.pathsep+env.get('PYTHONPATH','')
    cmd=[sys.executable,str(ROOT/script),*map(str,args)]
    print('+',' '.join(cmd))
    subprocess.check_call(cmd,cwd=ROOT,env=env)

def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
    return h.hexdigest()

def build_manifest(seed=42):
    outputs=[]
    for p in sorted((ROOT/'results').rglob('*')):
        if p.is_file() and p.name != 'reproducibility_manifest.json':
            outputs.append({'path':str(p.relative_to(ROOT)),'sha256':sha256(p),'bytes':p.stat().st_size})
    try:
        commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True,stderr=subprocess.DEVNULL).strip()
    except Exception:
        commit='UNCOMMITTED_AT_GENERATION'
    deps={}
    for name in ['numpy','pandas','scipy','scikit-learn','matplotlib','pyyaml','pydantic','pytest']:
        try: deps[name]=im.version(name)
        except im.PackageNotFoundError: deps[name]='not-installed'
    manifest={'software_version':'1.0.0','generated_at_utc':datetime.now(timezone.utc).isoformat(),'git_commit':commit,'python':platform.python_version(),'platform':platform.platform(),
              'random_seed':seed,'config_files':[str(p.relative_to(ROOT)) for p in sorted((ROOT/'configs').glob('*.yaml'))],
              'outputs':outputs,'dependencies':deps,
              'note':'Manifest is generated before release tagging; regenerate after the final release commit to record an exact release hash.'}
    (ROOT/'results/reproducibility_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    return manifest

def main(smoke=False):
    n_unc=500 if smoke else 10000
    n_weight=500 if smoke else 5000
    n_loss=5000 if smoke else 100000
    run('scripts/generate_scenarios.py')
    run('experiments/generate_static_materials.py')
    run('experiments/run_scenario_analysis.py','--n',n_unc)
    run('experiments/run_authority_ceiling.py')
    run('experiments/run_aggregation_sensitivity.py')
    # Weight sensitivity uses a smaller inline count in smoke mode.
    if not smoke:
        run('experiments/run_weight_sensitivity.py')
    run('experiments/run_interrater_demo.py')
    run('experiments/run_agent_authority_demo.py')
    if smoke:
        env=os.environ.copy(); env['PYTHONPATH']=str(ROOT/'src')+os.pathsep+env.get('PYTHONPATH','')
        subprocess.check_call([sys.executable,'-c',f"import sys;sys.path.insert(0,'{ROOT/'experiments'}');from run_weight_sensitivity import main;main(n={n_weight})"],cwd=ROOT,env=env)
        subprocess.check_call([sys.executable,'-c',f"import sys;sys.path.insert(0,'{ROOT/'experiments'}');from run_loss_model_demo import main;main(n={n_loss})"],cwd=ROOT,env=env)
    else:
        run('experiments/run_loss_model_demo.py')
    run('experiments/run_detection_threshold_demo.py')
    build_manifest(42)
    run('scripts/verify_results.py','--smoke' if smoke else '--full')
    build_manifest(42)
    print('\nREPRODUCTION COMPLETE')
    print('SWaT was intentionally NOT executed. Use experiments/swat/run_swat_experiment.py only with authorized official data.')

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--smoke',action='store_true'); a=ap.parse_args(); main(a.smoke)
