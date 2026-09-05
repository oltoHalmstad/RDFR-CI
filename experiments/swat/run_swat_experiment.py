#!/usr/bin/env python3
"""Execute the pre-specified SWaT A1/A2 external validation on authorized local data."""
from __future__ import annotations
from pathlib import Path
import argparse,csv,json,sys
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'src'))
sys.path.insert(0,str(HERE))
from prepare_swat import discover_csvs,load_swat,chronological_normal_split
from train_isolation_forest import train_isolation_forest,anomaly_scores
from train_autoencoder import train_autoencoder,reconstruction_scores
from threshold_analysis import evaluate_thresholds,select_f1,select_fpr_constrained
from attack_episode_metrics import event_metrics,contiguous_event_ids
from bootstrap_authority import bootstrap_water_authority

MISSING='''Official SWaT data not found.\n\nThe RDFR-CI repository does not redistribute SWaT.\n\nPlease obtain authorized access from iTrust/SUTD and place the required files in:\n\ndata/private/swat/\n\nNo empirical SWaT metrics have been generated.'''


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--data-dir',default=str(ROOT/'data/private/swat'))
    ap.add_argument('--normal-file'); ap.add_argument('--attack-file')
    ap.add_argument('--label-column'); ap.add_argument('--timestamp-column')
    ap.add_argument('--model',choices=['isolation_forest','autoencoder'],default='isolation_forest')
    ap.add_argument('--phi',type=float,default=.05); ap.add_argument('--seed',type=int,default=42)
    ap.add_argument('--bootstrap',type=int,default=10000)
    ap.add_argument('--output-dir',default=str(ROOT/'results/swat'))
    args=ap.parse_args()
    data_dir=Path(args.data_dir)
    if not data_dir.exists() or not any(data_dir.glob('*.csv')):
        print(MISSING,file=sys.stderr); return 2
    try:
        normal=Path(args.normal_file) if args.normal_file else None
        attack=Path(args.attack_file) if args.attack_file else None
        if normal is None or attack is None:
            normal,attack=discover_csvs(data_dir)
        Xn,Xa,yn,ya,features,tcol,attack_df=load_swat(normal,attack,args.label_column,args.timestamp_column)
        Xtrain,Xcal=chronological_normal_split(Xn,.80)
        if args.model=='isolation_forest':
            scaler,model=train_isolation_forest(Xtrain,args.seed)
            ns=anomaly_scores(scaler,model,Xcal); ats=anomaly_scores(scaler,model,Xa)
        else:
            scaler,model=train_autoencoder(Xtrain,args.seed)
            ns=reconstruction_scores(scaler,model,Xcal); ats=reconstruction_scores(scaler,model,Xa)
        rows=evaluate_thresholds(ns,ats,ya)
        f1=select_f1(rows); auth=select_fpr_constrained(rows,args.phi)
        for r in rows:
            r['D']=1-r['recall']; r['R_CI']=.430+.20*r['D']
        pred=(ats>=auth['threshold']).astype(int)
        ev=event_metrics(ya,pred,1.0)
        ids=contiguous_event_ids(ya); detected=[]
        for eid in sorted(set(ids[ids>=0].tolist())):
            idx=np.where(ids==eid)[0]; detected.append(int(pred[idx].any()))
        boot=bootstrap_water_authority(detected,args.bootstrap,args.seed) if detected else None
        out=Path(args.output_dir); out.mkdir(parents=True,exist_ok=True)
        with (out/'threshold_sweep.csv').open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
        summary={'data_files':[normal.name,attack.name],'model':args.model,'feature_count':len(features),
                 'phi':args.phi,'global_f1_point':f1,'authority_point':auth,'event_metrics':ev,'bootstrap':boot,
                 'scientific_scope':'External validation of D(phi) and detector-to-authority propagation only; not full-framework validation.'}
        (out/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
        print(json.dumps(summary,indent=2)); return 0
    except Exception as exc:
        print(f'SWaT experiment failed: {exc}',file=sys.stderr); return 1

if __name__=='__main__':
    raise SystemExit(main())
