#!/usr/bin/env python3
"""Regenerate unrestricted RDFR-CI v1.3.0 supplementary computations."""
from pathlib import Path
import argparse,subprocess,sys,os,json,hashlib,platform,importlib.metadata as im
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];VERSION='1.3.0'
def run(script,*args):
    env=os.environ.copy();env['PYTHONPATH']=str(ROOT/'src')+os.pathsep+env.get('PYTHONPATH','');cmd=[sys.executable,str(ROOT/script),*map(str,args)];print('+',' '.join(cmd));subprocess.check_call(cmd,cwd=ROOT,env=env)
def sha256(p):
    h=hashlib.sha256();h.update(Path(p).read_bytes());return h.hexdigest()
def build_manifest(seed=42):
    outputs=[{'path':str(p.relative_to(ROOT)),'sha256':sha256(p),'bytes':p.stat().st_size} for p in sorted((ROOT/'results').rglob('*')) if p.is_file() and p.name!='reproducibility_manifest.json']
    try: commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True,stderr=subprocess.DEVNULL).strip()
    except Exception: commit='UNCOMMITTED_AT_GENERATION'
    deps={}
    for name in ['numpy','pandas','scipy','scikit-learn','matplotlib','pyyaml','pydantic','pytest']:
        try: deps[name]=im.version(name)
        except im.PackageNotFoundError: deps[name]='not-installed'
    m={'software_version':VERSION,'generated_at_utc':datetime.now(timezone.utc).isoformat(),'git_commit':commit,'python':platform.python_version(),'platform':platform.platform(),'random_seed':seed,'outputs':outputs,'dependencies':deps,'publication_artifact_manifest':'paper/manuscript_artifact_manifest.json'}
    (ROOT/'results/reproducibility_manifest.json').write_text(json.dumps(m,indent=2),encoding='utf-8')
def main(smoke=False):
    n_unc=500 if smoke else 10000;n_weight=500 if smoke else 5000;n_loss=5000 if smoke else 100000
    run('scripts/generate_scenarios.py');run('experiments/generate_static_materials.py');run('experiments/run_scenario_analysis.py','--n',n_unc);run('experiments/run_authority_ceiling.py');run('experiments/run_aggregation_sensitivity.py')
    if not smoke: run('experiments/run_weight_sensitivity.py')
    run('experiments/run_interrater_demo.py');run('experiments/run_agent_authority_demo.py')
    if smoke:
        env=os.environ.copy();env['PYTHONPATH']=str(ROOT/'src')+os.pathsep+env.get('PYTHONPATH','');subprocess.check_call([sys.executable,'-c',f"import sys;sys.path.insert(0,'{ROOT/'experiments'}');from run_weight_sensitivity import main;main(n={n_weight})"],cwd=ROOT,env=env);subprocess.check_call([sys.executable,'-c',f"import sys;sys.path.insert(0,'{ROOT/'experiments'}');from run_loss_model_demo import main;main(n={n_loss})"],cwd=ROOT,env=env)
    else: run('experiments/run_loss_model_demo.py')
    run('experiments/run_detection_threshold_demo.py');build_manifest();run('scripts/verify_results.py','--smoke' if smoke else '--full');build_manifest();print('\nRDFR-CI v1.3.0 REPRODUCTION COMPLETE')
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--smoke',action='store_true');a=ap.parse_args();main(a.smoke)
